import streamlit as st

st.set_page_config(page_title="NL Net Income Calculator (Box system + credits)")
st.title("🇳🇱 Netherlands Net Income Calculator – Box 1/2/3 with Tax Credits")

# --------------------------
# Inputs
# --------------------------
st.subheader("Box 1: Income from work & home ownership")
gross_box1 = st.number_input("Gross income (Box 1) (€)", min_value=0.0, step=100.0, value=0.0)

st.subheader("Box 2: Income from substantial interest")
income_box2 = st.number_input("Box 2 income (€)", min_value=0.0, step=100.0, value=0.0)

st.subheader("Box 3: Income from savings/investments")
assets_box3 = st.number_input("Total assets (Box 3) (€)", min_value=0.0, step=100.0, value=0.0)
debts_box3 = st.number_input("Total debts (Box 3) (€)", min_value=0.0, step=100.0, value=0.0)
tax_partner = st.checkbox("Do you have a tax‑partner (Box 3 allowance doubling)")

# --------------------------
# Tax Credit Functions (simplified 2025)
# --------------------------
def calculate_general_tax_credit(income):
    # Max 3,070 €, phased out at higher income (~73,000)
    max_credit = 3070
    if income <= 73_000:
        return max_credit
    else:
        # linear phase-out above 73k
        credit = max(0, max_credit - 0.056 * (income - 73_000))
        return credit

def calculate_labour_tax_credit(income):
    # Simplified 2025 approximation
    if income <= 11_000:
        return 0
    elif income <= 36_000:
        return 1_000 + 0.215 * (income - 11_000)  # increasing part
    elif income <= 112_000:
        return max(0, 5_000 - 0.061 * (income - 36_000))  # decreasing part
    else:
        return 0

# --------------------------
# Calculation
# --------------------------
if st.button("Calculate Net Income"):
    # Box 1
    if gross_box1 <= 38_441:
        rate1 = 0.3582
    elif gross_box1 <= 76_817:
        rate1 = 0.3748
    else:
        rate1 = 0.4950
    tax1_before_credit = gross_box1 * rate1

    # Tax credits
    general_credit = calculate_general_tax_credit(gross_box1)
    labour_credit = calculate_labour_tax_credit(gross_box1)
    total_credit = general_credit + labour_credit

    tax1_after_credit = max(0, tax1_before_credit - total_credit)

    # Box 2
    if income_box2 <= 67_804:
        rate2 = 0.245
    else:
        rate2 = 0.31
    tax2 = income_box2 * rate2

    # Box 3
    allowance = 57_684
    if tax_partner:
        allowance *= 2
    taxable_assets = max(0.0, assets_box3 - debts_box3 - allowance)
    assumed_return_rate = 0.0588
    assumed_return = taxable_assets * assumed_return_rate
    rate3 = 0.36
    tax3 = assumed_return * rate3

    # Total tax & net income
    total_tax = tax1_after_credit + tax2 + tax3
    net_income = gross_box1 + income_box2 - (tax1_after_credit + tax2)  # Box3 is wealth tax

    # --------------------------
    # Output
    # --------------------------
    st.write("---")
    st.success(f"✅ Net Income (after tax on Box 1 & Box 2): €{net_income:,.2f}")
    st.info("🧮 Tax Breakdown:")
    st.write(f"Box 1 tax before credits: €{tax1_before_credit:,.2f}")
    st.write(f"Total tax credits (Box 1): €{total_credit:,.2f}")
    st.write(f"Box 1 tax after credits: €{tax1_after_credit:,.2f}")
    st.write(f"Box 2 tax: €{tax2:,.2f}")
    st.write(f"Box 3 tax (on assets): €{tax3:,.2f}")
