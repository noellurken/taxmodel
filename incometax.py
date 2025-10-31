import streamlit as st
import pandas as pd

# -----------------------------
# Pagina configuratie
# -----------------------------
st.set_page_config(page_title="NL Netto Inkomen Calculator 2025", layout="wide")
st.title("💶 Nederlandse Netto-Inkomen Calculator 2025")
st.caption("Inclusief hypotheekrenteaftrek, eigenwoningforfait staffel en heffingskortingen 2025")

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
        "belastbaar": round(belastbaar,2),
        "belasting": round(belasting,2),
        "algemene_korting": round(ahk,2),
        "arbeids_korting": round(ak,2),
        "kortingen_totaal": round(heffingskortingen,2),
        "netto": round(netto,2)
    }

# -----------------------------
# Layout columns
# -----------------------------
left, right = st.columns([2,1])

# -----------------------------
# Rechterkant: Salarisrekenhulp
# -----------------------------
with right:
    st.markdown("### 🧮 Salarisrekenhulp")

    # Callback om de rekenhulp te resetten bij wisselen
    def reset_rekenhulp():
        st.session_state["maandloon_display"] = "0,00"
        st.session_state["dertiemaand_checkbox"] = False
        st.session_state["vakantiegeld_pct"] = 8.0

    if "gebruiker_radio" not in st.session_state:
        st.session_state["gebruiker_radio"] = "Jij"
    gebruiker = st.radio("Voor wie wil je het salaris invoeren?", ["Jij", "Partner"], key="gebruiker_radio", on_change=reset_rekenhulp)

    # Initialiseer session_state
    for key in ["maandloon_display", "dertiemaand_checkbox", "vakantiegeld_pct"]:
        if key not in st.session_state:
            st.session_state[key] = "0,00" if "maandloon" in key else (False if "dertiemaand" in key else 8.0)

    # Callback voor directe formattering
    def format_salaris_input():
        val = parse_euro_input(st.session_state["maandloon_display"])
        st.session_state["maandloon_display"] = fmt_euro(val)

    st.text_input(
        "Bruto maandsalaris (€)",
        st.session_state["maandloon_display"],
        key="maandloon_display",
        on_change=format_salaris_input
    )

    dertiemaand_checkbox = st.checkbox("Ontvang 13e maand?", value=st.session_state["dertiemaand_checkbox"])
    vakantiegeld_pct = st.number_input(
        "Vakantiegeld (%)",
        min_value=0.0, max_value=20.0,
        value=st.session_state["vakantiegeld_pct"],
        step=0.01, format="%0.2f"
    )

    maandloon = parse_euro_input(st.session_state["maandloon_display"])
    d13 = maandloon if dertiemaand_checkbox else 0.0
    vakantiegeld = (maandloon*12 + d13) * vakantiegeld_pct/100
    jaarloon = maandloon*12 + d13 + vakantiegeld

    st.write(f"**Vakantiegeld:** {fmt_euro(vakantiegeld)}")
    st.write(f"**13e maand:** {fmt_euro(d13)}")
    st.write(f"**Brutojaarsalaris:** {fmt_euro(jaarloon)}")

    st.session_state["dertiemaand_checkbox"] = dertiemaand_checkbox
    st.session_state["vakantiegeld_pct"] = vakantiegeld_pct

    # Callback functies voor knoppen
    def gebruik_voor_jij():
        st.session_state["jij_ink"] = jaarloon
        st.session_state["jij_ink_input"] = fmt_euro(jaarloon)

    def gebruik_voor_partner():
        st.session_state["partner_ink"] = jaarloon
        st.session_state["partner_ink_input"] = fmt_euro(jaarloon)

    if gebruiker == "Jij":
        st.button("Gebruik voor jezelf", on_click=gebruik_voor_jij)
    else:
        st.button("Gebruik voor je partner", on_click=gebruik_voor_partner)

# -----------------------------
# Linkerkant: Jouw gegevens + Partner + Woning
# -----------------------------
with left:
    st.markdown("### 👤 Jouw gegevens")
    jij_ink_input = st.text_input(
        "Bruto Box-1 inkomen (€)",
        key="jij_ink_input",
        value=st.session_state.get("jij_ink_input","0,00")
    )
    jij_ink = parse_euro_input(jij_ink_input)
    jij_aow = st.checkbox("AOW-gerechtigd?")

    st.divider()
    partner_checkbox = st.checkbox("Ik heb een fiscale partner")
    if partner_checkbox:
        st.markdown("### 👥 Partner")
        partner_ink_input = st.text_input(
            "Bruto Box-1 inkomen partner (€)",
            key="partner_ink_input",
            value=st.session_state.get("partner_ink_input","0,00")
        )
        partner_ink = parse_euro_input(partner_ink_input)
        partner_aow = st.checkbox("Partner AOW-gerechtigd?")
    else:
        # Reset partnerinkomen als geen partner
        st.session_state["partner_ink"] = 0.0
        st.session_state["partner_ink_input"] = "0,00"
        partner_ink = 0.0
        partner_aow = False

    st.divider()
    st.markdown("### 🏡 Eigen woning")
    woz_input = st.text_input("WOZ-waarde woning (€)", "0,00")
    woz = parse_euro_input(woz_input)
    rente_input = st.text_input("Betaalde hypotheekrente per jaar (€)", "0,00")
    rente = parse_euro_input(rente_input)

# -----------------------------
# Berekening
# -----------------------------
jij_ink_model = st.session_state.get("jij_ink", jij_ink)
partner_ink_model = st.session_state.get("partner_ink", partner_ink if partner_checkbox else 0.0)

ewf = eigenwoningforfait(woz)
aftrek = max(0, rente - ewf)

jij_res = bereken_box1(jij_ink_model, jij_aow, ewf/2 if partner_checkbox else ewf, aftrek/2 if partner_checkbox else aftrek)
partner_res = bereken_box1(partner_ink_model, partner_aow, ewf/2 if partner_checkbox else 0, aftrek/2 if partner_checkbox else 0)
totaal_netto = jij_res["netto"] + partner_res["netto"]

# -----------------------------
# Output
# -----------------------------
st.success(f"📌 **Gezamenlijk netto-inkomen per jaar**: {fmt_euro(totaal_netto)}")

with st.expander("📊 Toon berekening & details"):
    st.subheader("Jij")
    st.write({k: fmt_euro(v) for k,v in jij_res.items()})
    if partner_checkbox:
        st.subheader("Partner")
        st.write({k: fmt_euro(v) for k,v in partner_res.items()})
    st.subheader("Woning / aftrekposten")
    st.write({
        "Eigenwoningforfait": fmt_euro(ewf),
        "Aftrek hypotheekrente": fmt_euro(aftrek)
    })

# -----------------------------
# Grafiek bruto → netto
# -----------------------------
st.markdown("### 📈 Bruto → Netto per maand")
maanden = [f"Maand {i}" for i in range(1,13)]
if st.session_state["dertiemaand_checkbox"]:
    maanden.append("13e maand")

bruto_maand = [parse_euro_input(st.session_state["maandloon_display"])]*12
if st.session_state["dertiemaand_checkbox"]:
    bruto_maand.append(parse_euro_input(st.session_state["maandloon_display"]))

bruto_jaar = sum(bruto_maand)
netto_maand = [totaal_netto*(bm/bruto_jaar) if bruto_jaar>0 else 0 for bm in bruto_maand]

df_chart = pd.DataFrame({
    "Maand": maanden,
    "Bruto": bruto_maand,
    "Netto": netto_maand
}).set_index("Maand")

st.bar_chart(df_chart)
