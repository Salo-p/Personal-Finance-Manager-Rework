"""Central navigation menu connecting each dashboard button to its dedicated feature module."""

import tkinter as tk
from tkinter import Label, Button, NW, N, NE, W, CENTER, E

from ui.income_tracker import IncomeTracker
from ui.budget_overview import BudgetOverview
from ui.goals import GoalsApp
from ui.expense_tracker import ExpenseTracker
from ml.ml_model import Investments
from ui.settings import Settings


class OpenMenuWindow:
    """Main dashboard window routing each of the six buttons to its own module."""

    def __init__(self, master):
        """Create the Menu Page window and bind its close handler."""
        self.master = master
        self.menu_window = tk.Toplevel(self.master)
        self.menu_window.title("Menu Page")
        self.menu_window.geometry("400x400")
        self.menu_window.protocol("WM_DELETE_WINDOW", self.master.destroy)

        self.create_widgets()

    def launch_income_history(self):
        """Open the Income Tracker window (ui/income_tracker.py)."""
        IncomeTracker(self.menu_window)

    def launch_budget_page(self):
        """Open the Category Budget Overview window (ui/budget_overview.py)."""
        BudgetOverview(self.menu_window)

    def launch_goals(self):
        """Open the Financial Goals CRUD window (ui/goals.py)."""
        GoalsApp(tk.Toplevel(self.menu_window))

    def launch_expenses(self):
        """Open the Expense Tracker window (ui/expense_tracker.py)."""
        ExpenseTracker(self.menu_window)

    def launch_investment_pred(self):
        """Open the ML Investment Prediction line graph (ml/ml_model.py)."""
        investment_tracker = Investments(self.menu_window)
        investment_tracker.visualise_predictions()

    def launch_settings(self):
        """Open the Application Settings & Database Summary window (ui/settings.py)."""
        Settings(self.menu_window)

    def create_widgets(self):
        """Place labels and buttons for all six modules on the Menu Page."""
        income_lb = Label(self.menu_window, text="Click to income \nhistory:", font=("Helvetica", 8))
        income_lb.place(relx=0.05, rely=0.25, anchor=NW)

        income_btn = Button(
            self.menu_window, text="Income History", font=("Helvetica", 8), command=self.launch_income_history
        )
        income_btn.place(relx=0.025, rely=0.35, anchor=NW)

        budget_lb = Label(self.menu_window, text="Click to see set \nbudgets:", font=("Helvetica", 8))
        budget_lb.place(relx=0.5, rely=0.25, anchor=N)

        Button(
            self.menu_window, text="Budget History", font=("Helvetica", 8), command=self.launch_budget_page
        ).place(relx=0.5, rely=0.35, anchor=N)

        goals_lb = Label(self.menu_window, text="Click to see current \ngoals:", font=("Helvetica", 8))
        goals_lb.place(relx=0.95, rely=0.25, anchor=NE)

        goals_btn = Button(
            self.menu_window, text="Goals", font=("Helvetica", 8), command=self.launch_goals
        )
        goals_btn.place(relx=0.875, rely=0.35, anchor=NE)

        expense_lb = Label(self.menu_window, text="Click to see \nexpenses:", font=("Helvetica", 8))
        expense_lb.place(relx=0.05, rely=0.75, anchor=W)

        expense_btn = Button(
            self.menu_window, text="Expenses", font=("Helvetica", 8), command=self.launch_expenses
        )
        expense_btn.place(relx=0.035, rely=0.85, anchor=W)

        investment_lb = Label(self.menu_window, text="Click to see running \ninvestments:", font=("Helvetica", 8))
        investment_lb.place(relx=0.5, rely=0.75, anchor=CENTER)

        investment_btn = Button(
            self.menu_window, text="Investments", font=("Helvetica", 8), command=self.launch_investment_pred
        )
        investment_btn.place(relx=0.5, rely=0.85, anchor=CENTER)

        setting_lb = Label(self.menu_window, text="Click for settings: ", font=("Helvetica", 8))
        setting_lb.place(relx=0.95, rely=0.75, anchor=E)

        settings_btn = Button(
            self.menu_window, text="Settings", font=("Helvetica", 8), command=self.launch_settings
        )
        settings_btn.place(relx=0.905, rely=0.85, anchor=E)
