"""Machine learning investment forecasting module using scikit-learn LinearRegression."""

import os
import sys
import tkinter as tk
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

ROOT_DIR = (
    sys._MEIPASS
    if getattr(sys, "frozen", False)
    else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
MOCK_10K_CSV = os.path.join(ROOT_DIR, "database", "mock_financial_10k.csv")


class Investments:
    """Trains a LinearRegression model on 10,000 portfolio price records and plots predictions."""

    def __init__(self, master=None):
        """Load the 10,000-row financial dataset, train LinearRegression, and compute RMSE."""
        self.master = master
        self.df = pd.read_csv(MOCK_10K_CSV)
        self.df["Date"] = pd.to_datetime(self.df["Date"])
        self.df["DayOfYear"] = self.df["Date"].dt.dayofyear

        self.X = self.df[["DayOfYear", "Open", "Low", "Volume"]]
        self.y = self.df["High"]

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )

        self.model = LinearRegression()
        self.model.fit(self.X_train, self.y_train)

        self.train_predictions = self.model.predict(self.X_train)
        self.test_predictions = self.model.predict(self.X_test)

        self.train_rmse = np.sqrt(mean_squared_error(self.y_train, self.train_predictions))
        self.test_rmse = np.sqrt(mean_squared_error(self.y_test, self.test_predictions))
        print("Train RMSE:", round(self.train_rmse, 4))
        print("Test RMSE:", round(self.test_rmse, 4))

    def predict_all(self):
        """Generate predicted High prices across the full 10,000-record dataset."""
        return self.model.predict(self.X)

    def generateGraph(self):
        """Build a Seaborn/Matplotlib line graph comparing actual vs. predicted asset prices."""
        all_predictions = self.predict_all()
        plot_df = self.df.tail(150).copy()
        pred_tail = all_predictions[-150:]

        fig, ax = plt.subplots(figsize=(9, 4.6))
        sns.lineplot(x=plot_df["Date"], y=plot_df["High"], label="Actual High Price", ax=ax)
        sns.lineplot(
            x=plot_df["Date"],
            y=pred_tail,
            label="Predicted High Price (LinearRegression)",
            linestyle="--",
            ax=ax,
        )
        ax.set_xlabel("Date")
        ax.set_ylabel("Asset Price (£)")
        ax.set_title(f"Portfolio Asset Price Forecast (Test RMSE: {self.test_rmse:.2f})")
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig

    def visualise_predictions(self):
        """Display the model explanation banner and embedded line graph in a Tkinter window."""
        all_predictions = self.predict_all()
        latest_actual = float(self.df["High"].iloc[-1])
        latest_pred = float(all_predictions[-1])

        if self.master is None:
            fig = self.generateGraph()
            plt.show()
            return

        self.menu_window = tk.Toplevel(self.master)
        self.menu_window.title("Investment Price Prediction (Linear Regression)")

        summary_text = (
            "Portfolio Asset Forecast: Multiple Linear Regression trained on 10,000 records "
            "(features: Day of Year, Open, Low, Volume; 80/20 train-test split).\n"
            f"Latest Actual High: £{latest_actual:.2f}  |  Model Predicted High: £{latest_pred:.2f}  "
            f"|  Test RMSE: {self.test_rmse:.2f}"
        )
        tk.Label(
            self.menu_window,
            text=summary_text,
            justify=tk.CENTER,
            font=("Helvetica", 9),
            pady=8,
            padx=12,
        ).pack()

        fig = self.generateGraph()
        canvas = FigureCanvasTkAgg(fig, master=self.menu_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        button = tk.Button(self.menu_window, text="Quit", command=self.menu_window.destroy)
        button.pack(pady=6)


if __name__ == "__main__":
    inv = Investments()
    inv.visualise_predictions()
