"""Application settings and SQLite database status module."""

import tkinter as tk
from tkinter import Label, Button, messagebox
from database.db_manager import get_connection, seed_mock_data


class Settings:
    """Tkinter window showing active user details, SQLite record counts, and demo reset."""

    def __init__(self, master):
        """Initialize the Settings window and query current SQLite table counts."""
        self.master = master
        self.menu_window = tk.Toplevel(self.master)
        self.menu_window.title("Settings Page")
        self.menu_window.geometry("400x400")

        self.label = Label(self.menu_window, text="Settings Options:", font=("bold", 12))
        self.label.pack(pady=10)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM transactions")
        tx_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM goals")
        goal_count = c.fetchone()[0]
        conn.close()

        Label(self.menu_window, text="Active User: user123").pack(pady=5)
        Label(self.menu_window, text=f"SQLite Transactions Stored: {tx_count}").pack(pady=5)
        Label(self.menu_window, text=f"Active Financial Goals: {goal_count}").pack(pady=5)

        Button(self.menu_window, text="Reset Mock Database", command=self.reset_demo).pack(pady=15)

    def reset_demo(self):
        """Restore the SQLite database to its initial 1,200 seeded mock transactions."""
        conn = get_connection()
        seed_mock_data(conn, force=True)
        conn.close()
        messagebox.showinfo("Reset", "Database reset to 1,200 mock transactions.", parent=self.menu_window)
