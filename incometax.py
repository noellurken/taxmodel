import streamlit as st

st.set_page_config(page_title="NL Netto Inkomen Calculator 2025", layout="wide")

st.title("💶 Nederlandse Netto-Inkomen Calculator 2025")
st.caption("Inclusief hypotheekrenteaftrek, eigenwoningforfait en heffingskortingen volgens 2025 regels")

# ─────────────────────────────────────────────────────────────
#  Functions — Belastingregels 2025
# ─────────────────────────────────────────────────────────────

def algemene_heffingskorting_2025(inkomen, aow):
    # Grenzen 2025
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
    # Bronnen 2025: Belastingdienst tabellen
    if arbeidsinkomen <= 11294:
        return 0.086 * arbeidsinkomen
    elif arbeidsinkomen <= 39422:
        return 971 + 0.31707 * (arbeidsinkomen - 11294)
    elif arbeidsinkomen <= 124283:
        return 4319 - 0.06455 * (arbeidsinkomen - 39422)
    else:
        return 0

def eigenwoningforfait(woz):
    # Tarief 0,45% in 2025 tot 1.2M
    return 0.0045 * woz

def bereken_box1(ink, aow, ewf, renteaftrek):
    # Box 1 tarief 2025
    tarief = 0.3687 if not aow else 0.1907  # vereenvoudigde AOW-tariefscheiding

    belastbaar = ink + ewf - renteaftrek
    if belastbaar < 0:
        belastbaar = 0

    belasting = belastbaar * tarief
    ahk = algemene_heffingskorting_2025(ink, aow)
    ak = arbeidskorting_2025(ink)

    heffingskortingen = min(belasting, ahk + ak)
    netto = ink - belasting + heffingskortingen

    return {
        "belastbaar": belastbaar,
        "belasting": belasting,
        "algemene_korting": ahk,
        "arbeids_korting": ak,
        "kortingen_totaal": heffingskortingen,
        "netto": netto
    }

# ─────────────────────────────────────────────────────────────
#  UI — Invoer velden
# ─────────────────────────────────────────────────────────────

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
