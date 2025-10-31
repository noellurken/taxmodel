import streamlit as st
import pandas as pd

st.set_page_config(page_title="NL Netto Inkomen Calculator 2025", layout="wide")
st.title("💶 Nederlandse Netto-Inkomen Calculator 2025")

# -----------------------------
# Formatter / Parser
# -----------------------------
def fmt_euro(val):
    return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_euro_input(s):
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except:
        return 0.0

# -----------------------------
# Heffingskortingen en Box1
# -----------------------------
def algemene_heffingskorting_2025(ink, aow):
    grens = 28406
    if not aow:
        max_k = 3068
        afbouw = 0.06337
        nul_bij = 76817
    else:
        max_k = 1536
        afbouw = 0.03170
        nul_bij = 76817
    if ink <= grens:
        return max_k
    elif ink >= nul_bij:
        return 0
    else:
        return max(0, max_k - afbouw * (ink - grens))

def arbeidskorting_2025(ink):
    if ink <= 11294:
        return 0.086 * ink
    elif ink <= 39422:
        return 971 + 0.31707 * (ink - 11294)
    elif ink <= 124283:
        return 4319 - 0.06455 * (ink - 39422)
    else:
        return 0

def eigenwoningforfait(woz):
    w = max(0.0, float(woz))
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
        "Belastbaar": round(belastbaar,2),
        "Belasting": round(belasting,2),
        "Algemene heffingskorting": round(ahk,2),
        "Arbeidskorting": round(ak,2),
        "Kortingen totaal": round(heffingskortingen,2),
        "Netto": round(netto,2)
    }

# Box2
def bereken_box2(ink):
    grens = 67804.0
    laag = 0.245
    hoog = 0.31
    if ink <= grens:
        belasting = ink * laag
    else:
        belasting = grens*laag + (ink-grens)*hoog
    netto = ink - belasting
    return {"Inkomen": round(ink,2), "Belasting": round(belasting,2), "Netto": round(netto,2)}

# Box3
def bereken_box3(spaar, beleg, schuld, vrijstelling=57684.0):
    belastbaar = max(0,(spaar + beleg - schuld)-vrijstelling)
    rend_spaar = spaar * 0.0144
    rend_beleg = beleg * 0.0588
    rend_schuld = schuld * 0.0262
    totaal = max(0,rend_spaar + rend_beleg - rend_schuld)
    belasting = totaal*0.36
    netto = spaar + beleg - schuld - belasting
    return {
        "Vermogen": round(spaar+beleg-schuld,2),
        "Belasting spaargeld": round(rend_spaar*0.36,2),
        "Belasting beleggingen": round(rend_beleg*0.36,2),
        "Belasting schulden": round(rend_schuld*0.36,2),
        "Belasting totaal": round(belasting,2),
        "Netto": round(netto,2)
    }

# -----------------------------
# Session State
# -----------------------------
for key in ["jij_ink","partner_ink","maandloon_raw","maandloon_float","partner_checkbox","aow_jij","aow_partner"]:
    if key not in st.session_state:
        st.session_state[key] = 0.0 if "ink" in key or "float" in key else False

# -----------------------------
# Sidebar: Rekenhulp
# -----------------------------
st.sidebar.header("💡 Rekenhulp Bruto → Jaarinkomen")
maandloon_input = st.sidebar.text_input("Bruto maandsalaris (€)", st.session_state.maandloon_raw)
vakantiegeld_pct = st.sidebar.number_input("Vakantiegeld (%)", value=8.0, step=1.0)
dertiemaand = st.sidebar.checkbox("13e maand aanwezig?", True)

if st.sidebar.button("Format toepassen"):
    maandloon_val = parse_euro_input(maandloon_input)
    jaarinkomen = maandloon_val * (13 if dertiemaand else 12)
    jaarinkomen += jaarinkomen * (vakantiegeld_pct/100)
    st.session_state.maandloon_float = maandloon_val
    st.session_state.maandloon_raw = fmt_euro(maandloon_val)
    st.session_state['jaarinkomen'] = jaarinkomen

st.sidebar.markdown(f"**Bruto jaarinkomen incl. vakantiegeld**: {fmt_euro(st.session_state.get('jaarinkomen',0))}")

if st.sidebar.button("Gebruik voor jezelf"):
    st.session_state.jij_ink = st.session_state.get('jaarinkomen',0)
if st.sidebar.button("Gebruik voor je partner"):
    st.session_state.partner_ink = st.session_state.get('jaarinkomen',0)

# -----------------------------
# Hoofdmodel Layout
# -----------------------------
st.header("📊 Netto-Inkomen Berekening")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Jij")
    st.write("Bruto jaarinkomen:", fmt_euro(st.session_state.get('jij_ink',0)))
    woz = st.number_input("WOZ-waarde eigen woning (€)", value=0.0)
    hypotheek = st.number_input("Renteaftrek (€)", value=0.0)
    box1 = bereken_box1(st.session_state.get('jij_ink',0), st.session_state.aow_jij, eigenwoningforfait(woz), hypotheek)
    st.write({k: fmt_euro(v) for k,v in box1.items()})

    st.number_input("Spaargeld (€)", value=0.0)
    st.number_input("Beleggingen (€)", value=0.0)
    st.number_input("Schulden (€)", value=0.0)
    box3 = bereken_box3(0,0,0)
    st.write({k: fmt_euro(v) for k,v in box3.items()})

with col2:
    st.subheader("Partner")
    st.checkbox("Partner aanwezig?", key="partner_checkbox")
    if st.session_state.partner_checkbox:
        st.write("Bruto jaarinkomen:", fmt_euro(st.session_state.get('partner_ink',0)))
        woz_p = st.number_input("WOZ-waarde partner (€)", value=0.0)
        hypotheek_p = st.number_input("Renteaftrek partner (€)", value=0.0)
        box1_p = bereken_box1(st.session_state.get('partner_ink',0), st.session_state.aow_partner, eigenwoningforfait(woz_p), hypotheek_p)
        st.write({k: fmt_euro(v) for k,v in box1_p.items()})

        st.number_input("Spaargeld partner (€)", value=0.0)
        st.number_input("Beleggingen partner (€)", value=0.0)
        st.number_input("Schulden partner (€)", value=0.0)
        box3_p = bereken_box3(0,0,0)
        st.write({k: fmt_euro(v) for k,v in box3_p.items()})
