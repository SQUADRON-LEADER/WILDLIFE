import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import importlib  # Use importlib instead of direct import

class VolunteerProjects:
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
        self.root.title("Volunteer Project Assignments")
        self.root.geometry("850x500")
        self.setup_ui()
        self.load_data()
        self.root.mainloop()

    def setup_ui(self):
        title = tk.Label(self.root, text="🤝 Volunteer Project Assignments", font=("Arial", 18, "bold"), pady=10)
        title.pack()

        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Volunteer ID:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(form_frame, text="Project ID:").grid(row=0, column=2, padx=5, pady=5)

        self.volunteer_id_entry = ttk.Entry(form_frame)
        self.project_id_entry = ttk.Entry(form_frame)

        self.volunteer_id_entry.grid(row=0, column=1, padx=5, pady=5)
        self.project_id_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(form_frame, text="Assign", command=self.add_assignment, bg="#1abc9c", fg="white").grid(row=0, column=4, padx=10)
        tk.Button(form_frame, text="Delete", command=self.delete_assignment, bg="#e74c3c", fg="white").grid(row=0, column=5)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Volunteer", "Project", "Date"), show='headings')
        self.tree.heading("ID", text="Assignment ID")
        self.tree.heading("Volunteer", text="Volunteer ID")
        self.tree.heading("Project", text="Project ID")
        self.tree.heading("Date", text="Assigned Date")
        self.tree.pack(fill="both", expand=True, pady=10)

        back_btn = tk.Button(self.root, text="⬅ Back to Dashboard", command=self.back_to_dashboard, bg="#34495e", fg="white")
        back_btn.pack(pady=10)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute("SELECT id, volunteer_id, project_id, assigned_date FROM Volunteer_Projects")
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def add_assignment(self):
        volunteer_id = self.volunteer_id_entry.get()
        project_id = self.project_id_entry.get()

        if not volunteer_id or not project_id:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            self.cursor.execute(
                "INSERT INTO Volunteer_Projects (volunteer_id, project_id, assigned_date) VALUES (%s, %s, CURDATE())",
                (volunteer_id, project_id)
            )
            self.conn.commit()
            messagebox.showinfo("Success", "Volunteer assigned successfully!")
            self.load_data()
            self.volunteer_id_entry.delete(0, tk.END)
            self.project_id_entry.delete(0, tk.END)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    def delete_assignment(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select a record", "Please select a record to delete.")
            return

        assignment_id = self.tree.item(selected)['values'][0]
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this assignment?")
        if confirm:
            self.cursor.execute("DELETE FROM Volunteer_Projects WHERE id = %s", (assignment_id,))
            self.conn.commit()
            self.load_data()

    def back_to_dashboard(self):
        self.root.destroy()
        dashboard_module = importlib.import_module("dashboard")
        dashboard_module.Dashboard(self.username)

