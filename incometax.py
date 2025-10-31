import streamlit as st
import pandas as pd

st.set_page_config(page_title="NL Netto Inkomen Calculator 2025", layout="wide")
st.title("💶 Nederlandse Netto-Inkomen Calculator 2025")

# -----------------------------
# Hulpfuncties
# -----------------------------
def fmt_euro(amount):
    return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_euro_input(s):
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except:
        return 0.0

def format_input(value):
    """Formatteer automatisch punten bij duizendtallen en komma voor decimalen"""
    try:
        val = float(value.replace(".", "").replace(",", "."))
        return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return value

def algemene_heffingskorting_2025(inkomen, aow):
    grens = 28406
    if not aow:
        max_k = 3068
        afbouw = 0.06337
        nul_bij = 76817
    else:
        max_k = 1536
        afbouw = 0.03170
        nul_bij = 76817
    if inkomen <= grens:
        return max_k
    elif inkomen >= nul_bij:
        return 0
    else:
        return max(0, max_k - afbouw * (inkomen - grens))

def arbeidskorting_2025(arbeidsinkomen):
    if arbeidsinkomen <= 11294:
        return 0.086 * arbeidsinkomen
    elif arbeidsinkomen <= 39422:
        return 971 + 0.31707 * (arbeidsinkomen - 11294)
    elif arbeidsinkomen <= 124283:
        return 4319 - 0.06455 * (arbeidsinkomen - 39422)
    else:
        return 0

def eigenwoningforfait(woz_value: float) -> float:
    w = max(0.0, float(woz_value))
    if w <= 12500:
        return 0.0
    elif w <= 25000:
        return w * 0.0010
    elif w <= 50000:
        return w * 0.0020
    elif w <= 75000:
        return w * 0.0025
    elif w <= 1330000:
        return w * 0.0035
    else:
        base = 1330000 * 0.0035
        extra = (w - 1330000) * 0.0235
        return base + extra

def bereken_box1(ink, aow, ewf, renteaftrek):
    belastbaar = max(0, ink + ewf - renteaftrek)
    if aow:
        if belastbaar <= 38441:
            belasting = belastbaar * 0.1792
        elif belastbaar <= 76817:
            belasting = 38441*0.1792 + (belastbaar-38441)*0.3707
        else:
            belasting = 38441*0.1792 + (76817-38441)*0.3707 + (belastbaar-76817)*0.4950
    else:
        if belastbaar <= 38441:
            belasting = belastbaar * 0.3582
        elif belastbaar <= 76817:
            belasting = 38441*0.3582 + (belastbaar-38441)*0.3707
        else:
            belasting = 38441*0.3582 + (76817-38441)*0.3707 + (belastbaar-76817)*0.4950
    ahk = algemene_heffingskorting_2025(ink, aow)
    ak = arbeidskorting_2025(ink)
    heffingskortingen = min(belasting, ahk + ak)
    netto = ink - belasting + heffingskortingen
    return {
        "belastbaar": round(belastbaar,2),
        "belasting": round(belasting,2),
        "algemene_korting": round(ahk,2),
        "arbeids_korting": round(ak,2),
        "kortingen_totaal": round(heffingskortingen,2),
        "netto": round(netto,2)
    }

def bereken_box2(ink: float) -> dict:
    grens = 67804.0
    laag_tarief = 0.245
    hoog_tarief = 0.31
    if ink <= grens:
        belasting = ink * laag_tarief
    else:
        belasting = grens * laag_tarief + (ink - grens) * hoog_tarief
    netto = ink - belasting
    return {
        "inkomen_box2": round(ink,2),
        "belasting_box2": round(belasting,2),
        "netto_box2": round(netto,2)
    }

def bereken_box3(spaar, beleg, schuld, vrijstelling=57684.0):
    belastbaar = max(0, (spaar + beleg - schuld) - vrijstelling)
    rend_spaar = spaar * 0.0144
    rend_beleg = beleg * 0.0588
    rend_schuld = schuld * 0.0262
    totaal_rend = max(0, rend_spaar + rend_beleg - rend_schuld)
    belasting = totaal_rend * 0.36
    netto = (spaar + beleg - schuld) - belasting
    return {
        "vermogen": round(spaar + beleg - schuld,2),
        "belasting_spaar": round(rend_spaar*0.36,2),
        "belasting_beleg": round(rend_beleg*0.36,2),
        "belasting_schuld": round(rend_schuld*0.36,2),
        "belasting_box3": round(belasting,2),
        "netto_box3": round(netto,2)
    }

# -----------------------------
# Session state
# -----------------------------
if "jij_ink" not in st.session_state:
    st.session_state.jij_ink = 0.0
if "partner_ink" not in st.session_state:
    st.session_state.partner_ink = 0.0

# -----------------------------
# Sidebar: Rekenhulp
# -----------------------------
st.sidebar.header("💡 Rekenhulp Bruto → Jaarinkomen")

if "maandloon_raw" not in st.session_state:
    st.session_state.maandloon_raw = "0,00"

maandloon_raw = st.sidebar.text_input("Bruto maandsalaris (€)", st.session_state.maandloon_raw)
formatted_maandloon = format_input(maandloon_raw)
if formatted_maandloon != maandloon_raw:
    st.session_state.maandloon_raw = formatted_maandloon
    st.experimental_rerun()

maandloon = float(formatted_maandloon.replace(".", "").replace(",", "."))
vakantiegeld_pct = st.sidebar.number_input("Vakantiegeld (%)", 8.0, step=1.0)
dertiemaand = st.sidebar.checkbox("13e maand?", True)

vakantiegeld = maandloon * (vakantiegeld_pct/100)
jaarinkomen = maandloon*12 + vakantiegeld + (maandloon if dertiemaand else 0.0)
st.sidebar.markdown(f"**Bruto jaarinkomen**: {fmt_euro(jaarinkomen)}")

if st.sidebar.button("Gebruik voor jezelf"):
    st.session_state.jij_ink = jaarinkomen
if st.sidebar.button("Gebruik voor je partner"):
    st.session_state.partner_ink = jaarinkomen

# -----------------------------
# Hoofdmodel Inputs
# -----------------------------
st.sidebar.header("Persoonlijke gegevens")
jij_aow = st.sidebar.checkbox("AOW bereikt - Jij?", False)
partner_checkbox = st.sidebar.checkbox("Partner aanwezig?", False)
partner_aow = st.sidebar.checkbox("AOW bereikt - Partner?", False) if partner_checkbox else False

st.sidebar.header("Eigen woning")
woz_value = parse_euro_input(st.sidebar.text_input("WOZ-waarde (€)", "0,00"))
hypotheek_rente = parse_euro_input(st.sidebar.text_input("Betaalde hypotheekrente (€)", "0,00"))

st.sidebar.header("Box 2 & 3")
bezit_ab = st.sidebar.checkbox("Bezit je ≥5% aandelen (Box 2)?")
box2_jij = parse_euro_input(st.sidebar.text_input("Box 2 inkomen - Jij (€)", "0,00")) if bezit_ab else 0.0
box2_partner = parse_euro_input(st.sidebar.text_input("Box 2 inkomen - Partner (€)", "0,00")) if (bezit_ab and partner_checkbox) else 0.0

bezittingen = st.sidebar.checkbox("Bezit je vermogen (Box 3)?")
spaar_jij = parse_euro_input(st.sidebar.text_input("Spaargeld - Jij (€)", "0,00")) if bezittingen else 0.0
beleg_jij = parse_euro_input(st.sidebar.text_input("Beleggingen - Jij (€)", "0,00")) if bezittingen else 0.0
schuld_jij = parse_euro_input(st.sidebar.text_input("Schulden - Jij (€)", "0,00")) if bezittingen else 0.0

spaar_partner = parse_euro_input(st.sidebar.text_input("Spaargeld - Partner (€)", "0,00")) if (bezittingen and partner_checkbox) else 0.0
beleg_partner = parse_euro_input(st.sidebar.text_input("Beleggingen - Partner (€)", "0,00")) if (bezittingen and partner_checkbox) else 0.0
schuld_partner = parse_euro_input(st.sidebar.text_input("Schulden - Partner (€)", "0,00")) if (bezittingen and partner_checkbox) else 0.0

# -----------------------------
# Berekeningen
# -----------------------------
ewf = eigenwoningforfait(woz_value)
aftrek = max(0, hypotheek_rente - ewf)

jij_res = bereken_box1(st.session_state.jij_ink, jij_aow, ewf/2 if partner_checkbox else ewf, aftrek/2 if partner_checkbox else aftrek)
partner_res = bereken_box1(st.session_state.partner_ink, partner_aow, ewf/2 if partner_checkbox else 0, aftrek/2 if partner_checkbox else 0)

box2_jij_res = bereken_box2(box2_jij)
box2_partner_res = bereken_box2(box2_partner) if partner_checkbox else {"netto_box2":0.0}

box3_jij_res = bereken_box3(spaar_jij, beleg_jij, schuld_jij)
box3_partner_res = bereken_box3(spaar_partner, beleg_partner, schuld_partner) if partner_checkbox else {"netto_box3":0.0}

totaal_netto = (
    jij_res["netto"] + partner_res["netto"] +
    box2_jij_res["netto_box2"] + box2_partner_res["netto_box2"] +
    box3_jij_res["netto_box3"] + box3_partner_res["netto_box3"]
)

# -----------------------------
# Output & Grafieken
# -----------------------------
st.success(f"📌 **Gezamenlijk netto-inkomen per jaar**: {fmt_euro(totaal_netto)}")

with st.expander("📊 Toon berekening & details"):
    st.subheader("Jij")
    st.write({k: fmt_euro(v) for k,v in jij_res.items()})
    if bezit_ab: st.subheader("Box 2 - Jij"); st.write({k: fmt_euro(v) for k,v in box2_jij_res.items()})
    if bezittingen:
        st.subheader("Box 3 - Jij")
        st.write({
            "Spaargeld belasting": fmt_euro(box3_jij_res["belasting_spaar"]),
            "Beleggingen belasting": fmt_euro(box3_jij_res["belasting_beleg"]),
            "Schulden voordeel": fmt_euro(box3_jij_res["belasting_schuld"]),
            "Totaal Box3": fmt_euro(box3_jij_res["netto_box3"])
        })
    if partner_checkbox:
        st.subheader("Partner")
        st.write({k: fmt_euro(v) for k,v in partner_res.items()})
        if bezit_ab: st.subheader("Box 2 - Partner"); st.write({k: fmt_euro(v) for k,v in box2_partner_res.items()})
        if bezittingen:
            st.subheader("Box 3 - Partner")
            st.write({
                "Spaargeld belasting": fmt_euro(box3_partner_res["belasting_spaar"]),
                "Beleggingen belasting": fmt_euro(box3_partner_res["belasting_beleg"]),
                "Schulden voordeel": fmt_euro(box3_partner_res["belasting_schuld"]),
                "Totaal Box3": fmt_euro(box3_partner_res["netto_box3"])
            })

# Grafieken
st.markdown("### 📊 Bruto → Netto per maand (Box 1) & Box 3 heffing per bestanddeel")
maanden = [f"Maand {i}" for i in range(1,13)]
bruto_maand = [st.session_state.jij_ink/12]*12
netto_maand = [jij_res["netto"]/12]*12
col1, col2 = st.columns(2)
with col1:
    st.subheader("Box 1: Bruto → Netto per maand")
    df_box1 = pd.DataFrame({"Maand": maanden, "Bruto": bruto_maand, "Netto": netto_maand}).set_index("Maand")
    st.bar_chart(df_box1)
with col2:
    st.subheader("Box 3: Heffing per bestanddeel")
    box3_components = pd.DataFrame({
        "Component": ["Spaargeld", "Beleggingen", "Schulden"],
        "Belasting": [
            box3_jij_res["belasting_spaar"],
            box3_jij_res["belasting_beleg"],
            box3_jij_res["belasting_schuld"]
        ]
    })
    st.bar_chart(box3_components.set_index("Component"))
