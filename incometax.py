def calculate_net_income(gross_income, tax_rate):
    tax_amount = gross_income * (tax_rate / 100)
    net_income = gross_income - tax_amount
    return net_income

def main():
    print("Welcome to the Net Income Calculator!")
    gross_income = float(input("Enter your gross income: $"))
    tax_rate = float(input("Enter your tax rate (%): "))

    net = calculate_net_income(gross_income, tax_rate)
    print(f"\nYour net income after taxes is: ${net:.2f}")

if __name__ == "__main__":
    main()
