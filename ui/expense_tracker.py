"""Expense tracking module for adding, viewing, and date-filtering relational SQLite expenses."""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta, date
from database.db_manager import get_connection, init_db


class ExpenseTracker:
    """Tkinter window for recording expenses, managing categories, and filtering history."""

    def __init__(self, master):
        """Initialize the Expense Tracker window and load existing transactions."""
        init_db()
        self.master = master
        self.menu_window = tk.Toplevel(self.master)
        self.menu_window.title("Expense Tracker")

        self.expenses = []
        self.categories = self._fetch_categories()

        self.create_widgets()
        self.view_expenses()

    def _fetch_categories(self):
        """Retrieve all expense category names from SQLite."""
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT name FROM categories WHERE type = 'expense' ORDER BY category_id")
        cats = [row[0] for row in c.fetchall()]
        conn.close()
        return cats

    def _load_expenses_from_db(self):
        """Query expense transactions joined with their category names from SQLite."""
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            """SELECT t.title, t.amount, t.transaction_date, c.name
               FROM transactions t
               JOIN categories c ON t.category_id = c.category_id
               WHERE t.transaction_type = 'expense'
               ORDER BY t.transaction_id DESC"""
        )
        rows = c.fetchall()
        conn.close()
        self.expenses = rows
        return rows

    def create_widgets(self):
        """Create entry fields, category selector, filter controls, and expense Treeview."""
        self.expense_label = tk.Label(self.menu_window, text="Enter Expense:")
        self.expense_label.grid(row=0, column=0, padx=5, pady=5)
        self.expense_entry = tk.Entry(self.menu_window)
        self.expense_entry.grid(row=0, column=1, padx=5, pady=5)

        self.amount_label = tk.Label(self.menu_window, text="Enter Amount:")
        self.amount_label.grid(row=1, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(self.menu_window)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        self.date_label = tk.Label(self.menu_window, text="Enter Date (DD-MM-YYYY):")
        self.date_label.grid(row=2, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(self.menu_window)
        self.date_entry.insert(0, date.today().strftime("%d-%m-%Y"))
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        self.category_label = tk.Label(self.menu_window, text="Select Category:")
        self.category_label.grid(row=3, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar(value=self.categories[0] if self.categories else "Food")
        self.category_dropdown = ttk.Combobox(
            self.menu_window, textvariable=self.category_var, values=self.categories
        )
        self.category_dropdown.grid(row=3, column=1, padx=5, pady=5)

        self.add_category_button = tk.Button(self.menu_window, text="Add Category", command=self.add_category)
        self.add_category_button.grid(row=3, column=2, padx=5, pady=5)

        self.add_button = tk.Button(self.menu_window, text="Add Expense", command=self.add_expense)
        self.add_button.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="we")

        self.view_button = tk.Button(self.menu_window, text="View Expenses", command=self.view_expenses)
        self.view_button.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="we")

        self.filter_label = tk.Label(self.menu_window, text="Filter Expenses:")
        self.filter_label.grid(row=6, column=0, padx=5, pady=5)
        self.filter_var = tk.StringVar(value="All")
        self.filter_dropdown = ttk.Combobox(
            self.menu_window, textvariable=self.filter_var, values=["All", "Past Week", "Past Month"]
        )
        self.filter_dropdown.grid(row=6, column=1, padx=5, pady=5)
        self.filter_button = tk.Button(self.menu_window, text="Filter", command=self.filter_expenses)
        self.filter_button.grid(row=6, column=2, padx=5, pady=5)

        self.table = ttk.Treeview(self.menu_window, columns=("Expense", "Amount", "Date", "Category"))
        self.table.heading("#0", text="ID")
        self.table.heading("Expense", text="Expense")
        self.table.heading("Amount", text="Amount")
        self.table.heading("Date", text="Date")
        self.table.heading("Category", text="Category")
        self.table.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

        self.status_label = tk.Label(self.menu_window, text="", fg="gray")
        self.status_label.grid(row=8, column=0, columnspan=3, pady=(0, 6))

    def add_category(self):
        """Prompt for a new category name and insert it into the SQLite categories table."""
        new_category = simpledialog.askstring("Add Category", "Enter new category:", parent=self.menu_window)
        if new_category:
            conn = get_connection()
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO categories (name, type) VALUES (?, 'expense')", (new_category,))
            conn.commit()
            conn.close()
            self.categories = self._fetch_categories()
            self.category_dropdown["values"] = self.categories
            self.category_var.set(new_category)

    def add_expense(self):
        """Validate form inputs and insert a new expense transaction into SQLite."""
        expense = self.expense_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        tx_date = self.date_entry.get().strip() or date.today().strftime("%d-%m-%Y")
        category = self.category_var.get() or "Others"

        if not expense or not amount_str:
            messagebox.showerror("Error", "Please enter an expense title and amount.", parent=self.menu_window)
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.", parent=self.menu_window)
            return

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT category_id FROM categories WHERE name = ?", (category,))
        row = c.fetchone()
        cat_id = row[0] if row else 1
        c.execute(
            """INSERT INTO transactions
               (user_id, category_id, title, amount, transaction_type, transaction_date)
               VALUES (1, ?, ?, ?, 'expense', ?)""",
            (cat_id, expense, amount, tx_date),
        )
        conn.commit()
        conn.close()

        self.expense_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.view_expenses()

    def view_expenses(self):
        """Reset active filters, reload all expenses from SQLite, and update the status bar."""
        self.filter_var.set("All")
        self._load_expenses_from_db()
        for item in self.table.get_children():
            self.table.delete(item)

        for i, (expense, amount, tx_date, category) in enumerate(self.expenses, start=1):
            self.table.insert("", tk.END, text=str(i), values=(expense, f"£{amount:.2f}", tx_date, category))

        self.status_label.config(text=f"Showing all {len(self.expenses)} expense records from SQLite.")

    def filter_expenses(self):
        """Dispatch table filtering based on the selected date window."""
        filter_option = self.filter_var.get()
        if filter_option == "Past Week":
            self.view_expenses_past_week()
        elif filter_option == "Past Month":
            self.view_expenses_past_month()
        else:
            self.view_expenses()

    def view_expenses_past_week(self):
        """Display only expenses dated within the last 7 days."""
        self._load_expenses_from_db()
        for item in self.table.get_children():
            self.table.delete(item)

        today = datetime.today()
        idx = 1
        for expense, amount, tx_date, category in self.expenses:
            expense_date = datetime.strptime(tx_date, "%d-%m-%Y")
            if today - timedelta(days=7) <= expense_date <= today:
                self.table.insert("", tk.END, text=str(idx), values=(expense, f"£{amount:.2f}", tx_date, category))
                idx += 1
        self.status_label.config(text=f"Filtered: {idx - 1} expense(s) in the past 7 days.")

    def view_expenses_past_month(self):
        """Display only expenses dated within the last 30 days."""
        self._load_expenses_from_db()
        for item in self.table.get_children():
            self.table.delete(item)

        today = datetime.today()
        idx = 1
        for expense, amount, tx_date, category in self.expenses:
            expense_date = datetime.strptime(tx_date, "%d-%m-%Y")
            if today - timedelta(days=30) <= expense_date <= today:
                self.table.insert("", tk.END, text=str(idx), values=(expense, f"£{amount:.2f}", tx_date, category))
                idx += 1
        self.status_label.config(text=f"Filtered: {idx - 1} expense(s) in the past 30 days.")
