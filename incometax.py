import streamlit as st
import plotly.graph_objects as go

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
    """Formateer bedrag: punt voor duizendtallen, komma voor decimalen"""
    return f"€ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
        "belastbaar": round(belastbaar,2),
        "belasting": round(belasting,2),
        "algemene_korting": round(ahk,2),
        "arbeids_korting": round(ak,2),
        "kortingen_totaal": round(heffingskortingen,2),
        "netto": round(netto,2)
    }

# -----------------------------
# UI: layout columns
# -----------------------------
left, right = st.columns([2,1])

# -----------------------------
# Rechterkant: Salaris rekenhulp
# -----------------------------
with right:
    st.markdown("### 🧮 Salaris rekenhulp")
    
    maandloon_str = st.text_input("Bruto maandsalaris (€)", value="0,00")
    try:
        maandloon = float(maandloon_str.replace(".", "").replace(",", "."))
    except:
        maandloon = 0.0

    dertiemaand_checkbox = st.checkbox("Ontvang 13e maand?")
    dertiemaand = maandloon if dertiemaand_checkbox else 0.0

    vakantiegeld_pct = st.number_input(
        "Vakantiegeld (%)", min_value=0.0, max_value=20.0, value=8.0, format="%0.2f", step=0.01
    )
    vakantiegeld = (maandloon * 12 + dertiemaand) * vakantiegeld_pct / 100
    jaarloon = maandloon * 12 + dertiemaand + vakantiegeld

    st.write(f"**Vakantiegeld:** {fmt_euro(vakantiegeld)}")
    st.write(f"**13e maand:** {fmt_euro(dertiemaand)}")
    st.write(f"**Brutojaarsalaris:** {fmt_euro(jaarloon)}")

    if "jij_ink" not in st.session_state:
        st.session_state["jij_ink"] = 0.0
    if st.button("Gebruik dit als jaarinkomen"):
        st.session_state["jij_ink"] = jaarloon

# -----------------------------
# Linkerkant: Jouw gegevens + Partner + Woning
# -----------------------------
with left:
    st.markdown("### 👤 Jouw gegevens")
    jij_ink = st.number_input(
        "Bruto Box-1 inkomen (€)",
        min_value=0.0,
        value=st.session_state.get("jij_ink",0.0),
        step=0.01, format="%0.2f"
    )
    jij_aow = st.checkbox("AOW-gerechtigd?")

    st.divider()
    partner = st.checkbox("Ik heb een fiscale partner")
    if partner:
        st.markdown("### 👥 Partner")
        partner_ink = st.number_input(
            "Bruto Box-1 inkomen partner (€)",
            min_value=0.0, value=0.0, step=0.01, format="%0.2f"
        )
        partner_aow = st.checkbox("Partner AOW-gerechtigd?")
    else:
        partner_ink = 0.0
        partner_aow = False

    st.divider()
    st.markdown("### 🏡 Eigen woning")
    woz = st.number_input(
        "WOZ-waarde woning (€)",
        min_value=0.0, value=0.0, step=0.01, format="%0.2f"
    )
    rente = st.number_input(
        "Betaalde hypotheekrente per jaar (€)",
        min_value=0.0, value=0.0, step=0.01, format="%0.2f"
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
st.success(f"📌 **Gezamenlijk netto-inkomen per jaar**: {fmt_euro(totaal_netto)}")

with st.expander("📊 Toon berekening & details"):
    st.subheader("Jij")
    st.write({k: fmt_euro(v) for k,v in jij_res.items()})
    if partner:
        st.subheader("Partner")
        st.write({k: fmt_euro(v) for k,v in partner_res.items()})
    st.subheader("Woning / aftrekposten")
    st.write({
        "Eigenwoningforfait": fmt_euro(ewf),
        "Aftrek hypotheekrente": fmt_euro(aftrek)
    })

# -----------------------------
# Interactieve grafiek bruto → netto
# -----------------------------
st.markdown("### 📈 Bruto → Netto per maand")

# Maanden 1-12 + evt 13e maand
maanden = [f"Maand {i}" for i in range(1,13)]
if dertiemaand_checkbox:
    maanden.append("13e maand")

# Bruto per maand
bruto_maand = [maandloon]*12
if dertiemaand_checkbox:
    bruto_maand.append(maandloon)

# Netto per maand (evenredig netto berekening)
# Voor eenvoud: netto/jaar * (bruto maand / totaal bruto jaar)
bruto_jaar = maandloon*12 + dertiemaand
netto_maand = [totaal_netto*(bm/bruto_jaar) for bm in bruto_maand]

fig = go.Figure()
fig.add_trace(go.Bar(x=maanden, y=bruto_maand, name='Bruto (€)'))
fig.add_trace(go.Bar(x=maanden, y=netto_maand, name='Netto (€)'))
fig.update_layout(
    barmode='group',
    yaxis_title="Bedrag (€)",
    xaxis_title="Maand",
    yaxis_tickformat=',.2f',
    legend=dict(x=0.8, y=1.1)
)
st.plotly_chart(fig, use_container_width=True)
