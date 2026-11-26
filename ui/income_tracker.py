"""Income tracking module supporting SQLite persistence, CSV logging, record editing, and line charts."""

import os
import sys
import csv
import tkinter as tk
from tkinter import Label, Entry, Button, messagebox
from datetime import date
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database.db_manager import get_connection, init_db

DATA_DIR = (
    os.path.dirname(sys.executable)
    if getattr(sys, "frozen", False)
    else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
)
CSV_PATH = os.path.join(DATA_DIR, "monthly_income.csv")


class IncomeTracker:
    """Tkinter interface for logging, editing, and plotting income transactions."""

    def __init__(self, master):
        """Build the Income Tracker window and initialize database connectivity."""
        init_db()
        self.master = master
        self.menu_window = tk.Toplevel(self.master)
        self.menu_window.title("Income Tracker")
        self.canvas_widget = None

        self.label = Label(self.menu_window, text="Manual Income History")
        self.label.pack()

        self.labelEnterHistory = Label(self.menu_window, text="Enter Income: ")
        self.labelEnterHistory.pack()

        self.entry_ = Entry(self.menu_window)
        self.entry_.pack()

        self.updateButton = Button(self.menu_window, text="Update", command=self.updateIncome)
        self.updateButton.pack()

        self.buttonEdit = Button(self.menu_window, text="Edit History", command=self.editIncome)
        self.buttonEdit.pack()

        self.button1 = Button(self.menu_window, text="Generate Graph", command=self.generateOnButton)
        self.button1.pack()

    def updateIncome(self):
        """Validate and save a new income entry to both SQLite and monthly_income.csv."""
        raw_val = self.entry_.get().strip()
        try:
            income = float(raw_val)
        except ValueError:
            messagebox.showerror("Error", "Please enter a numeric income value.", parent=self.menu_window)
            return

        current_date = date.today().strftime("%d-%m-%Y")

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT category_id FROM categories WHERE name = 'Salary'")
        row = c.fetchone()
        cat_id = row[0] if row else 7
        c.execute(
            """INSERT INTO transactions
               (user_id, category_id, title, amount, transaction_type, transaction_date)
               VALUES (1, ?, 'Manual Income Entry', ?, 'income', ?)""",
            (cat_id, income, current_date),
        )
        conn.commit()
        conn.close()

        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([income, current_date])

        self.entry_.delete(0, tk.END)
        messagebox.showinfo("Saved", f"Added income £{income:.2f} on {current_date}", parent=self.menu_window)

    def generateGraph(self):
        """Query income records from SQLite and return a Seaborn/Matplotlib line-chart Figure."""
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            """SELECT amount, transaction_date
               FROM transactions
               WHERE transaction_type = 'income'"""
        )
        data = c.fetchall()
        conn.close()

        df = pd.DataFrame(data, columns=["income", "current_date"])
        df["current_date"] = pd.to_datetime(df["current_date"], format="%d-%m-%Y", errors="coerce")
        df.sort_values(by="current_date", inplace=True)

        fig, ax = plt.subplots(figsize=(6.5, 4))
        sns.lineplot(x=df["current_date"], y=df["income"], marker="o", ax=ax)
        ax.set_xlabel("Date")
        ax.set_ylabel("Income")
        ax.set_title("Income History")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        return fig

    def generateOnButton(self):
        """Embed the generated income history line graph inside the Tkinter window."""
        if self.canvas_widget is not None:
            self.canvas_widget.destroy()
        fig = self.generateGraph()
        canvas = FigureCanvasTkAgg(fig, master=self.menu_window)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack()

    def editIncome(self):
        """Open a dialog prompting for an income transaction ID to edit."""
        self.edit_window = tk.Toplevel(self.menu_window)
        self.edit_window.title("Edit Income")

        conn = get_connection()
        c = conn.cursor()
        c.execute(
            """SELECT transaction_id, amount, transaction_date
               FROM transactions
               WHERE transaction_type = 'income'
               ORDER BY transaction_id DESC LIMIT 5"""
        )
        recent = c.fetchall()
        conn.close()

        recent_text = "Recent Income IDs: " + ", ".join(
            [f"ID {r[0]} (£{r[1]:.2f} on {r[2]})" for r in recent]
        )
        tk.Label(self.edit_window, text=recent_text, wraplength=320).pack(pady=4)

        id_label = tk.Label(self.edit_window, text="Enter Income ID")
        id_label.pack()

        self.income_id_entry = tk.Entry(self.edit_window)
        self.income_id_entry.pack()

        edit_button = tk.Button(self.edit_window, text="Edit", command=self.editIncomeRecord)
        edit_button.pack()

    def editIncomeRecord(self):
        """Fetch the chosen income record and populate editable amount and date fields."""
        income_id = self.income_id_entry.get().strip()

        conn = get_connection()
        c = conn.cursor()
        c.execute(
            """SELECT amount, transaction_date
               FROM transactions
               WHERE transaction_id = ? AND transaction_type = 'income'""",
            (income_id,),
        )
        row = c.fetchone()
        conn.close()

        if row:
            income, current_date = row

            income_label = tk.Label(self.edit_window, text="Income:")
            income_label.pack()

            self.income_entry = tk.Entry(self.edit_window)
            self.income_entry.insert(tk.END, str(income))
            self.income_entry.pack()

            date_label = tk.Label(self.edit_window, text="Date:")
            date_label.pack()

            self.date_entry = tk.Entry(self.edit_window)
            self.date_entry.insert(tk.END, current_date)
            self.date_entry.pack()

            update_button = tk.Button(
                self.edit_window, text="Update", command=lambda: self.updateIncomeRecord(income_id)
            )
            update_button.pack()
        else:
            messagebox.showerror("Error", "Income record with ID not found.", parent=self.edit_window)

    def updateIncomeRecord(self, income_id):
        """Commit updated amount and date values for an existing income record in SQLite."""
        new_income = float(self.income_entry.get())
        new_date = self.date_entry.get().strip()

        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE transactions SET amount = ?, transaction_date = ? WHERE transaction_id = ?",
            (new_income, new_date, income_id),
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Income record updated.", parent=self.edit_window)
        self.edit_window.destroy()
