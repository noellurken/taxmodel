import tkinter as tk
from tkinter import messagebox

def calculate_net_income():
    try:
        gross = float(gross_entry.get())
        tax_rate = float(tax_entry.get())
        
        tax_amount = gross * (tax_rate / 100)
        net_income = gross - tax_amount
        
        result_label.config(text=f"Net Income: ${net_income:.2f}")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")

# App window
app = tk.Tk()
app.title("Net Income Calculator")
app.geometry("350x200")

# Widgets
tk.Label(app, text="Gross Income ($):").pack()
gross_entry = tk.Entry(app)
gross_entry.pack()

tk.Label(app, text="Tax Rate (%):").pack()
tax_entry = tk.Entry(app)
tax_entry.pack()

tk.Button(app, text="Calculate", command=calculate_net_income).pack(pady=10)

result_label = tk.Label(app, text="Net Income: $0.00", font=("Arial", 12, "bold"))
result_label.pack()

# Run
app.mainloop()
