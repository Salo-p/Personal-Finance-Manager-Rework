"""Financial goals module providing SQLite-backed CRUD operations via Tkinter."""

import tkinter as tk
from tkinter import messagebox, simpledialog
from database.db_manager import get_connection, init_db


class GoalsApp:
    """Tkinter interface to view, add, edit, and delete personal financial goals."""

    def __init__(self, root):
        """Initialize the Goals window, buttons, and status indicator."""
        init_db()
        self.root = root
        self.root.title("Goals")
        self.goals = []

        self.goal_listbox = tk.Listbox(root, selectmode=tk.SINGLE, height=10, width=48)
        self.goal_listbox.pack(pady=10, padx=10)

        self.view_button = tk.Button(root, text="View Goals", command=self.view_goals)
        self.view_button.pack()

        self.add_button = tk.Button(root, text="Add Goal", command=self.add_goal)
        self.add_button.pack()

        self.edit_button = tk.Button(root, text="Edit Goal", command=self.edit_goal)
        self.edit_button.pack()

        self.delete_button = tk.Button(root, text="Delete Goal", command=self.delete_goal)
        self.delete_button.pack()

        self.status_label = tk.Label(root, text="", fg="gray")
        self.status_label.pack(pady=6)

        self.view_goals()

    def view_goals(self):
        """Reload all goals for the active user from SQLite and update the status label."""
        self.goal_listbox.delete(0, tk.END)
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT goal_id, goal_name, target_amount, target_date FROM goals WHERE user_id = 1")
        self.goals = c.fetchall()
        conn.close()
        for gid, goal_name, target_amount, target_date in self.goals:
            self.goal_listbox.insert(tk.END, f"{goal_name} - £{target_amount:.2f} (Target: {target_date})")
        self.status_label.config(text=f"Showing {len(self.goals)} active goal(s) from SQLite.")

    def add_goal(self):
        """Prompt for goal details and insert a new goal record into SQLite."""
        goal_name = simpledialog.askstring("Add Goal", "Enter your financial goal:", parent=self.root)
        target_amount = simpledialog.askfloat("Add Goal", "Enter the target amount:", parent=self.root)
        target_date = simpledialog.askstring("Add Goal", "Enter the target date (YYYY-MM-DD):", parent=self.root)

        if goal_name and target_amount is not None and target_date:
            conn = get_connection()
            c = conn.cursor()
            c.execute(
                "INSERT INTO goals (user_id, goal_name, target_amount, target_date) VALUES (1, ?, ?, ?)",
                (goal_name, target_amount, target_date),
            )
            conn.commit()
            conn.close()
            self.view_goals()

    def edit_goal(self):
        """Update the name of the currently selected financial goal in SQLite."""
        selected_index = self.goal_listbox.curselection()
        if selected_index:
            gid, old_name, old_amount, old_date = self.goals[selected_index[0]]
            edited_goal = simpledialog.askstring(
                "Edit Goal", "Edit your financial goal:", initialvalue=old_name, parent=self.root
            )
            if edited_goal:
                conn = get_connection()
                c = conn.cursor()
                c.execute("UPDATE goals SET goal_name = ? WHERE goal_id = ?", (edited_goal, gid))
                conn.commit()
                conn.close()
                self.view_goals()
        else:
            messagebox.showinfo("Edit Goal", "Please select a goal to edit.", parent=self.root)

    def delete_goal(self):
        """Delete the selected goal from SQLite after user confirmation."""
        selected_index = self.goal_listbox.curselection()
        if selected_index:
            confirmation = messagebox.askyesno(
                "Delete Goal", "Are you sure you want to delete this goal?", parent=self.root
            )
            if confirmation:
                gid = self.goals[selected_index[0]][0]
                conn = get_connection()
                c = conn.cursor()
                c.execute("DELETE FROM goals WHERE goal_id = ?", (gid,))
                conn.commit()
                conn.close()
                self.view_goals()
        else:
            messagebox.showinfo("Delete Goal", "Please select a goal to delete.", parent=self.root)


if __name__ == "__main__":
    root = tk.Tk()
    app = GoalsApp(root)
    root.mainloop()
