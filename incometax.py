import streamlit as st

st.set_page_config(page_title="NL Netto Inkomen Calculator 2025", layout="wide")

st.set_page_config(page_title="NL Netto Inkomen Calculator 2025", layout="wide")

st.title("💶 Nederlandse Netto-Inkomen Calculator 2025")
st.caption("Inclusief hypotheekrenteaftrek, eigenwoningforfait en heffingskortingen volgens 2025-regels")

# ─────────────────────────────────────────────────────────────
# Layout: Linkerkant = belasting-invoer, Rechterkant = salaris calculator
# ─────────────────────────────────────────────────────────────
left, right = st.columns([2, 1])

with right:
    st.markdown("### 🧮 Salaris rekenhulp")

    maandloon = st.number_input(
        "Bruto maandsalaris (€)",
        min_value=0.0, value=4_000.0, step=100.0, format="%.2f"
    )
    vakantiegeld_pct = st.number_input(
        "Vakantiegeld (%)", min_value=0.0, max_value=20.0, value=8.0, format="%.1f"
    )

    vakantiegeld = maandloon * 12 * (vakantiegeld_pct / 100)
    jaarloon = maandloon * 12 + vakantiegeld

    st.write(f"**Vakantiegeld:** € {vakantiegeld:,.2f}")
    st.write(f"**Brutojaarsalaris:** € {jaarloon:,.2f}")

    if st.button("Gebruik dit als jaarinkomen"):
        st.session_state["jij_ink"] = jaarloon


with left:
    st.markdown("### 👤 Jouw gegevens")

    jij_ink = st.number_input(
        "Bruto Box-1 inkomen (€)",
        min_value=0.0,
        value=st.session_state.get("jij_ink", 60_000.0),
        step=1000.0,
        format="%.2f"
    )
    jij_aow = st.checkbox("AOW-gerechtigd?")

st.markdown("### 👤 Jouw gegevens")

jij_ink = st.number_input("Bruto Box-1 inkomen (€)", min_value=0.0, value=60_000.0, step=1000.0, format="%.2f")
jij_aow = st.checkbox("AOW-gerechtigd?")

st.divider()

partner = st.checkbox("Ik heb een fiscale partner")

if partner:
    st.markdown("### 👥 Partner")
    partner_ink = st.number_input("Bruto Box-1 inkomen partner (€)", min_value=0.0, value=30_000.0, step=1000.0, format="%.2f")
    partner_aow = st.checkbox("Partner AOW-gerechtigd?")
else:
    partner_ink = 0
    partner_aow = False

st.divider()

st.markdown("### 🏡 Eigen woning")
woz = st.number_input("WOZ-waarde woning (€)", min_value=0.0, value=450_000.0, step=5000.0, format="%.2f")
rente = st.number_input("Betaalde hypotheekrente per jaar (€)", min_value=0.0, value=10_000.0, step=500.0, format="%.2f")

# ─────────────────────────────────────────────────────────────
#  Berekening
# ─────────────────────────────────────────────────────────────

ewf = eigenwoningforfait(woz)
aftrek = max(0, rente - ewf)

jij = bereken_box1(jij_ink, jij_aow, ewf/2 if partner else ewf, aftrek/2 if partner else aftrek)
partner_res = bereken_box1(partner_ink, partner_aow, ewf/2 if partner else 0, aftrek/2 if partner else 0)

totaal_netto = jij["netto"] + partner_res["netto"]

# ─────────────────────────────────────────────────────────────
#  Output
# ─────────────────────────────────────────────────────────────

st.success(f"📌 **Gezamenlijk netto-inkomen per jaar**: € {totaal_netto:,.2f}")

with st.expander("📊 Toon berekening & details"):
    st.subheader("Jij")
    st.write(jij)

    if partner:
        st.subheader("Partner")
        st.write(partner_res)

    st.subheader("Woning / aftrekposten")
    st.write({
        "Eigenwoningforfait": ewf,
        "Aftrek hypotheekrente": aftrek
    })
