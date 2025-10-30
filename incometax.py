# app.py
import streamlit as st
import pandas as pd
from math import isclose

# --------------------------
# Functie voor EU-notatie getallen
# --------------------------
def euro(n):
    return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --------------------------
# Parameters 2025
# --------------------------
HILLEN_PERCENT_2025 = 0.7667   # 76,67% Hillen aftrek-deel
MAX_DEDUCTION_RATE_2025 = 0.3748  # max belastingvoordeel hypotheekrenteaftrek
EWF_RATE_DEFAULT = 0.0035

# --------------------------
# Box 1 schijven (belasting+premies)
# --------------------------
def calc_box1_tax(ink):
    x = max(0.0, float(ink))
    b1, b2 = 38441.0, 76817.0
    tax = 0.0
    if x <= b1:
        return x * 0.1792
    tax += b1 * 0.1792
    if x <= b2:
        return tax + (x - b1) * 0.3748
    tax += (b2 - b1) * 0.3748
    tax += (x - b2) * 0.495
    return tax

# --------------------------
# Eigenwoningforfait tabel 2025
# --------------------------
def calc_eigenwoningforfait(woz):
    w = max(0.0, woz)
    if w <= 12500: return 0.0
    if w <= 25000: return w * 0.0010
    if w <= 50000: return w * 0.0020
    if w <= 75000: return w * 0.0025
    if w <= 1_330_000: return w * 0.0035
    return 4655 + (w - 1_330_000) * 0.0235

# --------------------------
# Hypotheekrente eerste jaar
# --------------------------
def annual_interest_paid(principal, rate, years=30, mort_type="Annuiteit"):
    P = float(principal)
    r = float(rate) / 100.0
    maanden = years * 12
    if P <= 0 or r <= 0: return 0.0

    if mort_type == "Aflossingsvrij":
        return P * r

    mr = r / 12.0

    if mort_type == "Lineair":
        maandelijks_aflossing = P / maanden
        schuld = P
        totaal = 0.0
        for _ in range(12):
            rente = schuld * mr
            totaal += rente
            schuld -= maandelijks_aflossing
        return totaal

    # Annuiteit
    maandlast = mr * P / (1 - (1 + mr)**(-maanden))
    schuld = P
    totaal = 0.0
    for _ in range(12):
        rente = schuld * mr
        aflossing = maandlast - rente
        totaal += rente
        schuld -= aflossing
    return totaal

# --------------------------
# Heffingskortingen
# --------------------------
def algemene_heffingskorting(ink):
    maxc = 3070.0
    if ink <= 73000: return maxc
    return max(0.0, maxc - 0.056 * (ink - 73000))

def arbeidskorting(ink):
    if ink <= 11000: return 0.0
    if ink <= 36000: return 1000 + 0.215 * (ink - 11000)
    if ink <= 112000: return max(0, 5000 - 0.061 * (ink - 36000))
    return 0.0

# --------------------------
# Box 3 belastingmodel 2025
# --------------------------
def box3_tax(a, d, partner):
    vrij = 57684 * (2 if partner else 1)
    bel = max(0.0, a - d - vrij)
    t1, t2 = 103000, 1_030_000
    r1, r2, r3 = 0.01818, 0.04366, 0.0553
    if bel <= 0: rendement = 0
    elif bel <= t1: rendement = bel * r1
    elif bel <= t2: rendement = t1*r1 + (bel - t1)*r2
    else: rendement = t1*r1 + (t2-t1)*r2 + (bel - t2)*r3
    return rendement * 0.36

# --------------------------
# UI
# --------------------------
st.set_page_config(page_title="Belastingcalculator NL 2025", layout="wide")
st.title("🇳🇱 Nederlandse Belasting- en Hypotheekcalculator (2025)")

st.subheader("Inkomen en werk")
bruto = st.number_input("Bruto jaarinkomen (Box 1) €", min_value=0.0, step=100.0, value=50000.0)

st.subheader("Eigen woning & hypotheek")
woz = st.number_input("WOZ-waarde woning €", min_value=0.0, step=1000.0, value=400000.0)
hp = st.number_input("Hypotheekschuld €", min_value=0.0, step=1000.0, value=300000.0)
rente = st.number_input("Hypotheekrente (%)", min_value=0.0, max_value=20.0, step=0.01, value=4.00)
htype = st.selectbox("Hypotheekvorm", ["Annuiteit", "Lineair", "Aflossingsvrij"])
term = st.number_input("Resterende looptijd (jaren)", min_value=1, step=1, value=30)

st.subheader("Andere boxen")
box2 = st.number_input("Box 2-inkomen €", min_value=0.0, step=100.0, value=0.0)
vermogen = st.number_input("Vermogen Box 3 €", min_value=0.0, step=100.0, value=100000.0)
schulden = st.number_input("Schulden Box 3 €", min_value=0.0, step=100.0, value=20000.0)
partner = st.checkbox("Fiscaal partner")

# --------------------------
# Berekening
# --------------------------
if st.button("Bereken"):
    ewf = calc_eigenwoningforfait(woz)
    renteaftrek = annual_interest_paid(hp, rente, term, htype)
    verschil = ewf - renteaftrek

    if verschil > 0:  # Hillen
        netto_woning = verschil * (1 - HILLEN_PERCENT_2025)
        hillen_bedrag = verschil * HILLEN_PERCENT_2025
    else:
        netto_woning = verschil
        hillen_bedrag = 0

    belastbaar1 = max(0.0, bruto + netto_woning)
    belastbaar1_zonder = max(0.0, bruto + ewf)

    tax_zonder = calc_box1_tax(belastbaar1_zonder)
    tax_met = calc_box1_tax(belastbaar1)

    cred_z = algemene_heffingskorting(belastbaar1_zonder) + arbeidskorting(belastbaar1_zonder)
    cred_m = algemene_heffingskorting(belastbaar1) + arbeidskorting(belastbaar1)

    tax_zonder -= cred_z
    tax_met -= cred_m

    voordeel_raw = tax_zonder - tax_met
    max_voordeel = renteaftrek * MAX_DEDUCTION_RATE_2025

    if voordeel_raw > max_voordeel:
        voordeel = max_voordeel
        tax_box1 = max(0, tax_zonder - max_voordeel)
        cap = True
    else:
        voordeel = voordeel_raw
        tax_box1 = tax_met
        cap = False

    # Box 2 en 3
    tax2 = box2 * (0.245 if box2 <= 67804 else 0.31)
    tax3 = box3_tax(vermogen, schulden, partner)

    totaal_bel = tax_box1 + tax2 + tax3
    netto = (bruto + box2) - (tax_box1 + tax2)
    eff = totaal_bel / (bruto + box2) if (bruto + box2) > 0 else 0

    # --------------------------
    # Output
    # --------------------------
    st.header("Resultaten")
    st.write(f"Eigenwoningforfait: **€{euro(ewf)}**")
    st.write(f"Betaalde hypotheekrente (1e jaar): **€{euro(renteaftrek)}**")

    if verschil > 0:
        st.write(f"🏠 Hillenregeling actief — beschermd deel: **€{euro(hillen_bedrag)}**")
    st.write(f"Netto bijtelling/aftrek woning: **€{euro(netto_woning)}**")

    st.write(f"Belastbaar inkomen Box 1: **€{euro(belastbaar1)}**")
    st.write(f"Belasting Box 1: **€{euro(tax_box1)}**")

    st.write(f"Belasting Box 2: **€{euro(tax2)}**")
    st.write(f"Belasting Box 3: **€{euro(tax3)}**")

    st.subheader("Hypotheekaftrek voordeel")
    st.write(f"Ruw voordeel: **€{euro(voordeel_raw)}**")
    st.write(f"Maximaal toegestaan (tariefaanpassing): **€{euro(max_voordeel)}**")
    st.write(f"Cap toegepast: **{'Ja' if cap else 'Nee'}**")
    st.write(f"Definitief voordeel: **€{euro(voordeel)}**")

    st.subheader("Netto resultaat")
    st.write(f"Totale belasting: **€{euro(totaal_bel)}**")
    st.write(f"Netto inkomen (Box1+Box2): **€{euro(netto)}**")
    st.write(f"Effectieve belastingdruk: **{eff*100:.2f}%**")

    # Charts
    st.write("### Belastingverdeling per Box")
    df = pd.DataFrame({
        "Box": ["Box 1", "Box 2", "Box 3"],
        "Belasting (€)": [tax_box1, tax2, tax3]
    }).set_index("Box")
    st.bar_chart(df)

    st.write("### Proportionele verdeling")
    df2 = pd.DataFrame([[tax_box1, tax2, tax3]], columns=["Box 1", "Box 2", "Box 3"])
    st.bar_chart(df2)

    st.caption("Model gebaseerd op Nederlandse regels 2025. Indicatief, geen fiscaal advies.")
