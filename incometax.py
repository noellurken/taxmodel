import streamlit as st
import plotly.graph_objects as go

# --------------------------
# Page Setup
# --------------------------
st.set_page_config(page_title="NL Net Income Calculator", layout="wide")
st.title("🇳🇱 Netherlands Net Income Calculator – Full Box System with Mortgage Deduction & Chart")

# --------------------------
# Inputs: Box 1
# --------------------------
st.subheader("Box 1: Income from work & home ownership")
gross_box1 = st.number_input("Gross income (Box 1) (€)", min_value=0.0, step=100.0, value=0.0)
mortgage_interest = st.number_input("Mortgage interest deduction (€)", min_value=0.0, step=100.0, value=0.0)

# --------------------------
# Inputs: Box 2
# --------------------------
st.subheader("Box 2: Income from substantial interest")
income_box2 = st.number_input("Box 2 income (€)", min_value=0.0, step=100.0, value=0.0)

# --------------------------
# Inputs: Box 3
# --------------------------
st.subheader("Box 3: Income from savings/investments")
assets_box3 = st.number_input("Total assets (Box 3) (€)", min_value=0.0, step=100.0, value=0.0)
debts_box3 = st.number_input("Total debts (Box 3) (€)", min_value=0.0, step=100.0, value=0.0)
tax_partner = st.checkbox("Do you have a tax‑partner (Box 3 allowance doubling)")

# --------------------------
# Tax Credit Functions
# --------------------------
def calculate_general_tax_credit(income):
    max_credit = 3070
    if income <= 73_000:
        return max_credit
    else:
        credit = max(0, max_credit - 0.056 * (income - 73_000))
        return credit

def calculate_labour_tax_credit(income):
    if income <= 11_000:
        return 0
    elif income <= 36_000:
        return 1_000 + 0.215 * (income - 11_000)
    elif income <= 112_000:
        return max(0, 5_000 - 0.061 * (income - 36_000))
    else:
        return 0

# --------------------------
# Box 3 Progressive Rates
# --------------------------
def calculate_box3_tax(assets, debts, partner=False):
    allowance = 57_684
    if partner:
        allowance *= 2
    taxable_assets = max(0, assets - debts - allowance)
    tier1_limit = 103_000
    tier2_limit = 1_030_000
    tier1_rate = 0.01818
    tier2_rate = 0.04366
    tier3_rate = 0.0553
    if taxable_assets <= tier1_limit:
        assumed_return = taxable_assets * tier1_rate
    elif taxable_assets <= tier2_limit:
        assumed_return = tier1_limit * tier1_rate + (taxable_assets - tier1_limit) * tier2_rate
    else:
        assumed_return = tier1_limit * tier1_rate + (tier2_limit - tier1_limit) * tier2_rate + (taxable_assets - tier2_limit) * tier3_rate
    tax3 = assumed_return * 0.36
    return tax3

# --------------------------
# Calculate Taxes
# --------------------------
if st.button("Calculate Net Income"):
    # Box 1
    taxable_box1 = max(0, gross_box1 - mortgage_interest)
    if taxable_box1 <= 38_441:
        rate1 = 0.3582
    elif taxable_box1 <= 76_817:
        rate1 = 0.3748
    else:
        rate1 = 0.4950
    tax1_before_credit = taxable_box1 * rate1
    general_credit = calculate_general_tax_credit(taxable_box1)
    labour_credit = calculate_labour_tax_credit(taxable_box1)
    total_credit = general_credit + labour_credit
    tax1_after_credit = max(0, tax1_before_credit - total_credit)

    # Box 2
    if income_box2 <= 67_804:
        rate2 = 0.245
    else:
        rate2 = 0.31
    tax2 = income_box2 * rate2

    # Box 3
    tax3 = calculate_box3_tax(assets_box3, debts_box3, tax_partner)

    # Net income (Box3 is wealth tax)
    net_income = gross_box1 + income_box2 - (tax1_after_credit + tax2)
    total_tax = tax1_after_credit + tax2 + tax3
    effective_tax_rate = total_tax / (gross_box1 + income_box2) if (gross_box1 + income_box2) > 0 else 0

    # --------------------------
    # Display Results
    # --------------------------
    st.write("---")
    st.success(f"✅ Net Income (after Box 1 & Box 2 taxes): €{net_income:,.2f}")
    st.info("🧮 Tax Breakdown:")
    st.write(f"Box 1 tax after credits: €{tax1_after_credit:,.2f}")
    st.write(f"Box 2 tax: €{tax2:,.2f}")
    st.write(f"Box 3 tax (on assets): €{tax3:,.2f}")
    st.write(f"Total taxes (including Box 3): €{total_tax:,.2f}")
    st.write(f"Effective tax rate: {effective_tax_rate*100:.2f}%")

    # --------------------------
    # Interactive Chart
    # --------------------------
    fig = go.Figure(data=[
        go.Bar(name="Box 1", x=["Taxes"], y=[tax1_after_credit], marker_color="indianred"),
        go.Bar(name="Box 2", x=["Taxes"], y=[tax2], marker_color="lightsalmon"),
        go.Bar(name="Box 3", x=["Taxes"], y=[tax3], marker_color="lightblue"),
    ])
    fig.update_layout(barmode='stack', title="Tax Contribution per Box", yaxis_title="€")
    st.plotly_chart(fig, use_container_width=True)

    # Pie chart for visual share
    fig2 = go.Figure(data=[go.Pie(labels=["Box 1", "Box 2", "Box 3"], values=[tax1_after_credit, tax2, tax3], hole=0.4)])
    fig2.update_layout(title="Share of Taxes by Box")
    st.plotly_chart(fig2, use_container_width=True)
