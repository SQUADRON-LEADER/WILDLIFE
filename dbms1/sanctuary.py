import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
import importlib
from datetime import datetime

def run(username):
    """Main function to run the Sanctuary Management module"""
    # Create and configure the main window
    root = tk.Tk()
    root.title("🌳 Sanctuary Management - WildGuard")
    root.geometry("1100x700")
    root.configure(bg="#f4f9f4")  # Light natural green background
    
    # Define color scheme
    colors = {
        "primary": "#2e7d32",      # Dark green
        "primary_light": "#60ad5e", # Lighter green
        "secondary": "#005b96",    # Blue for accents
        "accent": "#ffb74d",       # Orange for highlights/warnings
        "bg": "#f4f9f4",           # Light background
        "card": "#ffffff",         # White for cards
        "text": "#263238",         # Dark text
        "text_light": "#546e7a",   # Lighter text for subtitles
        "success": "#43a047",      # Green for success messages
        "error": "#e53935",        # Red for errors
        "border": "#e0e0e0"        # Light border color
    }
    
    # Configure ttk styles for consistent look
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure Treeview
    style.configure(
        "Custom.Treeview", 
        background=colors["card"],
        foreground=colors["text"],
        rowheight=28,
        fieldbackground=colors["card"],
        font=("Segoe UI", 10)
    )
    style.configure(
        "Custom.Treeview.Heading",
        background=colors["primary"],
        foreground="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat"
    )
    style.map(
        "Custom.Treeview",
        background=[("selected", colors["primary_light"])],
        foreground=[("selected", "white")]
    )
    
    # Configure buttons
    style.configure(
        "Primary.TButton", 
        font=("Segoe UI", 10, "bold"),
        background=colors["primary"],
        foreground="white"
    )
    style.map(
        "Primary.TButton",
        background=[("active", colors["primary_light"])]
    )
    
    style.configure(
        "Danger.TButton", 
        font=("Segoe UI", 10, "bold"),
        background=colors["error"],
        foreground="white"
    )
    
    style.configure(
        "Info.TButton", 
        font=("Segoe UI", 10, "bold"),
        background=colors["secondary"],
        foreground="white"
    )

    # DB Connection
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="11223344",
            database="WildGuardDB"
        )
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Sanctuary (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                location VARCHAR(100) NOT NULL,
                area_sq_km FLOAT,
                established_year INT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
        root.destroy()
        return
    
    # Header section
    header_frame = tk.Frame(root, bg=colors["primary"], padx=20, pady=15)
    header_frame.pack(fill="x")
    
    # Back button with improved styling
    def return_to_dashboard():
        try:
            root.destroy()
            dashboard = importlib.import_module("dashboard")
            dashboard.Dashboard(username=username)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to return to dashboard: {str(e)}")
    
    back_btn = tk.Button(
        header_frame, 
        text="← Back to Dashboard", 
        command=return_to_dashboard,
        bg=colors["primary"], 
        fg="white", 
        font=("Segoe UI", 10),
        bd=0,
        activebackground="#235c26",  # Darker shade for hover
        activeforeground="white",
        cursor="hand2",
        padx=10,
        pady=5
    )
    back_btn.pack(side="left", padx=10)
    
    # Title with icon
    title_label = tk.Label(
        header_frame, 
        text="🌳 Wildlife Sanctuary Management", 
        font=("Segoe UI", 18, "bold"), 
        bg=colors["primary"], 
        fg="white"
    )
    title_label.pack(pady=5)
    
    # User info in header
    user_frame = tk.Frame(header_frame, bg=colors["primary"])
    user_frame.pack(side="right")
    
    user_label = tk.Label(
        user_frame,
        text=f"Logged in as: {username}",
        font=("Segoe UI", 9),
        bg=colors["primary"],
        fg="white"
    )
    user_label.pack()
    
    # Main content container
    content_frame = tk.Frame(root, bg=colors["bg"], padx=20, pady=20)
    content_frame.pack(fill="both", expand=True)
    
    # Create two-column layout
    left_frame = tk.Frame(content_frame, bg=colors["bg"], width=400)
    left_frame.pack(side="left", fill="y", padx=(0, 10))
    left_frame.pack_propagate(False)  # Prevent shrinking
    
    right_frame = tk.Frame(content_frame, bg=colors["bg"])
    right_frame.pack(side="right", fill="both", expand=True)
    
    # Statistics card
    stats_frame = tk.LabelFrame(
        left_frame, 
        text=" 📊 Sanctuary Statistics ", 
        font=("Segoe UI", 12, "bold"),
        fg=colors["primary"],
        bg=colors["card"],
        padx=15,
        pady=15,
        bd=1,
        relief="solid"
    )
    stats_frame.pack(fill="x", pady=(0, 15))
    
    # Statistics counters
    stats_items = [
        {"icon": "🏞️", "label": "Total Sanctuaries:", "id": "total"},
        {"icon": "📏", "label": "Total Protected Area:", "id": "area", "unit": "km²"},
        {"icon": "🗓️", "label": "Oldest Sanctuary:", "id": "oldest"},
        {"icon": "🌍", "label": "Most Common Location:", "id": "location"}
    ]
    
    stat_labels = {}
    for i, item in enumerate(stats_items):
        frame = tk.Frame(stats_frame, bg=colors["card"])
        frame.pack(fill="x", pady=5)
        
        tk.Label(
            frame, 
            text=f"{item['icon']} {item['label']}", 
            font=("Segoe UI", 10),
            bg=colors["card"],
            fg=colors["text"]
        ).pack(side="left")
        
        value = tk.Label(
            frame,
            text="Loading...",
            font=("Segoe UI", 10, "bold"),
            bg=colors["card"],
            fg=colors["primary"]
        )
        value.pack(side="right")
        stat_labels[item["id"]] = value
    
    # Entry Form
    form_frame = tk.LabelFrame(
        left_frame, 
        text=" ✏️ Sanctuary Details ", 
        font=("Segoe UI", 12, "bold"),
        fg=colors["primary"],
        bg=colors["card"],
        padx=15,
        pady=15,
        bd=1,
        relief="solid"
    )
    form_frame.pack(fill="both", expand=True)
    
    form_title = tk.Label(
        form_frame,
        text="Add a new sanctuary:",
        font=("Segoe UI", 11),
        bg=colors["card"],
        fg=colors["text_light"],
        anchor="w"
    )
    form_title.pack(fill="x", pady=(0, 10))
    
    # Form fields with better layout
    labels = [
        {"name": "name", "text": "Name:", "required": True},
        {"name": "location", "text": "Location:", "required": True},
        {"name": "area_sq_km", "text": "Area (sq km):", "required": False},
        {"name": "established_year", "text": "Established Year:", "required": False}
    ]
    
    entries = {}
    for item in labels:
        # Container frame for each field
        field_frame = tk.Frame(form_frame, bg=colors["card"], pady=5)
        field_frame.pack(fill="x")
        
        # Label with required indicator if necessary
        label_text = item["text"]
        if item["required"]:
            label_text += " *"
            
        label = tk.Label(
            field_frame,
            text=label_text,
            font=("Segoe UI", 10),
            bg=colors["card"],
            fg=colors["text"],
            width=15,
            anchor="w"
        )
        label.pack(side="left")
        
        # Entry widget
        entry = ttk.Entry(field_frame, font=("Segoe UI", 10), width=25)
        entry.pack(side="left", fill="x", expand=True)
        entries[item["name"]] = entry
    
    # Description field (multiline)
    desc_frame = tk.Frame(form_frame, bg=colors["card"], pady=5)
    desc_frame.pack(fill="x")
    
    desc_label = tk.Label(
        desc_frame,
        text="Description:",
        font=("Segoe UI", 10),
        bg=colors["card"],
        fg=colors["text"],
        width=15,
        anchor="nw"
    )
    desc_label.pack(side="left", anchor="n")
    
    desc_text = scrolledtext.ScrolledText(
        desc_frame,
        font=("Segoe UI", 10),
        height=5,
        width=25,
        wrap="word"
    )
    desc_text.pack(side="left", fill="both", expand=True)
    entries["description"] = desc_text
    
    # Status message
    status_frame = tk.Frame(form_frame, bg=colors["card"])
    status_frame.pack(fill="x", pady=10)
    
    status_label = tk.Label(
        status_frame,
        text="",
        font=("Segoe UI", 9, "italic"),
        bg=colors["card"],
        fg=colors["success"]
    )
    status_label.pack(side="left")
    
    # Function to show status messages
    def show_status(message, is_error=False):
        status_label.config(text=message, fg=colors["error"] if is_error else colors["success"])
        # Auto-clear after 5 seconds
        root.after(5000, lambda: status_label.config(text=""))
    
    # Form buttons with improved styling
    button_frame = tk.Frame(form_frame, bg=colors["card"], pady=10)
    button_frame.pack(fill="x")
    
    # Variable to track if we're editing an existing sanctuary
    current_id = tk.StringVar()
    
    def clear_form():
        """Clear all form fields and reset edit mode"""
        for entry in entries.values():
            if isinstance(entry, scrolledtext.ScrolledText):
                entry.delete("1.0", tk.END)
            else:
                entry.delete(0, tk.END)
        current_id.set("")
        add_btn.config(text="➕ Add Sanctuary")
        show_status("Form cleared")
    
    def refresh_table():
        """Refresh the sanctuary list"""
        for row in tree.get_children():
            tree.delete(row)
            
        try:
            cursor.execute("SELECT * FROM Sanctuary ORDER BY name")
            for i, row in enumerate(cursor.fetchall()):
                # Format the data for display
                display_row = [
                    row[0],  # ID
                    row[1],  # Name
                    row[2],  # Location
                    f"{row[3]:.1f}" if row[3] else "-",  # Area
                    row[4] if row[4] else "-",  # Year
                    (row[5][:40] + "...") if row[5] and len(row[5]) > 40 else (row[5] or "-")  # Description
                ]
                # Add row with alternating colors
                tree.insert("", "end", values=display_row, tags=('even' if i % 2 == 0 else 'odd',))
                
            # Update statistics
            update_statistics()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch data: {err}")
    
    def update_statistics():
        """Update the sanctuary statistics"""
        try:
            # Total sanctuaries
            cursor.execute("SELECT COUNT(*) FROM Sanctuary")
            total = cursor.fetchone()[0]
            stat_labels["total"].config(text=str(total))
            
            # Total area
            cursor.execute("SELECT SUM(area_sq_km) FROM Sanctuary WHERE area_sq_km IS NOT NULL")
            total_area = cursor.fetchone()[0]
            if total_area:
                stat_labels["area"].config(text=f"{total_area:,.1f} km²")
            else:
                stat_labels["area"].config(text="0 km²")
            
            # Oldest sanctuary
            cursor.execute("""
                SELECT name, established_year FROM Sanctuary 
                WHERE established_year IS NOT NULL 
                ORDER BY established_year ASC LIMIT 1
            """)
            oldest = cursor.fetchone()
            if oldest:
                stat_labels["oldest"].config(text=f"{oldest[0]} ({oldest[1]})")
            else:
                stat_labels["oldest"].config(text="N/A")
            
            # Most common location
            cursor.execute("""
                SELECT location, COUNT(*) as count FROM Sanctuary 
                GROUP BY location ORDER BY count DESC LIMIT 1
            """)
            common_loc = cursor.fetchone()
            if common_loc:
                stat_labels["location"].config(text=f"{common_loc[0]} ({common_loc[1]})")
            else:
                stat_labels["location"].config(text="N/A")
                
        except mysql.connector.Error as err:
            print(f"Statistics error: {err}")
    
    def save_sanctuary():
        """Add or update a sanctuary record"""
        # Get form values
        name = entries["name"].get().strip()
        location = entries["location"].get().strip()
        
        # Validate required fields
        if not name:
            show_status("Name is required!", True)
            entries["name"].focus_set()
            return
            
        if not location:
            show_status("Location is required!", True)
            entries["location"].focus_set()
            return
        
        # Get optional fields
        area = entries["area_sq_km"].get().strip()
        year = entries["established_year"].get().strip()
        description = entries["description"].get("1.0", tk.END).strip()
        
        # Convert and validate numeric fields
        area_val = None
        if area:
            try:
                area_val = float(area)
                if area_val <= 0:
                    show_status("Area must be a positive number!", True)
                    entries["area_sq_km"].focus_set()
                    return
            except ValueError:
                show_status("Area must be a valid number!", True)
                entries["area_sq_km"].focus_set()
                return
        
        year_val = None
        if year:
            try:
                year_val = int(year)
                current_year = datetime.now().year
                if year_val < 1800 or year_val > current_year:
                    show_status(f"Year must be between 1800 and {current_year}!", True)
                    entries["established_year"].focus_set()
                    return
            except ValueError:
                show_status("Year must be a valid number!", True)
                entries["established_year"].focus_set()
                return
        
        try:
            if current_id.get():  # Update existing record
                cursor.execute(
                    """UPDATE Sanctuary 
                       SET name=%s, location=%s, area_sq_km=%s, established_year=%s, description=%s 
                       WHERE id=%s""",
                    (name, location, area_val, year_val, description, current_id.get())
                )
                message = "Sanctuary updated successfully!"
            else:  # Add new record
                cursor.execute(
                    """INSERT INTO Sanctuary 
                       (name, location, area_sq_km, established_year, description) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    (name, location, area_val, year_val, description)
                )
                message = "Sanctuary added successfully!"
                
            conn.commit()
            show_status(message)
            clear_form()
            refresh_table()
            
        except mysql.connector.Error as err:
            show_status(f"Database error: {err}", True)
    
    def delete_sanctuary():
        """Delete selected sanctuary records"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a sanctuary to delete.")
            return
        
        # Get names of selected sanctuaries for confirmation
        sanctuary_names = []
        for item in selected:
            sanctuary_id = tree.item(item)["values"][0]
            name = tree.item(item)["values"][1]
            sanctuary_names.append(f"• {name} (ID: {sanctuary_id})")
        
        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete the following {len(selected)} sanctuary/sanctuaries?\n\n" +
            "\n".join(sanctuary_names) +
            "\n\nThis action cannot be undone.",
            icon="warning"
        )
        
        if confirm:
            try:
                for item in selected:
                    sanctuary_id = tree.item(item)["values"][0]
                    cursor.execute("DELETE FROM Sanctuary WHERE id = %s", (sanctuary_id,))
                
                conn.commit()
                show_status(f"{len(selected)} sanctuary/sanctuaries deleted successfully!")
                refresh_table()
                
            except mysql.connector.Error as err:
                show_status(f"Error deleting sanctuary: {err}", True)
    
    def edit_sanctuary():
        """Load selected sanctuary for editing"""
        selected = tree.selection()
        if not selected or len(selected) > 1:
            messagebox.showwarning("Selection Required", "Please select a single sanctuary to edit.")
            return
        
        # Get the sanctuary ID
        sanctuary_id = tree.item(selected[0])["values"][0]
        
        try:
            # Fetch the sanctuary data
            cursor.execute("SELECT * FROM Sanctuary WHERE id = %s", (sanctuary_id,))
            sanctuary = cursor.fetchone()
            
            if sanctuary:
                # Clear the form first
                clear_form()
                
                # Set the current ID
                current_id.set(sanctuary[0])
                
                # Fill the form with data
                entries["name"].insert(0, sanctuary[1] or "")
                entries["location"].insert(0, sanctuary[2] or "")
                if sanctuary[3]:
                    entries["area_sq_km"].insert(0, str(sanctuary[3]))
                if sanctuary[4]:
                    entries["established_year"].insert(0, str(sanctuary[4]))
                if sanctuary[5]:
                    entries["description"].insert("1.0", sanctuary[5])
                
                # Update button text
                add_btn.config(text="🔄 Update Sanctuary")
                show_status("Sanctuary loaded for editing")
            else:
                show_status("Sanctuary not found!", True)
                
        except mysql.connector.Error as err:
            show_status(f"Error loading sanctuary: {err}", True)
    
    # Button actions for the form
    add_btn = ttk.Button(
        button_frame,
        text="➕ Add Sanctuary",
        style="Primary.TButton",
        command=save_sanctuary,
        width=20
    )
    add_btn.pack(side="left", padx=(0, 5))
    
    clear_btn = ttk.Button(
        button_frame,
        text="🗑️ Clear Form",
        style="Info.TButton",
        command=clear_form,
        width=15
    )
    clear_btn.pack(side="left")
    
    # Table section in right frame
    table_frame = tk.LabelFrame(
        right_frame, 
        text=" 🏞️ Sanctuary List ", 
        font=("Segoe UI", 12, "bold"),
        fg=colors["primary"],
        bg=colors["card"],
        padx=15,
        pady=15,
        bd=1,
        relief="solid"
    )
    table_frame.pack(fill="both", expand=True)
    
    # Search bar
    search_frame = tk.Frame(table_frame, bg=colors["card"])
    search_frame.pack(fill="x", pady=(0, 10))
    
    search_label = tk.Label(
        search_frame,
        text="🔍 Search:",
        font=("Segoe UI", 10),
        bg=colors["card"],
        fg=colors["text"]
    )
    search_label.pack(side="left", padx=(0, 5))
    
    search_var = tk.StringVar()
    search_entry = ttk.Entry(
        search_frame, 
        textvariable=search_var,
        font=("Segoe UI", 10),
        width=30
    )
    search_entry.pack(side="left", padx=(0, 5))
    
    def search_sanctuaries(*args):
        """Search sanctuaries by name or location"""
        search_text = search_var.get().strip().lower()
        
        # Clear the tree
        for row in tree.get_children():
            tree.delete(row)
        
        try:
            if search_text:
                # Search query
                cursor.execute(
                    """SELECT * FROM Sanctuary 
                       WHERE LOWER(name) LIKE %s OR LOWER(location) LIKE %s
                       ORDER BY name""",
                    (f"%{search_text}%", f"%{search_text}%")
                )
            else:
                # Show all
                cursor.execute("SELECT * FROM Sanctuary ORDER BY name")
                
            # Display results
            for i, row in enumerate(cursor.fetchall()):
                display_row = [
                    row[0],  # ID
                    row[1],  # Name
                    row[2],  # Location
                    f"{row[3]:.1f}" if row[3] else "-",  # Area
                    row[4] if row[4] else "-",  # Year
                    (row[5][:40] + "...") if row[5] and len(row[5]) > 40 else (row[5] or "-")  # Description
                ]
                tree.insert("", "end", values=display_row, tags=('even' if i % 2 == 0 else 'odd',))
                
        except mysql.connector.Error as err:
            print(f"Search error: {err}")
    
    # Bind search function to entry changes
    search_var.trace("w", search_sanctuaries)
    
    search_btn = ttk.Button(
        search_frame,
        text="Search",
        style="Info.TButton",
        command=search_sanctuaries
    )
    search_btn.pack(side="left")
    
    clear_search_btn = ttk.Button(
        search_frame,
        text="Clear",
        command=lambda: [search_var.set(""), search_entry.focus_set()]
    )
    clear_search_btn.pack(side="left", padx=5)
    
    # Tree view container with scrollbars
    tree_container = tk.Frame(table_frame, bg=colors["card"])
    tree_container.pack(fill="both", expand=True)
    
    # Create vertical scrollbar
    vsb = ttk.Scrollbar(tree_container, orient="vertical")
    vsb.pack(side="right", fill="y")
    
    # Create horizontal scrollbar
    hsb = ttk.Scrollbar(tree_container, orient="horizontal")
    hsb.pack(side="bottom", fill="x")
    
    # Create Treeview
    columns = ("ID", "Name", "Location", "Area", "Year", "Description")
    tree = ttk.Treeview(
        tree_container, 
        columns=columns, 
        show="headings", 
        style="Custom.Treeview",
        selectmode="extended",
        yscrollcommand=vsb.set,
        xscrollcommand=hsb.set
    )
    
    # Configure scrollbars
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)
    
    # Configure column headings
    column_widths = {
        "ID": 50, 
        "Name": 150, 
        "Location": 150, 
        "Area": 80, 
        "Year": 80, 
        "Description": 300
    }
    
    for col, width in column_widths.items():
        tree.heading(col, text=col, anchor="center")
        tree.column(col, width=width, anchor="w" if col in ["Name", "Location", "Description"] else "center")
    
    tree.pack(fill="both", expand=True)
    
    # Configure row colors
    tree.tag_configure('odd', background="#f0f7f0")
    tree.tag_configure('even', background=colors["card"])
    
    # Action buttons for the table
    action_frame = tk.Frame(table_frame, bg=colors["card"], pady=10)
    action_frame.pack(fill="x")
    
    ttk.Button(
        action_frame,
        text="✏️ Edit Selected",
        style="Primary.TButton",
        command=edit_sanctuary
    ).pack(side="left", padx=(0, 5))
    
    ttk.Button(
        action_frame,
        text="❌ Delete Selected",
        style="Danger.TButton",
        command=delete_sanctuary
    ).pack(side="left", padx=5)
    
    ttk.Button(
        action_frame,
        text="🔄 Refresh",
        style="Info.TButton",
        command=refresh_table
    ).pack(side="left", padx=5)
    
    # View details function
    def view_details():
        """Show detailed information for selected sanctuary"""
        selected = tree.selection()
        if not selected or len(selected) > 1:
            messagebox.showwarning("Selection Required", "Please select a single sanctuary to view details.")
            return
        
        # Get the sanctuary ID
        sanctuary_id = tree.item(selected[0])["values"][0]
        
        try:
            # Fetch the sanctuary data
            cursor.execute("SELECT * FROM Sanctuary WHERE id = %s", (sanctuary_id,))
            sanctuary = cursor.fetchone()
            
            if sanctuary:
                # Create a new window for details
                details_win = tk.Toplevel(root)
                details_win.title(f"Sanctuary Details: {sanctuary[1]}")
                details_win.geometry("600x500")
                details_win.configure(bg=colors["card"])
                details_win.grab_set()  # Make modal
                
                # Header
                header = tk.Frame(details_win, bg=colors["primary"], padx=15, pady=15)
                header.pack(fill="x")
                
                tk.Label(
                    header,
                    text=f"🏞️ {sanctuary[1]}",
                    font=("Segoe UI", 16, "bold"),
                    bg=colors["primary"],
                    fg="white"
                ).pack()
                
                # Details container
                details_frame = tk.Frame(details_win, bg=colors["card"], padx=20, pady=20)
                details_frame.pack(fill="both", expand=True)
                
                # Information fields
                info = [
                    {"label": "ID:", "value": sanctuary[0]},
                    {"label": "Name:", "value": sanctuary[1]},
                    {"label": "Location:", "value": sanctuary[2]},
                    {"label": "Area:", "value": f"{sanctuary[3]:.2f} sq km" if sanctuary[3] else "Not specified"},
                    {"label": "Established:", "value": sanctuary[4] if sanctuary[4] else "Not specified"}
                ]
                
                for i, item in enumerate(info):
                    row = tk.Frame(details_frame, bg=colors["card"], pady=8)
                    row.pack(fill="x")
                    
                    tk.Label(
                        row,
                        text=item["label"],
                        font=("Segoe UI", 11, "bold"),
                        width=12,
                        anchor="w",
                        bg=colors["card"],
                        fg=colors["primary"]
                    ).pack(side="left")
                    
                    tk.Label(
                        row,
                        text=item["value"],
                        font=("Segoe UI", 11),
                        anchor="w",
                        bg=colors["card"],
                        fg=colors["text"]
                    ).pack(side="left", fill="x", expand=True)
                
                # Description section
                desc_label = tk.Label(
                    details_frame,
                    text="Description:",
                    font=("Segoe UI", 11, "bold"),
                    anchor="w",
                    bg=colors["card"],
                    fg=colors["primary"]
                )
                desc_label.pack(anchor="w", pady=(15, 5))
                
                desc_text = tk.Text(
                    details_frame,
                    font=("Segoe UI", 11),
                    wrap="word",
                    height=8,
                    bg="#f9f9f9",
                    bd=1,
                    padx=10,
                    pady=10
                )
                desc_text.pack(fill="both", expand=True, pady=(0, 15))
                
                # Insert description text
                desc_text.insert("1.0", sanctuary[5] if sanctuary[5] else "No description available.")
                desc_text.config(state="disabled")  # Make read-only
                
                # Created at timestamp if available
                if len(sanctuary) > 6 and sanctuary[6]:
                    created_at = sanctuary[6].strftime("%Y-%m-%d %H:%M:%S") if hasattr(sanctuary[6], 'strftime') else str(sanctuary[6])
                    
                    tk.Label(
                        details_frame,
                        text=f"Record created: {created_at}",
                        font=("Segoe UI", 9, "italic"),
                        bg=colors["card"],
                        fg=colors["text_light"]
                    ).pack(anchor="e", pady=(0, 10))
                
                # Close button
                tk.Button(
                    details_win,
                    text="Close",
                    font=("Segoe UI", 11, "bold"),
                    bg=colors["primary"],
                    fg="white",
                    padx=20,
                    pady=10,
                    bd=0,
                    cursor="hand2",
                    command=details_win.destroy
                ).pack(pady=15)
            
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to load sanctuary details: {err}")
    
    # Add view details button
    ttk.Button(
        action_frame,
        text="👁️ View Details",
        style="Info.TButton",
        command=view_details
    ).pack(side="left", padx=5)
    
    # Status bar at the bottom
    status_bar = tk.Frame(root, bg=colors["primary"], padx=10, pady=5)
    status_bar.pack(fill="x", side="bottom")
    
    status_text = tk.Label(
        status_bar,
        text="WildGuard Sanctuary Management System v1.0",
        font=("Segoe UI", 8),
        bg=colors["primary"],
        fg="white"
    )
    status_text.pack(side="left")
    
    # Load initial data
    refresh_table()
    
    # Double-click to view details
    tree.bind("<Double-1>", lambda event: view_details())
    
    # Start the main loop
    root.mainloop()
    
    # Clean up
    try:
        cursor.close()
        conn.close()
    except:
        pass