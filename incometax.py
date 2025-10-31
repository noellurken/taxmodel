import streamlit as st
import pandas as pd

# -----------------------------
# Pagina instellingen
# -----------------------------
st.set_page_config(page_title="NL Netto Inkomen Calculator 2025", layout="wide")
st.title("💶 Nederlandse Netto-Inkomen Calculator 2025")

# -----------------------------
# Hulpfuncties
# -----------------------------
def fmt_euro(val):
    """Formatteer float naar string met punten voor duizendtallen en komma voor decimalen."""
    return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_euro_input(s):
    """Parse string naar float."""
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except:
        return 0.0

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
# Session state initialisatie
# -----------------------------
for key in ["jij_ink","partner_ink","maandloon_raw","maandloon_float"]:
    if key not in st.session_state:
        st.session_state[key] = 0.0 if "ink" in key or "float" in key else "0,00"

# -----------------------------
# Sidebar: Rekenhulp
# -----------------------------
st.sidebar.header("💡 Rekenhulp Bruto → Jaarinkomen")
maandloon_input = st.sidebar.text_input("Bruto maandsalaris (€)", st.session_state.maandloon_raw)
vakantiegeld_pct = st.sidebar.number_input("Vakantiegeld (%)", value=8.0, step=1.0)
dertiemaand = st.sidebar.checkbox("13e maand aanwezig?", True)

if st.sidebar.button("Toepassen / Format"):
    maandloon_val = parse_euro_input(maandloon_input)
    st.session_state.maandloon_float = maandloon_val
    st.session_state.maandloon_raw = fmt_euro(maandloon_val)

maandloon = st.session_state.maandloon_float
maandloon_effectief = maandloon * (13 if dertiemaand else 12)
vakantiegeld = maandloon_effectief * (vakantiegeld_pct / 100)
jaarinkomen = maandloon_effectief + vakantiegeld

st.sidebar.markdown(f"**Bruto jaarinkomen incl. vakantiegeld**: {fmt_euro(jaarinkomen)}")

if st.sidebar.button("Gebruik voor jezelf"):
    st.session_state.jij_ink = jaarinkomen
if st.sidebar.button("Gebruik voor je partner"):
    st.session_state.partner_ink = jaarinkomen

st.write("✅ Geformatteerde invoer:", st.session_state.maandloon_raw)
st.write("✅ Bruto jaarinkomen inclusief vakantiegeld:", fmt_euro(jaarinkomen))

# -----------------------------
# Hier kun je verder de hoofdapp integreren
# Box1-3, partner, woning, hypotheek, grafieken enz.
# -----------------------------
