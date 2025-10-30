# app.py
import streamlit as st
import pandas as pd
from math import isclose

# --------------------------
# Constants / Parameters (2025)
# --------------------------
HILLEN_PERCENT_2025 = 0.7667  # hillen: you keep 76.67% of the difference as deduction where applicable
MAX_DEDUCTION_RATE_2025 = 0.3748  # cap on tax benefit from mortgage interest (tariefsaanpassing)
EWF_RATE_DEFAULT = 0.0035  # common EWF rate for typical WOZ bands

# --------------------------
# Helper: Box1 tax calculation using 2025 bands (progressive)
# Returns tax amount (before credits)
# --------------------------
def calc_box1_tax(taxable_income: float) -> float:
    tax = 0.0
    x = float(max(0.0, taxable_income))
    # Band thresholds
    b1 = 38441.0
    b2 = 76817.0
    # Rates: note band1 is split: payroll/NI vs income tax; using combined values appropriate for net effect
    # Here we apply the commonly used combined rates as in earlier model:
    if x <= 0.0:
        return 0.0
    if x <= b1:
        tax += x * 0.1792
        return tax
    tax += b1 * 0.1792
    if x <= b2:
        tax += (x - b1) * 0.3748
        return tax
    tax += (b2 - b1) * 0.3748
    tax += (x - b2) * 0.4950
    return tax

# --------------------------
# Eigenwoningforfait (EWF) 2025 table implementation
# --------------------------
def calc_eigenwoningforfait(woz_value: float) -> float:
    w = float(max(0.0, woz_value))
    if w <= 12_500.0:
        return 0.0
    if w <= 25_000.0:
        return w * 0.0010
    if w <= 50_000.0:
        return w * 0.0020
    if w <= 75_000.0:
        return w * 0.0025
    if w <= 1_330_000.0:
        return w * 0.0035
    base = 4655.0
    extra = (w - 1_330_000.0) * 0.0235
    return base + extra

# --------------------------
# Mortgage interest (first-year) calculation
# Supports Annuity, Linear, Interest-only
# --------------------------
def annual_interest_paid(principal: float, annual_rate_pct: float, term_years: int = 30, mort_type: str = "Annuity") -> float:
    P = float(max(0.0, principal))
    r_annual = float(max(0.0, annual_rate_pct)) / 100.0
    months = max(1, int(term_years) * 12)
    if P <= 0.0 or r_annual <= 0.0:
        return 0.0

    if mort_type == "Interest-only":
        return P * r_annual

    monthly_rate = r_annual / 12.0

    if mort_type == "Linear":
        monthly_principal = P / months
        outstanding = P
        total_interest = 0.0
        for m in range(12):
            interest = outstanding * monthly_rate
            total_interest += interest
            outstanding -= monthly_principal
        return total_interest

    # Annuity mortgage
    if monthly_rate == 0:
        monthly_payment = P / months
    else:
        monthly_payment = monthly_rate * P / (1 - (1 + monthly_rate) ** (-months))
    outstanding = P
    total_interest = 0.0
    for m in range(12):
        interest = outstanding * monthly_rate
        principal_paid = monthly_payment - interest
        total_interest += interest
        outstanding -= principal_paid
    return total_interest

# --------------------------
# Tax credits (simplified realistic 2025 formulas)
# --------------------------
def calculate_general_tax_credit(income: float) -> float:
    max_credit = 3070.0
    income = float(max(0.0, income))
    if income <= 73000.0:
        return max_credit
    return max(0.0, max_credit - 0.056 * (income - 73000.0))

def calculate_labour_tax_credit(income: float) -> float:
    income = float(max(0.0, income))
    if income <= 11000.0:
        return 0.0
    if income <= 36000.0:
        return 1000.0 + 0.215 * (income - 11000.0)
    if income <= 112000.0:
        return max(0.0, 5000.0 - 0.061 * (income - 36000.0))
    return 0.0

# --------------------------
# Box 3 tax (progressive assumed return model) -> returns tax in euros
# --------------------------
def calculate_box3_tax(assets: float, debts: float, partner: bool = False) -> float:
    allowance = 57_684.0
    if partner:
        allowance *= 2.0
    taxable_assets = max(0.0, float(assets) - float(debts) - allowance)
    tier1_limit = 103_000.0
    tier2_limit = 1_030_000.0
    tier1_rate = 0.01818
    tier2_rate = 0.04366
    tier3_rate = 0.0553
    if taxable_assets <= 0.0:
        assumed_return = 0.0
    elif taxable_assets <= tier1_limit:
        assumed_return = taxable_assets * tier1_rate
    elif taxable_assets <= tier2_limit:
        assumed_return = tier1_limit * tier1_rate + (taxable_assets - tier1_limit) * tier2_rate
    else:
        assumed_return = (
            tier1_limit * tier1_rate
            + (tier2_limit - tier1_limit) * tier2_rate
            + (taxable_assets - tier2_limit) * tier3_rate
        )
    tax3 = assumed_return * 0.36
    return tax3

# --------------------------
# UI Inputs
# --------------------------
st.set_page_config(page_title="NL Net Income Calculator — Full Mortgage Rules", layout="wide")
st.title("🇳🇱 NL Net Income Calculator — Full Mortgage Rules (2025)")

st.subheader("Personal & Income")
gross_income = st.number_input("Gross income from work (Box 1) (€)", min_value=0.0, step=100.0, value=50000.0)

st.subheader("Property / Mortgage details (for mortgage interest deduction)")
woz_value = st.number_input("WOZ home value (€)", min_value=0.0, step=1000.0, value=400000.0)
mortgage_principal = st.number_input("Outstanding mortgage principal (€)", min_value=0.0, step=1000.0, value=300000.0)
annual_interest_rate = st.number_input("Mortgage interest rate (%)", min_value=0.0, max_value=20.0, step=0.01, value=4.00)
mortgage_type = st.selectbox("Mortgage type", ["Annuity", "Linear", "Interest-only"])
mortgage_term = st.number_input("Remaining term (years)", min_value=1, step=1, value=30)

st.subheader("Other boxes")
income_box2 = st.number_input("Box 2 income (substantial interest) (€)", min_value=0.0, step=100.0, value=0.0)
assets_box3 = st.number_input("Total assets (Box 3) (€)", min_value=0.0, step=100.0, value=100000.0)
debts_box3 = st.number_input("Total debts (Box 3) (€)", min_value=0.0, step=100.0, value=20000.0)
tax_partner = st.checkbox("Have a tax partner (Box 3 allowance doubles)")

# --------------------------
# Calculate
# --------------------------
if st.button("Calculate (full legal rules)"):
    # 1) Eigenwoningforfait
    ewf = calc_eigenwoningforfait(woz_value)

    # 2) Mortgage interest paid (approx first year)
    mortgage_interest = annual_interest_paid(mortgage_principal, annual_interest_rate, int(mortgage_term), mortgage_type)

    # 3) Raw income from home: EWF - interest (positive means net taxable benefit; negative means deductible interest)
    raw_income_from_home = ewf - mortgage_interest

    # 4) Apply hillenregeling when mortgage_interest < EWF (raw_income_from_home > 0)
    if raw_income_from_home > 0.0:
        # You fall into the no-or-small-debt regime; you only get HILLEN_PERCENT_2025 of the "difference" as deduction
        hillen = HILLEN_PERCENT_2025
        # The amount effectively reducing taxable income (negative) is:
        # net_income_from_home = raw_income_from_home * (1 - hillen)
        # if raw_income_from_home > 0, this will remain positive (an addition), but the deductible part is hillen * raw.
        net_income_from_home = raw_income_from_home * (1.0 - hillen)
        hillen_deduction_amount = raw_income_from_home * hillen
    else:
        # If raw_income_from_home <= 0 -> interest > EWF: full deduction of (mortgage_interest - ewf)
        net_income_from_home = raw_income_from_home  # negative value reduces taxable income
        hillen_deduction_amount = 0.0

    # 5) Box 1 taxable income (gross income plus income from main residence)
    taxable_box1 = max(0.0, gross_income + net_income_from_home)

    # 6) Taxable Box1 if NO mortgage deduction (for baseline comparison)
    taxable_box1_no_deduction = max(0.0, gross_income + ewf)  # baseline where you cannot deduct interest

    # 7) Compute Box1 tax amounts
    tax_no_deduction_before_credits = calc_box1_tax(taxable_box1_no_deduction)
    tax_with_deduction_before_credits = calc_box1_tax(taxable_box1)

    # 8) Tax credits on both scenarios
    gen_credit_no = calculate_general_tax_credit(taxable_box1_no_deduction)
    lab_credit_no = calculate_labour_tax_credit(taxable_box1_no_deduction)
    total_credits_no = gen_credit_no + lab_credit_no
    tax_no_deduction_after_credits = max(0.0, tax_no_deduction_before_credits - total_credits_no)

    gen_credit_with = calculate_general_tax_credit(taxable_box1)
    lab_credit_with = calculate_labour_tax_credit(taxable_box1)
    total_credits_with = gen_credit_with + lab_credit_with
    tax_with_deduction_after_credits = max(0.0, tax_with_deduction_before_credits - total_credits_with)

    # 9) Raw tax benefit from mortgage deduction
    tax_benefit_raw = tax_no_deduction_after_credits - tax_with_deduction_after_credits

    # 10) Cap the benefit at MAX_DEDUCTION_RATE_2025 * mortgage_interest
    cap_amount = mortgage_interest * MAX_DEDUCTION_RATE_2025
    cap_applied = False
    if tax_benefit_raw <= cap_amount + 1e-9:
        tax_box1_final = tax_with_deduction_after_credits
        tax_benefit = tax_benefit_raw
    else:
        cap_applied = True
        tax_benefit = cap_amount
        tax_box1_final = max(0.0, tax_no_deduction_after_credits - tax_benefit)

    # 11) Box 2 tax
    if income_box2 <= 67804.0:
        rate2 = 0.245
    else:
        rate2 = 0.31
    tax_box2 = income_box2 * rate2

    # 12) Box 3 tax
    tax_box3 = calculate_box3_tax(assets_box3, debts_box3, tax_partner)

    # 13) Totals and effective rates
    total_tax_all = tax_box1_final + tax_box2 + tax_box3
    gross_cash_income = gross_income + income_box2  # Box3 is wealth tax, not cash income
    effective_tax_rate = (total_tax_all / gross_cash_income) if gross_cash_income > 0 else 0.0
    net_income_cash = gross_cash_income - (tax_box1_final + tax_box2)

    # --------------------------
    # Outputs
    # --------------------------
    st.write("---")
    st.header("Results (full legal rules applied)")

    st.subheader("Mortgage & EWF")
    st.write(f"WOZ value: €{woz_value:,.2f}")
    st.write(f"Eigenwoningforfait (EWF): €{ewf:,.2f}")
    st.write(f"Estimated annual mortgage interest paid (first year): €{mortgage_interest:,.2f}")
    if raw_income_from_home > 0.0:
        st.write(f"Raw difference (EWF - interest): €{raw_income_from_home:,.2f} → hillen regime applies")
        st.write(f"Hillen deduction portion (protected): €{hillen_deduction_amount:,.2f}")
        st.write(f"Net addition to taxable income after hillen: €{net_income_from_home:,.2f}")
    else:
        st.write(f"Raw difference (EWF - interest): €{raw_income_from_home:,.2f} → interest > EWF, full deduction applied")

    st.subheader("Box 1 tax (mortgage effect)")
    st.write(f"Taxable Box 1 WITHOUT mortgage deduction: €{taxable_box1_no_deduction:,.2f}")
    st.write(f"Tax WITHOUT mortgage deduction (after credits): €{tax_no_deduction_after_credits:,.2f}")
    st.write(f"Taxable Box 1 WITH mortgage deduction: €{taxable_box1:,.2f}")
    st.write(f"Tax WITH mortgage deduction (before cap, after credits): €{tax_with_deduction_after_credits:,.2f}")
    st.write(f"Raw tax benefit from mortgage deduction: €{tax_benefit_raw:,.2f}")
    st.write(f"Cap on benefit (max {MAX_DEDUCTION_RATE_2025*100:.2f}% of interest): €{cap_amount:,.2f}")
    st.write(f"Cap applied: {'Yes' if cap_applied else 'No'}")
    st.write(f"Final Box 1 tax after applying cap (if any): €{tax_box1_final:,.2f}")

    st.subheader("Other boxes")
    st.write(f"Box 2 tax: €{tax_box2:,.2f}")
    st.write(f"Box 3 tax (wealth): €{tax_box3:,.2f}")

    st.subheader("Totals & Rates")
    st.write(f"Total tax (Box1 + Box2 + Box3): €{total_tax_all:,.2f}")
    st.write(f"Net cash income (gross Box1 + Box2 − Box1 tax − Box2 tax): €{net_income_cash:,.2f}")
    st.write(f"Effective tax rate (including Box3 tax): {effective_tax_rate*100:.2f}%")

    # --------------------------
    # Charts (Streamlit-native)
    # --------------------------
    st.subheader("Tax Contribution per Box")
    df_tax = pd.DataFrame({
        "Box": ["Box 1", "Box 2", "Box 3"],
        "Tax (€)": [tax_box1_final, tax_box2, tax_box3],
    }).set_index("Box")
    st.bar_chart(df_tax)

    st.subheader("Share of Taxes by Box (stacked view)")
    df_stack = pd.DataFrame([[tax_box1_final, tax_box2, tax_box3]], columns=["Box 1", "Box 2", "Box 3"])
    st.bar_chart(df_stack)

    st.write("---")
    st.caption("This model approximates Dutch 2025 rules (EWF, hillen, caps, etc.). Use as an estimator, not official tax advice.")

