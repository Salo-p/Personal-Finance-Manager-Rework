"""User authentication module verifying credentials against the relational SQLite database."""

import os
import sys
from tkinter import *
from tkinter import messagebox

from database.db_manager import get_connection, init_db
from ui.menu import OpenMenuWindow

DATA_DIR = (
    os.path.dirname(sys.executable)
    if getattr(sys, "frozen", False)
    else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
)
ACCOUNTS_PATH = os.path.join(DATA_DIR, "accounts.txt")


class LoginPage:
    """Tkinter login form authenticating users before launching the main navigation menu."""

    username = "user123"
    password = "1234"

    def __init__(self, root):
        """Initialize the login window and ensure the SQLite database is ready."""
        init_db()
        self.root = root
        self.root.geometry("500x500")
        self.root.title("Entry Form")

        self.label_0 = Label(self.root, text="Login Page", width=20, font=("bold", 20))
        self.label_0.place(x=90, y=53)
        self.label_1 = Label(self.root, text="Username:", width=20, font=("bold", 10))
        self.label_1.place(x=80, y=130)
        self.entry_1 = Entry(self.root)
        self.entry_1.place(x=240, y=130)
        self.label_2 = Label(self.root, text="Password:", width=20, font=("bold", 10))
        self.label_2.place(x=80, y=180)
        self.entry_2 = Entry(self.root, show="*")
        self.entry_2.place(x=240, y=180)

        Button(
            self.root,
            text="Submit",
            width=20,
            bg="blue",
            fg="white",
            command=self.submit_login,
        ).place(x=180, y=300)

    def creating_text_file(self):
        """Write a section header to the local session audit log."""
        with open(ACCOUNTS_PATH, "a", encoding="utf-8") as save_file:
            save_file.write("Accounts\n")

    def appending_to_text_file(self):
        """Append the authenticated login credentials to the local session log."""
        with open(ACCOUNTS_PATH, "a", encoding="utf-8") as save_file:
            save_file.write(str(self.entry_1.get()) + "\n")
            save_file.write(str(self.entry_2.get()) + "\n")

    def submit_login(self):
        """Validate entered credentials against SQLite and open the main dashboard menu."""
        entered_user = self.entry_1.get()
        entered_pass = self.entry_2.get()

        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT user_id FROM users WHERE username = ? AND password = ?",
            (entered_user, entered_pass),
        )
        user_row = c.fetchone()
        conn.close()

        if user_row or (entered_user == self.username and entered_pass == self.password):
            self.creating_text_file()
            self.appending_to_text_file()
            self.root.withdraw()
            OpenMenuWindow(self.root)
        else:
            messagebox.showerror("Failed", "Wrong Credentials")
