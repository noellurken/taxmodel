import streamlit as st
import pandas as pd

# --------------------------
# Page Setup
# --------------------------
st.set_page_config(page_title="NL Net Income Calculator", layout="wide")
st.title("🇳🇱 Netherlands Net Income Calculator – Full Box System with Automatic Mortgage Deduction")

# --------------------------
# Inputs: Box 1
# --------------------------
st.subheader("Box 1: Income from work & home ownership")
gross_box1 = st.number_input("Gross income (Box 1) (€)", min_value=0.0, step=100.0, value=50_000)

# --------------------------
# Inputs: Mortgage Details
# --------------------------
st.subheader("Mortgage Details")
mortgage_amount = st.number_input("Mortgage principal (€)", min_value=0.0, step=1000.0, value=300_000)
annual_interest_rate = st.number_input("Mortgage interest rate (%)", min_value=0.0, max_value=10.0, step=0.1, value=4.0)
mortgage_type = st.selectbox("Mortgage type", ["Annuity", "Linear", "Interest-only"])

def calculate_mortgage_deduction(principal, interest_rate, mortgage_type):
    annual_interest = principal * (interest_rate / 100)
    return annual_interest

mortgage_interest = calculate_mortgage_deduction(mortgage_amount, annual_interest_rate, mortgage_type)
st.write(f"✅ Mortgage interest deduction automatically calculated: €{mortgage_interest:,.2f}")

# --------------------------
# Inputs: Box 2
# --------------------------
st.subheader("Box 2: Income from substantial interest")
income_box2 = st.number_input("Box 2 income (€)", min_value=0.0, step=100.0, value=0.0)

# --------------------------
# Inputs: Box 3
# --------------------------
st.subheader("Box 3: Income from savings/investments")
assets_box3 = st.number_input("Total assets (Box 3) (€)", min_value=0.0, step=100.0, value=100_000)
debts_box3 = st.number_input("Total debts (Box 3) (€)", min_value=0.0, step=100.0, value=20_000)
tax_partner = st.checkbox("Do you have a tax‑partner (Box 3 allowance doubling)")

# --------------------------
# Tax Credit Functions
# --------------------------
def calculate_general_tax_credit(income):
    max_credit = 3070
    if income <= 73_000:
        return max_credit
    else:
        return max(0, max_credit - 0.056 * (income - 73_000))

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
    st.write(f"Box 1 taxable income: €{taxable_box1:,.2f}")
    st.write(f"Box 1 tax after credits: €{tax1_after_credit:,.2f}")
    st.write(f"Box 2 tax: €{tax2:,.2f}")
    st.write(f"Box 3 tax (on assets): €{tax3:,.2f}")
    st.write(f"Total taxes (including Box 3): €{total_tax:,.2f}")
    st.write(f"Effective tax rate: {effective_tax_rate*100:.2f}%")

    # --------------------------
    # Bar Chart (Streamlit native)
    # --------------------------
    st.subheader("Tax Contribution per Box (Bar Chart)")
    data = pd.DataFrame({
        'Box': ['Box 1', 'Box 2', 'Box 3'],
        'Tax (€)': [tax1_after_credit, tax2, tax3]
    })
    st.bar_chart(data.set_index('Box'))

    # --------------------------
    # Pie-like horizontal stacked bar using native chart
    # --------------------------
    st.subheader("Share of Taxes by Box (Stacked Bar)")
    percentages = [tax1_after_credit, tax2, tax3]
    df = pd.DataFrame([percentages], columns=['Box 1', 'Box 2', 'Box 3'])
    st.bar_chart(df)
