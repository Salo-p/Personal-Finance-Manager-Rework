# Personal Finance Manager

Python-based desktop application for managing personal finances, tracking income and expenses, monitoring category budgets, setting financial goals, and forecasting portfolio asset prices using linear regression.

## Demo Login Credentials

- **Username:** `user123`
- **Password:** `1234`

## Architecture & Maintainability

The project follows a modular, separation-of-concerns package layout so each feature can be maintained, tested, or extended independently:

- **One Module per Dashboard Action:** `ui/menu.py` acts as a lightweight router, connecting each of the six dashboard buttons (`Income History`, `Budget History`, `Goals`, `Expenses`, `Investments`, and `Settings`) to its own standalone file.
- **Centralized Relational Data Layer:** `database/db_manager.py` encapsulates SQLite connection management, foreign-key enforcement (`PRAGMA foreign_keys = ON`), schema initialization, and mock data seeding across four normalized tables (`users`, `categories`, `transactions`, `goals`).
- **Decoupled Machine Learning Pipeline:** `ml/ml_model.py` isolates `scikit-learn` (`LinearRegression`) training and `Seaborn`/`Matplotlib` visualisation from the Tkinter UI widgets.

## Project Structure

```text
Personal-Finance-Manager/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── README.md
├── database/                  # Relational SQLite database & data access layer
│   ├── __init__.py
│   ├── db_manager.py          # Schema setup, foreign keys & 1,200-transaction seeder
│   ├── finance_manager.db     # Pre-seeded SQLite database
│   ├── monthly_income.csv     # CSV backup for manual income entries
│   ├── mock_financial_10k.csv # 10,000-record dataset for ML regression
│   └── accounts.txt           # Session audit log
├── ui/                        # Modular Tkinter user interface package
│   ├── __init__.py
│   ├── login.py               # LoginPage authentication window
│   ├── menu.py                # OpenMenuWindow central button router
│   ├── income_tracker.py      # Button 1: Income History (SQLite, CSV, edit & line chart)
│   ├── budget_overview.py     # Button 2: Budget History (SQL GROUP BY category spend vs limits)
│   ├── goals.py               # Button 3: Goals (CRUD operations on SQLite goals table)
│   ├── expense_tracker.py     # Button 4: Expenses (add, view & date-filter expenses)
│   └── settings.py            # Button 6: Settings (user info, DB counts & demo reset)
└── ml/                        # Machine learning package
    ├── __init__.py
    └── ml_model.py            # Button 5: Investments (LinearRegression & line graph)
```

## Setup and Execution

1. Extract the ZIP archive and open a terminal (PowerShell, Command Prompt, or Terminal) inside `Personal-Finance-Manager/`.
2. Install the required dependencies:
   ```text
   python -m pip install -r requirements.txt
   ```
3. Run the application:
   ```text
   python main.py
   ```
