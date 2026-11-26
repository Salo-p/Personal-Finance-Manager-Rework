"""Category budget overview module comparing aggregated SQLite spending against budget limits."""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from database.db_manager import get_connection, init_db


class BudgetOverview:
    """Window displaying category-level spending totals against adjustable annual budget targets."""

    DEFAULT_LIMITS = {
        "Food": 6000.0,
        "Transportation": 4000.0,
        "Entertainment": 3500.0,
        "Utilities": 5000.0,
        "Shopping": 4500.0,
        "Others": 3000.0,
    }

    def __init__(self, master):
        """Initialize the Budget History window and load category spending summaries."""
        init_db()
        self.master = master
        self.window = tk.Toplevel(self.master)
        self.window.title("Budget History & Category Limits")
        self.limits = dict(self.DEFAULT_LIMITS)

        self.create_widgets()
        self.refresh_summary()

    def create_widgets(self):
        """Build the category budget summary table and interactive controls."""
        header = tk.Label(
            self.window,
            text="Category Budget Summary (Aggregated from SQLite Transactions)",
            font=("Helvetica", 10, "bold"),
        )
        header.pack(pady=(10, 5), padx=10)

        columns = ("Category", "Transactions", "TotalSpent", "BudgetLimit", "Remaining")
        self.table = ttk.Treeview(self.window, columns=columns, show="headings", height=8)
        self.table.heading("Category", text="Category")
        self.table.heading("Transactions", text="Tx Count")
        self.table.heading("TotalSpent", text="Total Spent")
        self.table.heading("BudgetLimit", text="Budget Limit")
        self.table.heading("Remaining", text="Remaining")

        for col in columns:
            self.table.column(col, width=115, anchor="center")
        self.table.pack(padx=10, pady=5)

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=6)

        tk.Button(btn_frame, text="Adjust Selected Limit", command=self.adjust_limit).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh Summary", command=self.refresh_summary).pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.window, text="", fg="gray")
        self.status_label.pack(pady=(0, 8))

    def refresh_summary(self):
        """Query grouped expense totals per category from SQLite and update the table."""
        for item in self.table.get_children():
            self.table.delete(item)

        conn = get_connection()
        c = conn.cursor()
        c.execute(
            """SELECT c.name, COUNT(t.transaction_id), COALESCE(SUM(t.amount), 0)
               FROM categories c
               LEFT JOIN transactions t
                 ON c.category_id = t.category_id AND t.transaction_type = 'expense'
               WHERE c.type = 'expense'
               GROUP BY c.category_id, c.name
               ORDER BY SUM(t.amount) DESC"""
        )
        rows = c.fetchall()
        conn.close()

        grand_spent = 0.0
        for cat_name, tx_count, total_spent in rows:
            limit_val = self.limits.get(cat_name, 3000.0)
            remaining = limit_val - total_spent
            grand_spent += total_spent
            self.table.insert(
                "",
                tk.END,
                values=(
                    cat_name,
                    tx_count,
                    f"£{total_spent:,.2f}",
                    f"£{limit_val:,.2f}",
                    f"£{remaining:,.2f}",
                ),
            )

        self.status_label.config(text=f"Total Expense Spend Across All Categories: £{grand_spent:,.2f}")

    def adjust_limit(self):
        """Prompt the user to update the budget limit for the selected category."""
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Select Category", "Please select a category row first.", parent=self.window)
            return

        cat_name = self.table.item(selected[0])["values"][0]
        new_limit = simpledialog.askfloat(
            "Adjust Budget Limit",
            f"Enter new budget limit for {cat_name}:",
            initialvalue=self.limits.get(cat_name, 3000.0),
            parent=self.window,
        )
        if new_limit is not None:
            self.limits[cat_name] = new_limit
            self.refresh_summary()
