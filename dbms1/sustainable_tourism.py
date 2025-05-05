import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import dashboard

class SustainableTourism:
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
        self.root.title("🌍 Sustainable Tourism")
        self.root.geometry("950x500")
        self.root.configure(bg="white")
        self.setup_ui()
        self.load_data()
        self.root.mainloop()

    def setup_ui(self):
        tk.Label(self.root, text="🌍 Sustainable Tourism", font=("Arial", 18, "bold"), bg="white", fg="#16a085").pack(pady=10)

        form = tk.Frame(self.root, bg="white")
        form.pack(pady=5)

        tk.Label(form, text="Program Name", bg="white").grid(row=0, column=0, padx=10, pady=5)
        self.name_entry = ttk.Entry(form, width=30)
        self.name_entry.grid(row=0, column=1)

        tk.Label(form, text="Description", bg="white").grid(row=0, column=2, padx=10)
        self.desc_entry = ttk.Entry(form, width=40)
        self.desc_entry.grid(row=0, column=3)

        tk.Label(form, text="Start Date (YYYY-MM-DD)", bg="white").grid(row=1, column=0, padx=10)
        self.start_entry = ttk.Entry(form)
        self.start_entry.grid(row=1, column=1)

        tk.Label(form, text="End Date (YYYY-MM-DD)", bg="white").grid(row=1, column=2)
        self.end_entry = ttk.Entry(form)
        self.end_entry.grid(row=1, column=3)

        ttk.Button(form, text="➕ Add Program", command=self.add_program).grid(row=2, column=1, pady=10)
        ttk.Button(form, text="❌ Delete Selected", command=self.delete_program).grid(row=2, column=2)

        # Table
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Description", "Start", "End"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, pady=10)

        # Back Button
        back_btn = tk.Button(self.root, text="⬅ Back to Dashboard", command=self.back_to_dashboard, bg="#2c3e50", fg="white")
        back_btn.pack(pady=10)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute("SELECT * FROM Sustainable_Tourism")
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def add_program(self):
        name = self.name_entry.get()
        desc = self.desc_entry.get()
        start = self.start_entry.get()
        end = self.end_entry.get()

        if not all([name, desc, start, end]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            self.cursor.execute("""
                INSERT INTO Sustainable_Tourism (program_name, description, start_date, end_date)
                VALUES (%s, %s, %s, %s)
            """, (name, desc, start, end))
            self.conn.commit()
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Tourism program added successfully.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    def delete_program(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Delete Error", "Select a program to delete.")
            return
        tourism_id = self.tree.item(selected)['values'][0]
        confirm = messagebox.askyesno("Confirm", "Delete this tourism program?")
        if confirm:
            self.cursor.execute("DELETE FROM Sustainable_Tourism WHERE id = %s", (tourism_id,))
            self.conn.commit()
            self.load_data()

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)

    def back_to_dashboard(self):
        self.root.destroy()
        dashboard.Dashboard(self.username)
