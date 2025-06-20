import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
from datetime import datetime
import math

# === Database Setup ===
conn = sqlite3.connect("operations.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS operations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        operand1 REAL,
        operand2 REAL,
        operator TEXT,
        result REAL,
        timestamp TEXT
    )
''')
conn.commit()

# === Operation Function ===


def calculate(op):
    try:
        a = float(entry1.get())
        b = float(entry2.get()) if op not in ["√"] else 0

        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op == "*":
            result = a * b
        elif op == "/":
            if b == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            result = a / b
        elif op == "%":
            result = a % b
        elif op == "^":
            result = a ** b
        elif op == "√":
            if a < 0:
                raise ValueError("Cannot take square root of negative number")
            result = math.sqrt(a)
        elif op == "EMI":
            rate = b / (12 * 100)
            time = float(entry3.get())
            result = (a * rate * (1 + rate) ** time) / ((1 + rate) ** time - 1)
        elif op == "SI":
            time = float(entry3.get())
            result = (a * b * time) / 100
        elif op == "CI":
            time = float(entry3.get())
            result = a * ((1 + b / 100) ** time) - a
        else:
            raise ValueError("Unknown operator")

        result_var.set(f"Result: {result:.2f}")
        log_operation(a, b, op, result)
        update_history()

    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except ZeroDivisionError as zde:
        messagebox.showerror("Math Error", str(zde))

# === Log Operation to SQLite ===


def log_operation(a, b, op, result):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO operations (operand1, operand2, operator, result, timestamp) VALUES (?, ?, ?, ?, ?)",
                   (a, b, op, result, timestamp))
    conn.commit()

# === Generate Report ===


def generate_report():
    df = pd.read_sql_query("SELECT * FROM operations", conn)
    df.to_csv("report.csv", index=False)
    messagebox.showinfo("Report Generated", "Saved to report.csv")

# === History ===


def update_history():
    history_box.delete(0, tk.END)
    cursor.execute(
        "SELECT operand1, operator, operand2, result FROM operations ORDER BY id DESC LIMIT 10")
    for row in cursor.fetchall():
        a, op, b, res = row
        history_box.insert(tk.END, f"{a} {op} {b} = {res:.2f}")

# === Clear Fields ===


def clear_all():
    entry1.delete(0, tk.END)
    entry2.delete(0, tk.END)
    entry3.delete(0, tk.END)
    result_var.set("Result: ")

# === Dark Mode Toggle ===


def toggle_theme():
    current = style.theme_use()
    style.theme_use("default" if current == "alt" else "alt")


# === GUI Setup ===
root = tk.Tk()
root.title("💰 Finance Calculator")
root.geometry("450x520")
root.resizable(False, False)

style = ttk.Style()
if "alt" not in style.theme_names():
    style.theme_create("alt", parent="clam", settings={
        ".": {"configure": {"background": "#2e2e2e", "foreground": "white"}},
        "TLabel": {"configure": {"background": "#2e2e2e", "foreground": "white"}},
        "TButton": {"configure": {"background": "#444", "foreground": "white"}},
        "TEntry": {"configure": {"fieldbackground": "#3e3e3e", "foreground": "white"}}
    })

style.theme_use("default")

frame = ttk.Frame(root, padding=10)
frame.pack()

# Inputs
ttk.Label(frame, text="Operand 1 / Principal:").grid(row=0, column=0, sticky="e")
entry1 = ttk.Entry(frame, width=20)
entry1.grid(row=0, column=1, pady=5)

ttk.Label(frame, text="Operand 2 / Rate:").grid(row=1, column=0, sticky="e")
entry2 = ttk.Entry(frame, width=20)
entry2.grid(row=1, column=1, pady=5)

ttk.Label(frame, text="Time (months/years):").grid(row=2, column=0, sticky="e")
entry3 = ttk.Entry(frame, width=20)
entry3.grid(row=2, column=1, pady=5)

# Buttons Grid
btn_frame = ttk.Frame(root, padding=10)
btn_frame.pack()

buttons = [
    ("+", 0, 0), ("-", 0, 1), ("*", 0, 2), ("/", 0, 3),
    ("%", 1, 0), ("^", 1, 1), ("√", 1, 2), ("Clear", 1, 3),
    ("EMI", 2, 0), ("SI", 2, 1), ("CI", 2, 2)
]

for (text, r, c) in buttons:
    cmd = clear_all if text == "Clear" else lambda t=text: calculate(t)
    ttk.Button(btn_frame, text=text, command=cmd, width=8).grid(
        row=r, column=c, padx=4, pady=4)

# Result display
result_var = tk.StringVar(value="Result: ")
ttk.Label(root, textvariable=result_var, font=(
    "Arial", 12), foreground="blue").pack(pady=5)

# Report and Theme Buttons
ttk.Button(root, text="📄 Generate Report",
           command=generate_report).pack(pady=5)
ttk.Button(root, text="🌓 Toggle Theme", command=toggle_theme).pack(pady=5)

# History Box
ttk.Label(root, text="📜 History").pack()
history_box = tk.Listbox(root, height=8, width=50)
history_box.pack(padx=10, pady=5)

update_history()
root.mainloop()
