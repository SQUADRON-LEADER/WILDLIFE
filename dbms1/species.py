import tkinter as tk
from tkinter import ttk, messagebox, font
import mysql.connector
import dashboard
from datetime import datetime

# Transaction tracking for rollbacks
transaction_history = []
MAX_HISTORY = 10  # Maximum number of operations to remember

def run(username):
    # ROOT WINDOW SETUP
    root = tk.Tk()
    root.title("🦁 WildGuard - Species Management")
    root.geometry("1050x700")
    
    # WILDLIFE THEMED COLOR SCHEME
    forest_green = "#1e8449"     # Deep forest green
    leaf_green = "#27ae60"       # Lighter green
    earth_brown = "#795548"      # Earth brown
    savanna_tan = "#f5f5dc"      # Light tan background
    ivory_white = "#fffff0"      # Ivory for cards
    sunset_orange = "#FF7F50"    # For warning/delete buttons
    
    root.configure(bg=savanna_tan)
    
    # CUSTOM STYLES
    style = ttk.Style()
    style.theme_use("clam")
    
    # Button styles
    style.configure("TButton", font=("Helvetica", 10), padding=5)
    
    style.configure("Add.TButton", 
                    background=forest_green, 
                    foreground="white",
                    font=("Helvetica", 10, "bold"))
    
    style.configure("Delete.TButton", 
                    background=sunset_orange, 
                    foreground="white",
                    font=("Helvetica", 10, "bold"))
    
    # Treeview style
    style.configure("Treeview", 
                    background="#ffffff",
                    foreground="#333333",
                    rowheight=25,
                    fieldbackground="#ffffff")
    
    style.configure("Treeview.Heading", 
                    background=forest_green,
                    foreground="white",
                    font=("Helvetica", 10, "bold"),
                    relief="flat")
    
    style.map('Treeview', 
              background=[('selected', leaf_green)],
              foreground=[('selected', 'white')])
    
    # DATABASE CONNECTION
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="11223344",
            database="WildGuardDB"
        )
        cursor = conn.cursor(buffered=True)
        print("Database connected successfully!")
        
        # Test connection with a simple query
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"Connected to database: {db_name}")
        
    except mysql.connector.Error as err:
        # Handle specific error types
        if err.errno == 1049:  # Unknown database
            messagebox.showerror("Database Error", 
                "Database 'WildGuardDB' does not exist. Please create it first.")
        elif err.errno == 1045:  # Access denied
            messagebox.showerror("Database Error", 
                "Access denied. Please check your username and password.")
        elif err.errno == 2003:  # Server not found
            messagebox.showerror("Database Error", 
                "Could not connect to MySQL server. Is it running?")
        else:
            messagebox.showerror("Database Error", f"MySQL Error: {err}")
        
        print(f"Database connection failed: {err}")
        
        # Create a warning label in the UI
        conn_error_label = tk.Label(
            root, 
            text="⚠️ DATABASE NOT CONNECTED - Some features may not work", 
            font=("Helvetica", 12, "bold"), 
            bg="#ffcccc", 
            fg="#cc0000",
            padx=10,
            pady=5
        )
        conn_error_label.pack(fill="x")
        
        # Create dummy objects so the UI will still load
        conn = None
        cursor = None
    
    # CREATE SPECIES TABLE IF NOT EXISTS
    try:
        if conn:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Species (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(50),
                region VARCHAR(100),
                status VARCHAR(50),
                description TEXT
            )
            """)
            conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
    
    # HEADER
    header_frame = tk.Frame(root, bg=forest_green, pady=15)
    header_frame.pack(fill="x")
    
    tk.Label(
        header_frame, 
        text="🦁 Wildlife Species Management", 
        font=("Helvetica", 22, "bold"), 
        bg=forest_green, 
        fg="white"
    ).pack()
    
    tk.Label(
        header_frame, 
        text=f"Logged in as: {username}", 
        font=("Helvetica", 10), 
        bg=forest_green, 
        fg="white"
    ).pack()
    
    # MAIN CONTENT
    content_frame = tk.Frame(root, bg=savanna_tan, padx=20, pady=15)
    content_frame.pack(fill="both", expand=True)
    
    # SPLIT INTO TWO COLUMNS
    left_column = tk.Frame(content_frame, bg=savanna_tan)
    left_column.pack(side="left", fill="both", padx=(0, 10), expand=True)
    
    right_column = tk.Frame(content_frame, bg=savanna_tan)
    right_column.pack(side="right", fill="both", padx=(10, 0), expand=True)
    
    # FORM PANEL (LEFT)
    form_frame = tk.LabelFrame(
        left_column, 
        text=" Add New Species ", 
        font=("Helvetica", 12, "bold"), 
        bg=ivory_white, 
        fg=forest_green, 
        padx=15, 
        pady=15
    )
    form_frame.pack(fill="both", expand=True)
    
    # Form fields
    labels = ["Name", "Type", "Region", "Status", "Description"]
    entries = {}
    
    # Status options for dropdown
    status_options = [
        "Least Concern", 
        "Near Threatened", 
        "Vulnerable", 
        "Endangered", 
        "Critically Endangered",
        "Extinct in the Wild",
        "Extinct"
    ]
    
    # Icons for form labels
    icons = {
        "Name": "🏷️",
        "Type": "🔍",
        "Region": "🌍",
        "Status": "⚠️",
        "Description": "📝"
    }
    
    # Create form fields with icons
    for i, label in enumerate(labels):
        label_frame = tk.Frame(form_frame, bg=ivory_white)
        label_frame.grid(row=i, column=0, sticky="w", pady=5)
        
        tk.Label(
            label_frame, 
            text=f"{icons[label]} {label}:", 
            font=("Helvetica", 10, "bold"), 
            bg=ivory_white, 
            fg=forest_green
        ).pack(anchor="w")
        
        # Different widget types based on field
        if label == "Status":
            # Dropdown for status
            status_var = tk.StringVar()
            status_dropdown = ttk.Combobox(
                form_frame, 
                textvariable=status_var,
                values=status_options, 
                state="readonly",
                width=43
            )
            status_dropdown.current(0)
            status_dropdown.grid(row=i, column=1, pady=5, padx=5, sticky="w")
            entries[label.lower()] = status_var
            
        elif label == "Description":
            # Text widget for description
            desc_text = tk.Text(
                form_frame, 
                height=5, 
                width=35, 
                font=("Helvetica", 10),
                wrap="word"
            )
            desc_text.grid(row=i, column=1, pady=5, padx=5, sticky="w")
            entries[label.lower()] = desc_text
            
        else:
            # Regular entry for other fields
            entry = ttk.Entry(form_frame, width=45)
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="w")
            entries[label.lower()] = entry
    
    # Form buttons
    form_btn_frame = tk.Frame(form_frame, bg=ivory_white, pady=10)
    form_btn_frame.grid(row=len(labels), column=0, columnspan=2, sticky="ew")
    
    # TABLE PANEL (RIGHT)
    table_frame = tk.LabelFrame(
        right_column, 
        text=" Species Database ", 
        font=("Helvetica", 12, "bold"), 
        bg=ivory_white, 
        fg=forest_green, 
        padx=15, 
        pady=15
    )
    table_frame.pack(fill="both", expand=True)
    
    # Search bar
    search_frame = tk.Frame(table_frame, bg=ivory_white)
    search_frame.pack(fill="x", pady=(0, 10))
    
    tk.Label(
        search_frame, 
        text="🔍 Search:", 
        font=("Helvetica", 10, "bold"), 
        bg=ivory_white
    ).pack(side="left")
    
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side="left", padx=5)
    
    # Table with scrollbars
    tree_container = tk.Frame(table_frame)
    tree_container.pack(fill="both", expand=True)
    
    # Scrollbars
    vsb = ttk.Scrollbar(tree_container, orient="vertical")
    hsb = ttk.Scrollbar(tree_container, orient="horizontal")
    
    # Treeview
    columns = ("ID", "Name", "Type", "Region", "Status", "Description")
    tree = ttk.Treeview(
        tree_container, 
        columns=columns, 
        show="headings", 
        yscrollcommand=vsb.set,
        xscrollcommand=hsb.set,
        height=15
    )
    
    # Configure scrollbars
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)
    
    # Pack scrollbars and treeview
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    tree.pack(side="left", fill="both", expand=True)
    
    # Configure columns
    tree.column("ID", width=50, anchor="center")
    tree.column("Name", width=150, anchor="w")
    tree.column("Type", width=100, anchor="w")
    tree.column("Region", width=120, anchor="w")
    tree.column("Status", width=150, anchor="w")
    tree.column("Description", width=200, anchor="w")
    
    # Configure headings
    for col in columns:
        tree.heading(col, text=col)
    
    # Add this to the table_frame after the buttons
    rollback_status = tk.Label(
        table_frame, 
        text="No recent actions to undo", 
        font=("Helvetica", 9, "italic"), 
        bg=ivory_white, 
        fg="#666666"
    )
    rollback_status.pack(anchor="e", pady=(5, 0))
    
    # FOOTER
    footer_frame = tk.Frame(root, bg=forest_green, height=60)
    footer_frame.pack(side="bottom", fill="x")
    
    # FUNCTIONS
    def refresh_table(search_term=""):
        """Refresh the table data, optionally filtering by search term"""
        # Clear existing rows
        for item in tree.get_children():
            tree.delete(item)
            
        if not conn:
            return
            
        try:
            # Execute query based on search term
            if search_term:
                cursor.execute("""
                    SELECT * FROM Species 
                    WHERE name LIKE %s OR type LIKE %s OR region LIKE %s OR status LIKE %s
                    ORDER BY name
                """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            else:
                cursor.execute("SELECT * FROM Species ORDER BY name")
                
            # Insert data with color coding by status
            for i, row in enumerate(cursor.fetchall()):
                # Determine row tags for coloring
                tags = (f"row{i % 2}",)  # Alternating row colors
                
                # Add status-based tag
                status_lower = str(row[4]).lower()
                if "critically" in status_lower:
                    tags = tags + ("critical",)
                elif "endangered" in status_lower:
                    tags = tags + ("endangered",)
                elif "vulnerable" in status_lower:
                    tags = tags + ("vulnerable",)
                elif "extinct" in status_lower:
                    tags = tags + ("extinct",)
                elif "threatened" in status_lower:
                    tags = tags + ("threatened",)
                    
                # Insert row with tags
                tree.insert("", "end", values=row, tags=tags)
                
            # Configure tag colors
            tree.tag_configure("row0", background="#ffffff")
            tree.tag_configure("row1", background="#f0f0f0")
            tree.tag_configure("critical", foreground="#cc0000")  # Dark red
            tree.tag_configure("endangered", foreground="#e74c3c")  # Red
            tree.tag_configure("vulnerable", foreground="#f39c12")  # Orange
            tree.tag_configure("extinct", foreground="#7f8c8d")    # Gray
            tree.tag_configure("threatened", foreground="#8e44ad") # Purple
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh table: {e}")
    
    def add_species():
        """Add a new species to the database"""
        if not conn:
            messagebox.showerror("Error", "Database not connected")
            return
            
        try:
            # Get values from form fields
            name = entries["name"].get().strip()
            type_val = entries["type"].get().strip()
            region = entries["region"].get().strip()
            
            # Handle different form field types
            if isinstance(entries["status"], tk.StringVar):
                status = entries["status"].get()
            else:
                status = entries["status"].get().strip()
                
            if isinstance(entries["description"], tk.Text):
                description = entries["description"].get("1.0", "end-1c").strip()
            else:
                description = entries["description"].get().strip()
            
            # Validate required fields
            if not name:
                messagebox.showwarning("Input Error", "Species name is required")
                return
                
            # Insert into database
            cursor.execute("""
                INSERT INTO Species (name, type, region, status, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, type_val, region, status, description))
            
            # Get the ID of the newly inserted record
            new_id = cursor.lastrowid
            
            # Add to transaction history
            transaction_history.append({
                "type": "INSERT",
                "id": new_id,
                "name": name,
                "time": datetime.now()
            })
            
            # Limit history size
            if len(transaction_history) > MAX_HISTORY:
                transaction_history.pop(0)
                
            # Enable the rollback button
            rollback_btn.state(["!disabled"])
            
            conn.commit()
            
            # Clear form fields
            clear_form()
            
            # Refresh table and show success message
            refresh_table()
            update_rollback_status()
            messagebox.showinfo("Success", "Species added successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add species: {e}")
            conn.rollback()  # Rollback on error
    
    def delete_species():
        """Delete selected species"""
        if not conn:
            messagebox.showerror("Error", "Database not connected")
            return
            
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Error", "Please select a species to delete")
            return
            
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete {len(selected)} selected species?"
        )
        
        if confirm:
            try:
                for item in selected:
                    # Get all values to store for potential rollback
                    values = tree.item(item, "values")
                    species_id = values[0]
                    
                    # Store record for rollback before deletion
                    transaction_history.append({
                        "type": "DELETE",
                        "id": species_id,
                        "name": values[1],
                        "type": values[2],
                        "region": values[3],
                        "status": values[4],
                        "description": values[5],
                        "time": datetime.now()
                    })
                    
                    # Limit history size
                    if len(transaction_history) > MAX_HISTORY:
                        transaction_history.pop(0)
                    
                    cursor.execute("DELETE FROM Species WHERE id = %s", (species_id,))
                
                # Enable the rollback button
                rollback_btn.state(["!disabled"])
                
                conn.commit()
                
                refresh_table()
                update_rollback_status()
                messagebox.showinfo("Success", "Selected species deleted successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete species: {e}")
                conn.rollback()  # Rollback on error
    
    def clear_form():
        """Clear all form fields"""
        entries["name"].delete(0, "end")
        entries["type"].delete(0, "end")
        entries["region"].delete(0, "end")
        
        if isinstance(entries["status"], tk.StringVar):
            entries["status"].set(status_options[0])
        else:
            entries["status"].delete(0, "end")
            
        if isinstance(entries["description"], tk.Text):
            entries["description"].delete("1.0", "end")
        else:
            entries["description"].delete(0, "end")
    
    def on_search(*args):
        """Handle search input changes"""
        refresh_table(search_var.get())
    
    def back_to_dashboard():
        """Return to dashboard"""
        if conn:
            conn.close()
        root.destroy()
        dashboard.Dashboard(username)
    
    def rollback_last_action():
        """Roll back the last database operation"""
        if not conn or not transaction_history:
            messagebox.showinfo("Info", "Nothing to roll back")
            return
            
        try:
            # Get the last transaction
            last_action = transaction_history.pop()
            action_type = last_action["type"]
            
            if action_type == "INSERT":
                # Rollback an insert by deleting the record
                cursor.execute("DELETE FROM Species WHERE id = %s", (last_action["id"],))
                messagebox.showinfo("Success", f"Rolled back addition of '{last_action['name']}'")
                
            elif action_type == "DELETE":
                # Rollback a delete by re-inserting the record
                cursor.execute("""
                    INSERT INTO Species (id, name, type, region, status, description) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    last_action["id"], 
                    last_action["name"], 
                    last_action["type"], 
                    last_action["region"], 
                    last_action["status"], 
                    last_action["description"]
                ))
                messagebox.showinfo("Success", f"Restored deleted species '{last_action['name']}'")
                
            conn.commit()
            refresh_table()
            update_rollback_status()
            
            # Disable rollback button if history is empty
            if not transaction_history:
                rollback_btn.state(["disabled"])
                
        except Exception as e:
            messagebox.showerror("Rollback Failed", f"Could not roll back the last action: {e}")
            conn.rollback()  # Rollback the failed rollback attempt
    
    def update_rollback_status():
        if not transaction_history:
            rollback_status.config(text="No recent actions to undo")
        else:
            last = transaction_history[-1]
            if last["type"] == "INSERT":
                rollback_status.config(text=f"Last action: Added '{last['name']}' at {last['time'].strftime('%H:%M:%S')}")
            elif last["type"] == "DELETE":
                rollback_status.config(text=f"Last action: Deleted '{last['name']}' at {last['time'].strftime('%H:%M:%S')}")
    
    # Bind search field
    search_var.trace("w", on_search)
    
    # Populate form when selecting a table row
    def on_tree_select(event):
        selected = tree.selection()
        if selected:
            values = tree.item(selected[0], "values")
            
            # Clear form
            clear_form()
            
            # Fill form with selected data
            entries["name"].insert(0, values[1])
            entries["type"].insert(0, values[2])
            entries["region"].insert(0, values[3])
            
            if isinstance(entries["status"], tk.StringVar):
                if values[4] in status_options:
                    entries["status"].set(values[4])
                else:
                    entries["status"].set(status_options[0])
            else:
                entries["status"].insert(0, values[4])
                
            if isinstance(entries["description"], tk.Text):
                entries["description"].insert("1.0", values[5])
            else:
                entries["description"].insert(0, values[5])
    
    # Double click to select row
    tree.bind("<Double-1>", on_tree_select)
    
    # ADD BUTTONS
    # Form buttons
    add_btn = ttk.Button(
        form_btn_frame, 
        text="➕ Add Species", 
        command=add_species, 
        style="Add.TButton", 
        cursor="hand2"
    )
    add_btn.pack(side="left", padx=(0, 5), fill="x", expand=True)
    
    clear_btn = ttk.Button(
        form_btn_frame, 
        text="🔄 Clear Form", 
        command=clear_form, 
        cursor="hand2"
    )
    clear_btn.pack(side="left", padx=5, fill="x", expand=True)
    
    # Table buttons
    table_btn_frame = tk.Frame(table_frame, bg=ivory_white, pady=10)
    table_btn_frame.pack(fill="x")
    
    delete_btn = ttk.Button(
        table_btn_frame, 
        text="❌ Delete Selected", 
        command=delete_species, 
        style="Delete.TButton", 
        cursor="hand2"
    )
    delete_btn.pack(side="left", padx=(0, 5), fill="x", expand=True)
    
    refresh_btn = ttk.Button(
        table_btn_frame, 
        text="🔄 Refresh", 
        command=lambda: refresh_table(), 
        cursor="hand2"
    )
    refresh_btn.pack(side="left", padx=5, fill="x", expand=True)
    
    # Add the rollback button to the table button frame
    rollback_btn = ttk.Button(
        table_btn_frame, 
        text="↩️ Rollback Last Action", 
        command=rollback_last_action, 
        cursor="hand2"
    )
    rollback_btn.pack(side="left", padx=5, fill="x", expand=True)

    # Initially disable until we have something to roll back
    rollback_btn.state(["disabled"])
    
    # Back button in footer
    back_btn = tk.Button(
        footer_frame, 
        text="⬅️ Back to Dashboard", 
        font=("Helvetica", 12, "bold"),
        bg="#196f3d", 
        fg="white", 
        padx=20, 
        pady=10, 
        bd=0, 
        cursor="hand2",
        command=back_to_dashboard
    )
    back_btn.pack(side="left", padx=20, pady=10)
    
    # Add hover effect to back button
    back_btn.bind("<Enter>", lambda e: back_btn.config(bg=leaf_green))
    back_btn.bind("<Leave>", lambda e: back_btn.config(bg="#196f3d"))
    
    # Load data initially
    refresh_table()
    
    # Start the main loop
    root.mainloop()

# For standalone testing
if __name__ == "__main__":
    run("Admin")
