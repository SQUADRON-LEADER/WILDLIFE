import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import dashboard  # To go back to the main dashboard

def run(username):
    root = tk.Tk()
    root.title("🦁 WildGuard - Endangered Species Management")
    root.geometry("900x600")
    
    # WILDLIFE THEMED COLOR SCHEME
    forest_green = "#1e8449"     # Deep forest green
    leaf_green = "#27ae60"       # Lighter green
    earth_brown = "#795548"      # Earth brown
    savanna_tan = "#f5f5dc"      # Light tan background
    ivory_white = "#fffff0"      # Ivory for cards
    sunset_orange = "#FF7F50"    # For warning/delete buttons
    sky_blue = "#3498db"         # For back button
    
    root.configure(bg=savanna_tan)
    
    # CUSTOM STYLES
    style = ttk.Style()
    style.theme_use('clam')
    
    # Style the treeview
    style.configure("Treeview", 
                    background="#ffffff",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="#ffffff")
                    
    style.configure("Treeview.Heading", 
                    background=forest_green,
                    foreground="white",
                    font=('Helvetica', 10, 'bold'),
                    relief="flat")
                    
    style.map('Treeview', 
              background=[('selected', leaf_green)],
              foreground=[('selected', 'white')])

    # Database connection
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="11223344",
        database="WildGuardDB"
    )
    cursor = conn.cursor()

    # Function to fetch and display endangered species
    def load_data():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("""
            SELECT es.id, s.name AS species_name, es.status 
            FROM Endangered_Species es
            JOIN Species s ON es.species_id = s.id
        """)
        for i, row in enumerate(cursor.fetchall()):
            # Add tags for alternating row colors
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            
            # Add tag based on status
            status_lower = str(row[2]).lower()
            if "critically" in status_lower:
                tag_status = "critical"
            elif "endangered" in status_lower:
                tag_status = "endangered"
            elif "vulnerable" in status_lower:
                tag_status = "vulnerable"
            else:
                tag_status = "normal"
                
            tree.insert("", "end", values=row, tags=(tag, tag_status))
            
        # Configure tag colors
        tree.tag_configure("evenrow", background="#ffffff")
        tree.tag_configure("oddrow", background="#f0f0f0")
        tree.tag_configure("critical", foreground="#cc0000")  # Dark red
        tree.tag_configure("endangered", foreground="#e74c3c") # Red
        tree.tag_configure("vulnerable", foreground="#f39c12") # Orange
        tree.tag_configure("normal", foreground="#2c3e50")    # Dark blue-grey

    # Add Endangered Species
    def add_entry():
        try:
            species_id = int(species_id_entry.get())
            status = status_entry.get()

            if not status:
                raise ValueError("Status cannot be empty.")

            cursor.execute("INSERT INTO Endangered_Species (species_id, status) VALUES (%s, %s)", (species_id, status))
            conn.commit()
            messagebox.showinfo("Success", "Endangered species entry added!")
            species_id_entry.delete(0, tk.END)
            status_entry.delete(0, tk.END)
            load_data()
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except mysql.connector.Error as err:
            messagebox.showerror("MySQL Error", str(err))

    # Delete selected entry
    def delete_selected():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Select row", "Please select a row to delete.")
            return
            
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this record?")
        if not confirm:
            return
            
        values = tree.item(selected, 'values')
        es_id = values[0]
        cursor.execute("DELETE FROM Endangered_Species WHERE id = %s", (es_id,))
        conn.commit()
        load_data()
        messagebox.showinfo("Success", "Record deleted successfully!")

    # Back to dashboard
    def back_to_dashboard():
        root.destroy()
        dashboard.Dashboard(username=username)

    # === IMPROVED UI LAYOUT ===
    
    # Header with shadow effect
    header_frame = tk.Frame(root, bg=forest_green, height=80)
    header_frame.pack(fill="x")
    
    # Add shadow frame
    shadow_frame = tk.Frame(root, height=5, bg="#144c2e")
    shadow_frame.pack(fill="x")
    
    # Header content
    heading = tk.Label(
        header_frame, 
        text="🐅 Endangered Species Management", 
        font=("Arial", 22, "bold"), 
        bg=forest_green, 
        fg="white"
    )
    heading.pack(pady=20)

    # Main content container
    main_frame = tk.Frame(root, bg=savanna_tan, pady=15)
    main_frame.pack(fill="both", expand=True, padx=20)
    
    # Form panel with title and border
    form_panel = tk.LabelFrame(
        main_frame, 
        text=" Add New Endangered Species ", 
        font=('Arial', 12, 'bold'), 
        bg=ivory_white, 
        fg=forest_green, 
        padx=15, 
        pady=15
    )
    form_panel.pack(fill="x", pady=10)

    # Input Frame with better styling
    form_frame = tk.Frame(form_panel, bg=ivory_white)
    form_frame.pack(pady=5)

    # Form fields with better labels and styling
    tk.Label(
        form_frame, 
        text="🏷️ Species ID:", 
        font=('Arial', 11, 'bold'), 
        bg=ivory_white, 
        fg=earth_brown
    ).grid(row=0, column=0, padx=10, pady=8, sticky="e")
    
    species_id_entry = ttk.Entry(form_frame, width=20, font=('Arial', 10))
    species_id_entry.grid(row=0, column=1, padx=5, pady=8, sticky="w")

    tk.Label(
        form_frame, 
        text="⚠️ Status:", 
        font=('Arial', 11, 'bold'), 
        bg=ivory_white, 
        fg=earth_brown
    ).grid(row=0, column=2, padx=10, pady=8, sticky="e")
    
    status_entry = ttk.Entry(form_frame, width=30, font=('Arial', 10))
    status_entry.grid(row=0, column=3, padx=5, pady=8, sticky="w")

    # Create a beautiful Add button
    add_btn = tk.Button(
        form_frame, 
        text="➕ Add Species", 
        command=add_entry,
        bg=leaf_green, 
        fg="white", 
        font=('Arial', 10, 'bold'),
        padx=15, 
        pady=8, 
        bd=0, 
        cursor="hand2",
        relief="raised"
    )
    add_btn.grid(row=0, column=4, padx=15, pady=8)
    
    # Add hover effect to Add button
    add_btn.bind("<Enter>", lambda e: add_btn.config(bg="#2ecc71"))
    add_btn.bind("<Leave>", lambda e: add_btn.config(bg=leaf_green))

    # Table panel with title
    table_panel = tk.LabelFrame(
        main_frame, 
        text=" Endangered Species List ", 
        font=('Arial', 12, 'bold'), 
        bg=ivory_white, 
        fg=forest_green, 
        padx=15, 
        pady=15
    )
    table_panel.pack(fill="both", expand=True, pady=10)

    # Treeview with scrollbar in a container frame
    tree_container = tk.Frame(table_panel, bg=ivory_white)
    tree_container.pack(fill="both", expand=True, pady=5)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(tree_container)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Enhanced treeview
    columns = ("ID", "Species Name", "Status")
    tree = ttk.Treeview(
        tree_container, 
        columns=columns, 
        show="headings", 
        height=12,
        yscrollcommand=scrollbar.set
    )
    
    # Configure columns with better widths
    tree.column("ID", width=80, anchor="center")
    tree.column("Species Name", width=300, anchor="w")
    tree.column("Status", width=300, anchor="w")
    
    # Configure headings
    for col in columns:
        tree.heading(col, text=col)
    
    # Configure scrollbar
    scrollbar.config(command=tree.yview)
    
    tree.pack(fill="both", expand=True)

    # Action buttons frame
    btn_frame = tk.Frame(table_panel, bg=ivory_white, pady=10)
    btn_frame.pack(fill="x")

    # Create a styled Delete button
    delete_btn = tk.Button(
        btn_frame, 
        text="❌ Delete Selected", 
        command=delete_selected,
        bg=sunset_orange, 
        fg="white", 
        font=('Arial', 10, 'bold'),
        padx=15, 
        pady=8, 
        bd=0, 
        cursor="hand2"
    )
    delete_btn.pack(side="left", padx=(0, 10))
    
    # Add hover effect to Delete button
    delete_btn.bind("<Enter>", lambda e: delete_btn.config(bg="#e74c3c"))
    delete_btn.bind("<Leave>", lambda e: delete_btn.config(bg=sunset_orange))

    # Footer with back button
    footer_frame = tk.Frame(root, bg=forest_green, height=60)
    footer_frame.pack(side="bottom", fill="x")
    
    # Create a prominent back button
    back_btn = tk.Button(
        footer_frame, 
        text="⬅️ Back to Dashboard", 
        command=back_to_dashboard,
        bg="#1a5e3e", 
        fg="white", 
        font=('Arial', 12, 'bold'),
        padx=20, 
        pady=10, 
        bd=0, 
        cursor="hand2"
    )
    back_btn.pack(side="left", padx=20, pady=10)
    
    # Add hover effect to back button
    back_btn.bind("<Enter>", lambda e: back_btn.config(bg=leaf_green))
    back_btn.bind("<Leave>", lambda e: back_btn.config(bg="#1a5e3e"))

    load_data()
    root.mainloop()
