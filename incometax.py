import streamlit as st

# App title
st.set_page_config(page_title="Net Income Calculator")
st.title("💰 Net Income Calculator")

# Inputs
st.subheader("Enter your income details:")
gross_income = st.number_input("Gross Income (€)", min_value=0.0, value=0.0, step=100.0)
tax_rate = st.slider("Tax Rate (%)", min_value=0, max_value=60, value=20)

# Calculate button
if st.button("Calculate Net Income"):
    tax_amount = gross_income * (tax_rate / 100)
    net_income = gross_income - tax_amount

    st.success(f"✅ Net Income: **€{net_income:,.2f}**")
    st.info(f"💸 Total Tax Paid: **€{tax_amount:,.2f}**")


