import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import dashboard

class VolunteerApp:
    def __init__(self, username):
        self.username = username
        self.root = tk.Tk()
        self.root.title("Volunteers Management")
        self.root.geometry("950x600")
        self.root.configure(bg="white")

        # Connect to MySQL
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="11223344",
                database="WildGuardDB"
            )
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            self.root.destroy()
            return

        self.create_ui()
        self.load_data()
        self.root.mainloop()

    def create_ui(self):
        tk.Label(self.root, text="👥 Volunteer Management", font=("Arial", 20, "bold"), bg="white", fg="#2e8b57").pack(pady=15)

        # Form Frame
        form = tk.Frame(self.root, bg="white")
        form.pack()

        tk.Label(form, text="Name:", bg="white").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.name_entry = ttk.Entry(form, width=30)
        self.name_entry.grid(row=0, column=1, padx=10)

        tk.Label(form, text="Email:", bg="white").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.email_entry = ttk.Entry(form, width=30)
        self.email_entry.grid(row=1, column=1, padx=10)

        tk.Label(form, text="Phone:", bg="white").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.phone_entry = ttk.Entry(form, width=30)
        self.phone_entry.grid(row=2, column=1, padx=10)

        tk.Label(form, text="Availability:", bg="white").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.avail_entry = ttk.Entry(form, width=30)
        self.avail_entry.grid(row=3, column=1, padx=10)

        # Buttons
        btn_frame = tk.Frame(self.root, bg="white")
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Volunteer", command=self.add_volunteer).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_volunteer).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Back to Dashboard", command=self.back_to_dashboard).pack(side="left", padx=10)

        # Table
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Email", "Phone", "Availability"), show="headings", height=12)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Availability", text="Availability")
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=150)
        self.tree.column("Email", width=200)
        self.tree.column("Phone", width=100)
        self.tree.column("Availability", width=150)
        self.tree.pack(pady=15)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute("SELECT * FROM Volunteers")
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def add_volunteer(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        availability = self.avail_entry.get().strip()

        if not name or not email:
            messagebox.showwarning("Input Error", "Name and Email are required.")
            return

        try:
            self.cursor.execute(
                "INSERT INTO Volunteers (name, email, phone, availability) VALUES (%s, %s, %s, %s)",
                (name, email, phone, availability)
            )
            self.conn.commit()
            self.load_data()
            self.name_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.avail_entry.delete(0, tk.END)
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Email already exists.")

    def delete_volunteer(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Delete Error", "Please select a volunteer to delete.")
            return
        volunteer_id = self.tree.item(selected)["values"][0]
        self.cursor.execute("DELETE FROM Volunteers WHERE id = %s", (volunteer_id,))
        self.conn.commit()
        self.load_data()

    def back_to_dashboard(self):
        self.root.destroy()
        dashboard.Dashboard(self.username)

def run(username):
    VolunteerApp(username)
