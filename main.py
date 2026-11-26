"""Application entry point for the Personal Finance Manager."""

from tkinter import Tk
from ui.login import LoginPage


def main():
    """Initialize the root Tkinter window and launch the LoginPage."""
    root = Tk()
    LoginPage(root)
    root.mainloop()


if __name__ == "__main__":
    main()
