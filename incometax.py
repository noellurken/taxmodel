import streamlit as st

# -----------------------------
# Pagina configuratie
# -----------------------------
st.set_page_config(page_title="NL Netto Inkomen Calculator 2025", layout="wide")
st.title("💶 Nederlandse Netto-Inkomen Calculator 2025")
st.caption("Inclusief hypotheekrenteaftrek, eigenwoningforfait staffel en heffingskortingen 2025")

# -----------------------------
# Functies
# -----------------------------
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
    if w <= 12_500:
        return 0.0
    elif w <= 25_000:
        return w * 0.0010
    elif w <= 50_000:
        return w * 0.0020
    elif w <= 75_000:
        return w * 0.0025
    elif w <= 1_330_000:
        return w * 0.0035
    else:
        base = 1_330_000 * 0.0035
        extra = (w - 1_330_000) * 0.0235
        return base + extra

def bereken_box1(ink, aow, ewf, renteaftrek):
    tarief = 0.3687 if not aow else 0.1907
    raw = ewf - renteaftrek
    if raw > 0:
        hillen_afbouw = raw * 0.76667
        belastbaar_ewf = renteaftrek + hillen_afbouw
    else:
        belastbaar_ewf = ewf

    belastbaar = max(0, ink + belastbaar_ewf - renteaftrek)
    belasting = belastbaar * tarief
    ahk = algemene_heffingskorting_2025(ink, aow)
    ak = arbeidskorting_2025(ink)
    heffingskortingen = min(belasting, ahk + ak)
    netto = ink - belasting + heffingskortingen
    return {
        "belastbaar": round(belastbaar,0),
        "belasting": round(belasting,0),
        "algemene_korting": round(ahk,0),
        "arbeids_korting": round(ak,0),
        "kortingen_totaal": round(heffingskortingen,0),
        "netto": round(netto,0)
    }

# -----------------------------
# UI: layout columns
# -----------------------------
left, right = st.columns([2,1])

# -------------- Rechterkant: Salaris rekenhulp --------------
with right:
    st.markdown("### 🧮 Salaris rekenhulp")
    
    # Bruto maandsalaris met punten als duizendtallen
    maandloon_str = st.text_input("Bruto maandsalaris (€)", value="0")
    try:
        maandloon = float(maandloon_str.replace(".", "").replace(",", ""))
    except:
        maandloon = 0.0

    # Vakantiegeld standaard op 8%
    vakantiegeld_pct = st.number_input(
        "Vakantiegeld (%)", min_value=0.0, max_value=20.0, value=8.0, format="%0.0f"
    )

    # 13e maand
    dertiemaand = st.number_input(
        "13e maand (€)", min_value=0.0, value=0.0, step=100.0, format="%0.0f"
    )

    vakantiegeld = maandloon * 12 * vakantiegeld_pct / 100
    jaarloon = maandloon * 12 + vakantiegeld + dertiemaand

    st.write(f"**Vakantiegeld:** € {vakantiegeld:,.0f}".replace(",", "."))
    st.write(f"**Brutojaarsalaris:** € {jaarloon:,.0f}".replace(",", "."))

    if "jij_ink" not in st.session_state:
        st.session_state["jij_ink"] = 0.0
    if st.button("Gebruik dit als jaarinkomen"):
        st.session_state["jij_ink"] = jaarloon

# -------------- Linkerkant: Jouw gegevens + Partner + Woning --------------
with left:
    st.markdown("### 👤 Jouw gegevens")
    jij_ink = st.number_input(
        "Bruto Box-1 inkomen (€)",
        min_value=0.0,
        value=st.session_state.get("jij_ink",0.0),
        step=1000.0, format="%0.0f"
    )
    jij_aow = st.checkbox("AOW-gerechtigd?")

    st.divider()
    partner = st.checkbox("Ik heb een fiscale partner")
    if partner:
        st.markdown("### 👥 Partner")
        partner_ink = st.number_input(
            "Bruto Box-1 inkomen partner (€)",
            min_value=0.0, value=0.0, step=1000.0, format="%0.0f"
        )
        partner_aow = st.checkbox("Partner AOW-gerechtigd?")
    else:
        partner_ink = 0.0
        partner_aow = False

    st.divider()
    st.markdown("### 🏡 Eigen woning")
    woz = st.number_input(
        "WOZ-waarde woning (€)",
        min_value=0.0, value=0.0, step=5000.0, format="%0.0f"
    )
    rente = st.number_input(
        "Betaalde hypotheekrente per jaar (€)",
        min_value=0.0, value=0.0, step=500.0, format="%0.0f"
    )

# -----------------------------
# Berekening
# -----------------------------
ewf = eigenwoningforfait(woz)
aftrek = max(0, rente - ewf)

jij_res = bereken_box1(jij_ink, jij_aow, ewf/2 if partner else ewf, aftrek/2 if partner else aftrek)
partner_res = bereken_box1(partner_ink, partner_aow, ewf/2 if partner else 0, aftrek/2 if partner else 0)

totaal_netto = jij_res["netto"] + partner_res["netto"]

# -----------------------------
# Output
# -----------------------------
st.success(f"📌 **Gezamenlijk netto-inkomen per jaar**: € {totaal_netto:,.0f}".replace(",", "."))

with st.expander("📊 Toon berekening & details"):
    st.subheader("Jij")
    st.write({k: f"€ {v:,.0f}".replace(",", ".") for k,v in jij_res.items()})
    if partner:
        st.subheader("Partner")
        st.write({k: f"€ {v:,.0f}".replace(",", ".") for k,v in partner_res.items()})
    st.subheader("Woning / aftrekposten")
    st.write({
        "Eigenwoningforfait": f"€ {ewf:,.0f}".replace(",", "."),
        "Aftrek hypotheekrente": f"€ {aftrek:,.0f}".replace(",", ".")
    })
