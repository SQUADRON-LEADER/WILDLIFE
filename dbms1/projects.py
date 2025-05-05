import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import dashboard

def run(username):
    root = tk.Tk()
    root.title("🌿 WildGuard - Conservation Projects")
    root.geometry("1000x680")  # Increased height to ensure footer is visible
    
    # Modern color scheme
    colors = {
        "primary": "#2E7D32",      # Forest green
        "secondary": "#4CAF50",    # Lighter green
        "accent": "#FF9800",       # Orange
        "background": "#F8F9FA",   # Light gray background
        "card": "#FFFFFF",         # White for cards
        "text": "#212121",         # Dark gray text
        "text_secondary": "#757575", # Medium gray text
        "delete": "#F44336",       # Red for delete
        "divider": "#EEEEEE",      # Light gray divider
        "button_text": "#FFFFFF",  # White text on buttons
    }
    
    # Configure the root window
    root.config(bg=colors["background"])
    
    # Configure styles
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure Treeview style
    style.configure("modern.Treeview",
                   background="white",
                   foreground=colors["text"],
                   rowheight=30,
                   fieldbackground="white",
                   font=('Arial', 10))
                   
    style.configure("modern.Treeview.Heading",
                   background=colors["primary"],
                   foreground="white",
                   font=('Arial', 11, 'bold'),
                   padding=8)
                   
    style.map("modern.Treeview",
             background=[('selected', colors["secondary"])],
             foreground=[('selected', 'white')])
    
    # Setup database connection
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="11223344",
        database="WildGuardDB"
    )
    cursor = conn.cursor()
    
    # ===== FUNCTIONS =====
    
    # Load all project data
    def load_data():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("SELECT id, name, status, description FROM Projects")
        
        # Add alternating row colors and status-based styling
        for i, row in enumerate(cursor.fetchall()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            
            # Add status-based tag
            status = row[2].lower() if row[2] else ""
            if "active" in status:
                status_tag = "active"
            elif "completed" in status:
                status_tag = "completed"
            elif "cancelled" in status or "canceled" in status:
                status_tag = "cancelled"
            else:
                status_tag = "normal"
                
            tree.insert("", "end", values=row, tags=(tag, status_tag))
        
        # Configure tag colors
        tree.tag_configure("evenrow", background="#FFFFFF")
        tree.tag_configure("oddrow", background="#F5F5F5")
        tree.tag_configure("active", foreground="#388E3C")  # Green
        tree.tag_configure("completed", foreground="#1976D2") # Blue
        tree.tag_configure("cancelled", foreground="#D32F2F") # Red
        tree.tag_configure("normal", foreground=colors["text"])

    # Add a new project
    def add_project():
        name = entry_name.get().strip()
        status = status_var.get() if status_dropdown else entry_status.get().strip()
        desc = entry_desc.get("1.0", tk.END).strip() if isinstance(entry_desc, tk.Text) else entry_desc.get().strip()

        if not name:
            messagebox.showwarning("Input Error", "Project name is required.")
            return
            
        if not status:
            messagebox.showwarning("Input Error", "Status is required.")
            return

        try:
            cursor.execute(
                "INSERT INTO Projects (name, status, description) VALUES (%s, %s, %s)",
                (name, status, desc)
            )
            conn.commit()
            messagebox.showinfo("Success", "Project added successfully!")
            
            # Clear form fields
            entry_name.delete(0, tk.END)
            
            if status_dropdown:
                status_var.set(status_options[0])
            else:
                entry_status.delete(0, tk.END)
                
            if isinstance(entry_desc, tk.Text):
                entry_desc.delete("1.0", tk.END)
            else:
                entry_desc.delete(0, tk.END)
                
            # Refresh data
            load_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add project: {e}")

    # Delete selected project
    def delete_project():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a project to delete.")
            return
            
        # Get project details
        values = tree.item(selected)["values"]
        proj_id = values[0]
        proj_name = values[1]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete project '{proj_name}'?"
        )
        
        if confirm:
            try:
                cursor.execute("DELETE FROM Projects WHERE id = %s", (proj_id,))
                conn.commit()
                load_data()
                messagebox.showinfo("Success", "Project deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete project: {e}")

    # Return to Dashboard
    def back_to_dashboard():
        root.destroy()
        dashboard.Dashboard(username=username)
    
    # ===== UI COMPONENTS =====
    
    # === HEADER SECTION ===
    header_frame = tk.Frame(root, bg=colors["primary"], height=70)
    header_frame.pack(fill="x")
    
    # Add subtle shadow effect
    shadow_frame = tk.Frame(root, bg="#1B5E20", height=5)
    shadow_frame.pack(fill="x")
    
    # Header title
    header_label = tk.Label(
        header_frame,
        text="🌿 Conservation Projects",
        font=("Arial", 18, "bold"),
        bg=colors["primary"],
        fg="white",
        pady=20
    )
    header_label.pack(side="left", padx=20)
    
    # User welcome
    user_label = tk.Label(
        header_frame,
        text=f"Welcome, {username}",
        font=("Arial", 10),
        bg=colors["primary"],
        fg="white"
    )
    user_label.pack(side="right", padx=20)
    
    # === MAIN CONTENT ===
    content_frame = tk.Frame(root, bg=colors["background"], padx=20, pady=20)
    content_frame.pack(fill="both", expand=True)
    
    # === FORM SECTION ===
    form_card = tk.Frame(
        content_frame, 
        bg=colors["card"], 
        padx=20, 
        pady=20,
        bd=1, 
        relief="solid"
    )
    form_card.pack(fill="x", pady=(0, 20))
    
    # Form title
    form_title = tk.Label(
        form_card,
        text="Add New Project",
        font=("Arial", 14, "bold"),
        bg=colors["card"],
        fg=colors["primary"]
    )
    form_title.grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=(0, 15))
    
    # Form fields with better styling
    tk.Label(
        form_card, 
        text="Project Name:",
        font=("Arial", 10, "bold"),
        bg=colors["card"],
        fg=colors["text"]
    ).grid(row=1, column=0, padx=5, pady=10, sticky="e")
    
    entry_name = tk.Entry(
        form_card, 
        font=("Arial", 10),
        width=40,
        bd=1,
        relief="solid"
    )
    entry_name.grid(row=1, column=1, padx=5, pady=10, sticky="w")
    
    tk.Label(
        form_card, 
        text="Status:",
        font=("Arial", 10, "bold"),
        bg=colors["card"],
        fg=colors["text"]
    ).grid(row=2, column=0, padx=5, pady=10, sticky="e")
    
    # Use dropdown for status
    status_options = ["Active", "Planning", "Completed", "On Hold", "Cancelled"]
    status_var = tk.StringVar()
    status_dropdown = ttk.Combobox(
        form_card,
        textvariable=status_var,
        values=status_options,
        state="readonly",
        font=("Arial", 10),
        width=38
    )
    status_dropdown.current(0)
    status_dropdown.grid(row=2, column=1, padx=5, pady=10, sticky="w")
    
    tk.Label(
        form_card, 
        text="Description:",
        font=("Arial", 10, "bold"),
        bg=colors["card"],
        fg=colors["text"]
    ).grid(row=3, column=0, padx=5, pady=10, sticky="ne")
    
    # Use Text widget for description
    entry_desc = tk.Text(
        form_card,
        font=("Arial", 10),
        width=40,
        height=4,
        bd=1,
        relief="solid"
    )
    entry_desc.grid(row=3, column=1, padx=5, pady=10, sticky="w")
    
    # === FORM SECTION with BOTH ADD and DELETE buttons side by side ===

    # Add button - REPOSITIONED
    add_button = tk.Button(
        form_card,
        text="➕ Add Project",
        font=("Arial", 11, "bold"),
        bg=colors["secondary"],
        fg="white",
        padx=20,
        pady=15,
        bd=0,
        cursor="hand2",
        command=add_project
    )
    add_button.grid(row=1, column=2, padx=5, pady=10, sticky="nsew")

    # Delete button - MOVED HERE from below
    delete_button = tk.Button(
        form_card,
        text="🗑️ Delete Selected",
        font=("Arial", 11, "bold"),
        bg=colors["delete"],
        fg="white",
        padx=15,
        pady=15,
        bd=0,
        cursor="hand2",
        command=delete_project
    )
    delete_button.grid(row=2, column=2, padx=5, pady=10, sticky="nsew")

    # Back to Dashboard button - MOVED HERE from footer
    back_button = tk.Button(
        form_card,
        text="⬅️ Back to Dashboard",
        font=("Arial", 11, "bold"),
        bg="#1B5E20",
        fg="white",
        padx=15,
        pady=15,
        bd=0,
        relief="raised",
        cursor="hand2",
        command=back_to_dashboard
    )
    back_button.grid(row=3, column=2, padx=5, pady=10, sticky="nsew")

    # Add hover effects
    add_button.bind("<Enter>", lambda e: add_button.config(bg="#3AA83A"))
    add_button.bind("<Leave>", lambda e: add_button.config(bg=colors["secondary"]))
    delete_button.bind("<Enter>", lambda e: delete_button.config(bg="#D32F2F"))
    delete_button.bind("<Leave>", lambda e: delete_button.config(bg=colors["delete"]))
    back_button.bind("<Enter>", lambda e: back_button.config(bg="#2E7D32"))
    back_button.bind("<Leave>", lambda e: back_button.config(bg="#1B5E20"))
    
    # === TABLE SECTION ===
    table_card = tk.Frame(
        content_frame, 
        bg=colors["card"], 
        padx=20, 
        pady=20,
        bd=1, 
        relief="solid"
    )
    table_card.pack(fill="both", expand=True)
    
    # Table title
    table_title = tk.Label(
        table_card,
        text="Project Database",
        font=("Arial", 14, "bold"),
        bg=colors["card"],
        fg=colors["primary"]
    )
    table_title.pack(anchor="w", pady=(0, 15))
    
    # Table with scrollbar
    table_frame = tk.Frame(table_card, bg=colors["card"])
    table_frame.pack(fill="both", expand=True)
    
    # Create scrollbars
    y_scrollbar = ttk.Scrollbar(table_frame)
    y_scrollbar.pack(side="right", fill="y")
    
    x_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
    x_scrollbar.pack(side="bottom", fill="x")
    
    # Create treeview with modern styling
    tree = ttk.Treeview(
        table_frame,
        columns=("ID", "Name", "Status", "Description"),
        show="headings",
        style="modern.Treeview",
        yscrollcommand=y_scrollbar.set,
        xscrollcommand=x_scrollbar.set,
        height=8  # Reduced height to ensure delete button is visible
    )
    
    # Configure scrollbars
    y_scrollbar.config(command=tree.yview)
    x_scrollbar.config(command=tree.xview)
    
    # Configure columns
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Project Name")
    tree.heading("Status", text="Status")
    tree.heading("Description", text="Description")
    
    tree.column("ID", width=70, anchor="center", minwidth=50)
    tree.column("Name", width=230, anchor="w", minwidth=150)
    tree.column("Status", width=120, anchor="center", minwidth=100)
    tree.column("Description", width=420, anchor="w", minwidth=200)
    
    tree.pack(fill="both", expand=True)
    
    # === FOOTER ===
    footer_frame = tk.Frame(root, bg=colors["primary"], height=70)
    footer_frame.pack(side="bottom", fill="x")
    footer_frame.pack_propagate(False)  # This forces footer to maintain its height
    
    # Move user info to right side of footer
    user_label = tk.Label(
        footer_frame,
        text=f"Logged in as: {username}",
        font=("Arial", 10),
        bg=colors["primary"],
        fg="white"
    )
    user_label.pack(side="right", padx=20, pady=25)  # Positioned on right side
    
    # Load initial data
    load_data()
    root.mainloop()
