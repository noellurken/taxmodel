import streamlit as st

st.set_page_config(page_title="NL Net Income Calculator (Box system)")
st.title("🇳🇱 Netherlands Net Income Calculator – Box 1/2/3")

# Inputs for Box 1
st.subheader("Box 1: Income from work & home ownership")
gross_box1 = st.number_input("Gross income (Box 1) (€)", min_value=0.0, step=100.0, value=0.0)

# Inputs for Box 2
st.subheader("Box 2: Income from substantial interest")
income_box2 = st.number_input("Box 2 income (€)", min_value=0.0, step=100.0, value=0.0)

# Inputs for Box 3
st.subheader("Box 3: Income from savings/investments")
assets_box3 = st.number_input("Total assets (Box 3) (€)", min_value=0.0, step=100.0, value=0.0)
debts_box3 = st.number_input("Total debts (Box 3) (€)", min_value=0.0, step=100.0, value=0.0)
tax_partner = st.checkbox("Do you have a tax-partner (Box 3 allowance doubling)")

# Button
if st.button("Calculate Net Income"):
    # Box 1 calculation
    if gross_box1 <= 38_441:
        rate1 = 0.3582
    elif gross_box1 <= 76_817:
        rate1 = 0.3748
    else:
        rate1 = 0.4950
    tax1 = gross_box1 * rate1

    # Box 2 calculation
    if income_box2 <= 67_804:
        rate2 = 0.245
    else:
        rate2 = 0.31
    tax2 = income_box2 * rate2

    # Box 3 calculation
    allowance = 57_684
    if tax_partner:
        allowance *= 2
    taxable_assets = max(0.0, assets_box3 - debts_box3 - allowance)
    # Using simplified assumed return: e.g., assume return 5% on taxable assets
    assumed_return_rate = 0.0588
    assumed_return = taxable_assets * assumed_return_rate
    rate3 = 0.36
    tax3 = assumed_return * rate3

    total_tax = tax1 + tax2 + tax3
    net_income = gross_box1 + income_box2 - total_tax  # Note: Box3 is tax on assets, not income addition

    st.write("---")
    st.success(f"✅ Net Income (after tax on Box 1 & Box 2): €{net_income:,.2f}")
    st.info(f"🧮 Tax breakdown:")
    st.write(f"Box 1 tax (€): €{tax1:,.2f}")
    st.write(f"Box 2 tax (€): €{tax2:,.2f}")
    st.write(f"Box 3 tax (€): €{tax3:,.2f} (on assets)")

st.caption("Note: This is a simplified model. Use as approx. Not official tax advice.")
