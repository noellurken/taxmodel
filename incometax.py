# app.py
import streamlit as st
import pandas as pd

# --------------------------
# Helper functions
# --------------------------
def euro_format(n):
    """Format float as Dutch euro: 50.000,00"""
    return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_euro_input(text):
    """Parse Dutch-style euro input to float."""
    text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except:
        return 0.0

# --------------------------
# Parameters 2025
# --------------------------
HILLEN_PERCENT_2025 = 0.7667
MAX_DEDUCTION_RATE_2025 = 0.3748

# --------------------------
# Box1 belasting
# --------------------------
def calc_box1_tax(ink):
    x = max(0.0, float(ink))
    b1, b2 = 38441.0, 76817.0
    tax = 0.0
    if x <= b1:
        return x * 0,3582
    tax += b1 * 0,3582
    if x <= b2:
        return tax + (x - b1) * 0.3748
    tax += (b2 - b1) * 0.3748
    tax += (x - b2) * 0.495
    return tax

# --------------------------
# Eigenwoningforfait
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
# Box3 belasting
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
# Initialize session state for formatted inputs
# --------------------------
inputs = {
    "bruto": "50.000,00",
    "woz": "400.000,00",
    "hp": "300.000,00",
    "rente": "4,00",
    "term": "30",
    "box2": "0",
    "vermogen": "100.000",
    "schulden": "20.000"
}

for key in inputs:
    if key not in st.session_state:
        st.session_state[key] = inputs[key]

# Helper for auto-formatting
def auto_format(key):
    val = parse_euro_input(st.session_state[key])
    st.session_state[key] = euro_format(val)

# --------------------------
# UI
# --------------------------
st.set_page_config(page_title="Belastingcalculator 2025", layout="centered")
st.title("Belastingcalculator 2025")

st.subheader("Inkomen en werk")
st.text_input("Brutojaarinkomen (Box 1) €", key="bruto", on_change=auto_format, args=("bruto",))
bruto = parse_euro_input(st.session_state.bruto)

st.subheader("Eigen woning & hypotheek")
st.text_input("WOZ-waarde eigen woning €", key="woz", on_change=auto_format, args=("woz",))
woz = parse_euro_input(st.session_state.woz)

st.text_input("Hypotheekschuld €", key="hp", on_change=auto_format, args=("hp",))
hp = parse_euro_input(st.session_state.hp)

st.text_input("Hypotheekrente (%)", key="rente", on_change=auto_format, args=("rente",))
rente = parse_euro_input(st.session_state.rente)

htype = st.selectbox("Hypotheekvorm", ["Annuiteit", "Lineair", "Aflossingsvrij"])

st.text_input("Resterende looptijd (jaren)", key="term", on_change=auto_format, args=("term",))
term = int(parse_euro_input(st.session_state.term))

st.subheader("Box 2 en box 3")
st.text_input("Box 2-inkomen €", key="box2", on_change=auto_format, args=("box2",))
box2 = parse_euro_input(st.session_state.box2)

st.text_input("Vermogen Box 3 €", key="vermogen", on_change=auto_format, args=("vermogen",))
vermogen = parse_euro_input(st.session_state.vermogen)

st.text_input("Schulden Box 3 €", key="schulden", on_change=auto_format, args=("schulden",))
schulden = parse_euro_input(st.session_state.schulden)

partner = st.checkbox("Fiscaal partner")

# --------------------------
# Berekening
# --------------------------
if st.button("Bereken"):
    ewf = calc_eigenwoningforfait(woz)
    renteaftrek = annual_interest_paid(hp, rente, term, htype)
    verschil = ewf - renteaftrek

    if verschil > 0:
        netto_woning = verschil * (1 - HILLEN_PERCENT_2025)
        hillen_bedrag = verschil * HILLEN_PERCENT_2025
    else:
        netto_woning = verschil
        hillen_bedrag = 0

    belastbaar1 = max(0.0, bruto + netto_woning)
    belastbaar1_zonder = max(0.0, bruto + ewf)

    tax_zonder = calc_box1_tax(belastbaar1_zonder) - (algemene_heffingskorting(belastbaar1_zonder) + arbeidskorting(belastbaar1_zonder))
    tax_met = calc_box1_tax(belastbaar1) - (algemene_heffingskorting(belastbaar1) + arbeidskorting(belastbaar1))

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

    tax2 = box2 * (0.245 if box2 <= 67804 else 0.31)
    tax3 = box3_tax(vermogen, schulden, partner)

    totaal_bel = tax_box1 + tax2 + tax3
    netto = (bruto + box2) - (tax_box1 + tax2)
    eff = totaal_bel / (bruto + box2) if (bruto + box2) > 0 else 0

    # --------------------------
    # Output
    # --------------------------
    st.header("Resultaten")
    st.write(f"Eigenwoningforfait: **€{euro_format(ewf)}**")
    st.write(f"Betaalde hypotheekrente (1e jaar): **€{euro_format(renteaftrek)}**")
    if verschil > 0:
        st.write(f"🏠 Hillenregeling actief — beschermd deel: **€{euro_format(hillen_bedrag)}**")
    st.write(f"Netto bijtelling/aftrek woning: **€{euro_format(netto_woning)}**")
    st.write(f"Belastbaar inkomen Box 1: **€{euro_format(belastbaar1)}**")
    st.write(f"Belasting Box 1: **€{euro_format(tax_box1)}**")
    st.write(f"Belasting Box 2: **€{euro_format(tax2)}**")
    st.write(f"Belasting Box 3: **€{euro_format(tax3)}**")
    st.subheader("Hypotheekaftrek voordeel")
    st.write(f"Ruw voordeel: **€{euro_format(voordeel_raw)}**")
    st.write(f"Maximaal toegestaan: **€{euro_format(max_voordeel)}**")
    st.write(f"Cap toegepast: **{'Ja' if cap else 'Nee'}**")
    st.write(f"Definitief voordeel: **€{euro_format(voordeel)}**")
    st.subheader("Netto resultaat")
    st.write(f"Totale belasting: **€{euro_format(totaal_bel)}**")
    st.write(f"Netto inkomen (Box1+Box2): **€{euro_format(netto)}**")
    st.write(f"Effectieve belastingdruk: **{eff*100:.2f}%**")

    # Charts
    st.write("### Belastingverdeling per Box")
    df = pd.DataFrame({
        "Box": ["Box 1", "Box 2", "Box 3"],
        "Belasting (€)": [tax_box1, tax2, tax3]
    }).set_index("Box")
    st.bar_chart(df)
