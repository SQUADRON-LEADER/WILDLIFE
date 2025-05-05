import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import dashboard

class WildlifePatrol:
    def __init__(self, username):
        self.username = username
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="11223344",
            database="WildGuardDB"
        )
        self.cursor = self.conn.cursor()
        self.root = tk.Tk()
        self.root.title("🦺 Wildlife Patrol Management")
        self.root.geometry("900x500")
        self.root.configure(bg="white")
        self.setup_ui()
        self.load_data()
        self.root.mainloop()

    def setup_ui(self):
        title = tk.Label(self.root, text="🦺 Wildlife Patrol Management", font=("Arial", 18, "bold"), fg="#1e8449", bg="white")
        title.pack(pady=10)

        form = tk.Frame(self.root, bg="white")
        form.pack(pady=10)

        tk.Label(form, text="Patrol Name", bg="white").grid(row=0, column=0, padx=5, pady=5)
        self.patrol_name_entry = ttk.Entry(form)
        self.patrol_name_entry.grid(row=0, column=1, padx=5)

        tk.Label(form, text="Start Date (YYYY-MM-DD)", bg="white").grid(row=0, column=2, padx=5)
        self.start_entry = ttk.Entry(form)
        self.start_entry.grid(row=0, column=3, padx=5)

        tk.Label(form, text="End Date (YYYY-MM-DD)", bg="white").grid(row=1, column=0, padx=5)
        self.end_entry = ttk.Entry(form)
        self.end_entry.grid(row=1, column=1, padx=5)

        tk.Label(form, text="Status", bg="white").grid(row=1, column=2, padx=5)
        self.status_entry = ttk.Entry(form)
        self.status_entry.grid(row=1, column=3, padx=5)

        ttk.Button(form, text="Add Patrol", command=self.add_patrol).grid(row=2, column=1, pady=10)
        ttk.Button(form, text="Delete Selected", command=self.delete_patrol).grid(row=2, column=2, pady=10)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Start", "End", "Status"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Patrol Name")
        self.tree.heading("Start", text="Start Date")
        self.tree.heading("End", text="End Date")
        self.tree.heading("Status", text="Status")
        self.tree.pack(pady=10, fill="both", expand=True)

        back_btn = tk.Button(self.root, text="⬅ Back to Dashboard", command=self.back_to_dashboard, bg="#2c3e50", fg="white")
        back_btn.pack(pady=10)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute("SELECT * FROM Wildlife_Patrol")
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def add_patrol(self):
        name = self.patrol_name_entry.get()
        start = self.start_entry.get()
        end = self.end_entry.get()
        status = self.status_entry.get()

        if not all([name, start, end, status]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            self.cursor.execute(
                "INSERT INTO Wildlife_Patrol (patrol_name, start_date, end_date, status) VALUES (%s, %s, %s, %s)",
                (name, start, end, status)
            )
            self.conn.commit()
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Patrol added successfully.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to insert data: {err}")

    def delete_patrol(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Delete Error", "Please select a patrol to delete.")
            return
        patrol_id = self.tree.item(selected)['values'][0]
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this patrol?")
        if confirm:
            self.cursor.execute("DELETE FROM Wildlife_Patrol WHERE id = %s", (patrol_id,))
            self.conn.commit()
            self.load_data()

    def clear_fields(self):
        self.patrol_name_entry.delete(0, tk.END)
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)
        self.status_entry.delete(0, tk.END)

    def back_to_dashboard(self):
        self.root.destroy()
        dashboard.Dashboard(self.username)
