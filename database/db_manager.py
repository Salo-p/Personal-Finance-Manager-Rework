"""Relational SQLite database manager with foreign-key enforcement and mock data seeding."""

import os
import sys
import sqlite3
import random
from datetime import datetime, timedelta

BASE_DIR = (
    os.path.dirname(sys.executable)
    if getattr(sys, "frozen", False)
    else os.path.dirname(os.path.abspath(__file__))
)
DB_PATH = os.path.join(BASE_DIR, "finance_manager.db")


def get_connection():
    """Return a SQLite connection with foreign-key referential integrity enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Create normalized database tables and seed default user, categories, and mock records."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT CHECK(type IN ('expense', 'income')) NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_type TEXT CHECK(transaction_type IN ('expense', 'income')) NOT NULL,
            transaction_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            goal_name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            target_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # Default demo user
    c.execute(
        "INSERT OR IGNORE INTO users (user_id, username, password, age) VALUES (1, 'user123', '1234', 24)"
    )

    default_categories = [
        ("Food", "expense"),
        ("Transportation", "expense"),
        ("Entertainment", "expense"),
        ("Utilities", "expense"),
        ("Shopping", "expense"),
        ("Others", "expense"),
        ("Salary", "income"),
        ("Freelance", "income"),
        ("Investments", "income"),
    ]
    c.executemany(
        "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
        default_categories,
    )

    conn.commit()
    seed_mock_data(conn)
    conn.close()


def seed_mock_data(conn, force=False):
    """Populate 1,200 realistic transactions and starter goals if the database is empty or reset."""
    c = conn.cursor()
    if force:
        c.execute("DELETE FROM transactions")
        c.execute("DELETE FROM goals")

    c.execute("SELECT COUNT(*) FROM transactions")
    if c.fetchone()[0] >= 1000:
        return

    c.execute("SELECT category_id, name, type FROM categories")
    cat_rows = c.fetchall()
    expense_cats = [(cid, name) for cid, name, ctype in cat_rows if ctype == "expense"]
    income_cats = [(cid, name) for cid, name, ctype in cat_rows if ctype == "income"]

    sample_titles = {
        "Food": ["Supermarket Groceries", "Lunch Cafe", "Dinner Takeaway", "Coffee Shop"],
        "Transportation": ["Train Pass", "Fuel Top-Up", "Uber Ride", "Bus Ticket"],
        "Entertainment": ["Cinema Tickets", "Streaming Subscription", "Concert", "Books"],
        "Utilities": ["Electricity Bill", "Water Bill", "Broadband Internet", "Mobile Plan"],
        "Shopping": ["Clothing Store", "Electronics", "Home Supplies", "Online Order"],
        "Others": ["Pharmacy", "Gym Membership", "Gift", "Misc Expense"],
        "Salary": ["Monthly Payroll", "Bi-Weekly Salary"],
        "Freelance": ["Consulting Invoice", "Web Project"],
        "Investments": ["Dividend Payout", "ETF Return"],
    }

    random.seed(42)
    records = []
    start_date = datetime.today() - timedelta(days=365)

    for i in range(1200):
        tx_date = (start_date + timedelta(days=random.randint(0, 365))).strftime("%d-%m-%Y")
        if i % 12 == 0:
            cid, cname = random.choice(income_cats)
            tx_type = "income"
            amount = round(random.uniform(800.0, 3200.0), 2)
        else:
            cid, cname = random.choice(expense_cats)
            tx_type = "expense"
            amount = round(random.uniform(6.5, 220.0), 2)
        title = random.choice(sample_titles.get(cname, [cname]))
        records.append((1, cid, title, amount, tx_type, tx_date))

    c.executemany(
        """INSERT INTO transactions
           (user_id, category_id, title, amount, transaction_type, transaction_date)
           VALUES (?, ?, ?, ?, ?, ?)""",
        records,
    )

    sample_goals = [
        (1, "Emergency Fund", 5000.0, "2026-12-31"),
        (1, "Summer Holiday", 1800.0, "2026-08-15"),
        (1, "New Laptop", 1200.0, "2026-10-01"),
    ]
    c.executemany(
        "INSERT OR IGNORE INTO goals (user_id, goal_name, target_amount, target_date) VALUES (?, ?, ?, ?)",
        sample_goals,
    )
    conn.commit()
