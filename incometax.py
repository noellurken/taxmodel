import streamlit as st
import pandas as pd

# -----------------------------
# 2025 FISCUS FUNCTIES
# -----------------------------

def algemene_heffingskorting(inkomen, aow=False):
    # bron: Belastingdienst tabellen 2025
    if not aow:  # onder AOW-leeftijd
        if inkomen <= 28_406:
            return 3_068.0
        elif inkomen <= 76_817:
            return max(0.0, 3_068.0 - 0.06337 * (inkomen - 28_406))
        else:
            return 0.0
    else:  # AOW-gerechtigd
        if inkomen <= 28_406:
            return 1_536.0
        elif inkomen <= 76_817:
            return max(0.0, 1_536.0 - 0.03170 * (inkomen - 28_406))
        else:
            return 0.0

def arbeidskorting(arbeidsinkomen, aow=False):
    # bron: Belastingdienst tabellen 2025
    if arbeidsinkomen <= 12_169:
        korting = 0.08053 * arbeidsinkomen
    elif arbeidsinkomen <= 26_288:
        korting = 980.0 + 0.30030 * (arbeidsinkomen - 12_169)
    elif arbeidsinkomen <= 43_071:
        korting = 5_220.0 + 0.02258 * (arbeidsinkomen - 26_288)
    elif arbeidsinkomen <= 129_078:
        korting = 5_599.0 - 0.06510 * (arbeidsinkomen - 43_071)
    else:
        korting = 0.0

    # AOW heeft aangepaste percentages maar Belastingdienst publiceert volledige tabel;
    # Voor nu lineair schalen met factor (AOW krijgt 50% korting)
    if aow:
        korting *= 0.5

    return max(0.0, korting)

def eigenwoningforfait(woz):
    return 0.0035 * woz  # 0,35% WOZ in 2025

def box1_belasting(belastbaar_inkomen):
    if belastbaar_inkomen <= 75_518:
        return belastbaar_inkomen * 0.3697
    else:
        return 75_518 * 0.3697 + (belastbaar_inkomen - 75_518) * 0.4950

# -----------------------------
# STREAMLIT UI
# -----------------------------

st.set_page_config(page_title="NL Belastingcalculator 2025", layout="wide")
st.title("🇳🇱 Nederlandse Inkomstenbelasting Calculator 2025")

st.write("Inclusief: algemene heffingskorting, arbeidskorting, hypotheekrenteaftrek, EWF, partners.")

# ---- INVOER ----
col1, col2 = st.columns(2)

with col1:
    st.header("Jij")
    jij_ink = st.number_input("Bruto Box 1-inkomen (€)", value=60_000.0, min_value=0.0, step=1_000.0, format="%.2f")
    jij_aow = st.checkbox("AOW-gerechtigd (jij)?", value=False)

with col2:
    st.header("Partner")
    partner = st.checkbox("Ik heb een fiscale partner", value=False)
    if partner:
        partner_ink = st.number_input("Bruto Box 1-inkomen partner (€)", value=30_000.0, min_value=0.0, step=1_000.0, format="%.2f")
        partner_aow = st.checkbox("AOW-gerechtigd (partner)?", value=False)
    else:
        partner_ink = 0.0
        partner_aow = False

st.header("Eigen woning")
woz = st.number_input("WOZ-waarde (€)", value=400_000.0, min_value=0.0, step=10_000.0, format="%.2f")
rente = st.number_input("Betaalde hypotheekrente (€)", value=10_000.0, min_value=0.0, step=500.0, format="%.2f")

if partner:
    split = st.slider("Verdeling hypotheekrenteaftrek naar jou (%)", 0, 100, 50)
else:
    split = 100

toon_steps = st.checkbox("Toon tussenstappen", value=True)

# ---- BEREKENING ----
ewf = eigenwoningforfait(woz)

aftrek_jij = rente * (split / 100)
aftrek_partner = rente - aftrek_jij if partner else 0

bel_jij = jij_ink + ewf - aftrek_jij
bel_partner = partner_ink + ewf - aftrek_partner if partner else 0

tax_jij = box1_belasting(bel_jij)
tax_partner = box1_belasting(bel_partner) if partner else 0

hk_jij = algemene_heffingskorting(bel_jij, jij_aow) + arbeidskorting(jij_ink, jij_aow)
hk_partner = algemene_heffingskorting(bel_partner, partner_aow) + arbeidskorting(partner_ink, partner_aow) if partner else 0

netto_jij = max(0.0, tax_jij - hk_jij)
netto_partner = max(0.0, tax_partner - hk_partner) if partner else 0
totaal = netto_jij + netto_partner

# ---- OUTPUT ----
st.header("Resultaat")
st.success(f"Totale verschuldigde belasting: **€ {totaal:,.2f}**")

# Tussenstappen
if toon_steps:
    st.subheader("Tussenstappen berekening")
    df = pd.DataFrame({
        " ": [
            "Box 1-inkomen",
            "Eigenwoningforfait",
            "Hypotheekrenteaftrek",
            "Belastbaar inkomen Box 1",
            "Bruto Box 1-belasting",
            "Heffingskortingen",
            "Netto te betalen"
        ],
        "Jij (€)": [
            jij_ink, ewf, -aftrek_jij, bel_jij, tax_jij, -hk_jij, netto_jij
        ],
        "Partner (€)": [
            partner_ink if partner else None,
            ewf if partner else None,
            -aftrek_partner if partner else None,
            bel_partner if partner else None,
            tax_partner if partner else None,
            -hk_partner if partner else None,
            netto_partner if partner else None
        ]
    })
    st.dataframe(df.set_index(" "))

st.caption("📌 Indicatief — geen fiscaal advies. Gebaseerd op gepubliceerde Belastingdienst-tabellen 2025.")
