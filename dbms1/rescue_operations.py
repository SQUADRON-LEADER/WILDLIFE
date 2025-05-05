import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import dashboard
from datetime import datetime
from ttkthemes import ThemedTk
from tkcalendar import DateEntry

class RescueOperations:
    def __init__(self, username):
        self.username = username
        self.setup_database()
        
        # Use ThemedTk for modern appearance
        self.root = ThemedTk(theme="arc")  # Modern flat theme
        self.root.title("🚨 WildGuard - Rescue Operations")
        self.root.geometry("1100x680")
        self.root.configure(bg="#f5f7fa")
        
        # Define color scheme
        self.colors = {
            "primary": "#c0392b",     # Rescue red
            "primary_dark": "#a53125", # Darker red for hover
            "secondary": "#3498db",   # Info blue
            "accent": "#f39c12",      # Warning yellow
            "success": "#2ecc71",     # Success green
            "bg": "#f5f7fa",          # Light background
            "card": "#ffffff",        # White card background
            "text": "#34495e",        # Dark text
            "text_light": "#7f8c8d",  # Light text
            "border": "#e0e5ec"       # Border color
        }
        
        # Configure styles
        self.setup_styles()
        
        # Build the interface
        self.create_header_frame()
        self.create_content_frame()
        self.create_footer()
        
        # Load initial data
        self.load_species()
        self.load_data()
        
        # Show statistics after loading data
        self.update_statistics()
        
        # Start the app
        self.root.mainloop()
    
    def setup_database(self):
        """Connect to database and ensure tables exist"""
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="11223344",
                database="WildGuardDB"
            )
            self.cursor = self.conn.cursor()
            
            # Create tables if they don't exist
            self.create_tables_if_needed()
            
            # Verify the notes column exists
            self.check_column_name()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Connection Error", 
                                 f"Failed to connect to database: {str(err)}")
    
    def create_tables_if_needed(self):
        """Create necessary tables if they don't exist"""
        # Create Species table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Species (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                scientific_name VARCHAR(100),
                conservation_status VARCHAR(50),
                habitat VARCHAR(100),
                population INT
            )
        """)
        
        # Create Rescue_Operations table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Rescue_Operations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                species_id INT NOT NULL,
                location VARCHAR(100) NOT NULL,
                rescue_date DATE NOT NULL,
                status VARCHAR(50) NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (species_id) REFERENCES Species(id)
            )
        """)
        
        # No need to check for note vs notes here since we've defined it as 'notes'
        # Just check if the table exists and has data
        
        # Check if Species table has data, add sample data if empty
        self.cursor.execute("SELECT COUNT(*) FROM Species")
        species_count = self.cursor.fetchone()[0]
        
        if species_count == 0:
            # Add sample species data
            sample_species = [
                ("Bengal Tiger", "Panthera tigris tigris", "Endangered", "Forest", 3500),
                ("Asian Elephant", "Elephas maximus", "Endangered", "Forest", 40000),
                ("Indian Rhinoceros", "Rhinoceros unicornis", "Vulnerable", "Grassland", 3600),
                ("Snow Leopard", "Panthera uncia", "Vulnerable", "Mountain", 4000),
                ("Red Panda", "Ailurus fulgens", "Endangered", "Forest", 10000)
            ]
            self.cursor.executemany("""
                INSERT INTO Species (name, scientific_name, conservation_status, habitat, population)
                VALUES (%s, %s, %s, %s, %s)
            """, sample_species)
        
        self.conn.commit()
    
    def setup_styles(self):
        """Configure ttk styles with custom text colors"""
        self.style = ttk.Style()
        
        # Configure Treeview (unchanged)
        self.style.configure(
            "Custom.Treeview",
            background=self.colors["card"],
            foreground=self.colors["text"],
            rowheight=30,
            fieldbackground=self.colors["card"]
        )
        
        # CHANGED BUTTON TEXT COLORS - Each button gets a unique color
        
        # "Add Operation" button - Bright Green Text
        self.style.configure(
        "Primary.TButton",
        font=("Segoe UI", 11, "bold"),
        background=self.colors["primary"],
        foreground="#006600",  # Dark green text
        relief="raised",
        borderwidth=2
       )
        
        # "Clear Form" button - Light Blue Text
        self.style.configure(
        "Secondary.TButton",
        font=("Segoe UI", 11, "bold"),
        background="#1E6091",
        foreground="#003366",  # Dark blue text
        relief="raised",
        borderwidth=2
    )
        
        # "Delete Selected" button - Bright Yellow Text
        self.style.configure(
        "Warning.TButton",
        font=("Segoe UI", 11, "bold"),
        background="#C0392B",
        foreground="#996600",  # Dark gold text
        relief="raised",
        borderwidth=2
    )
        
        # "View Details" button - Light Purple Text
        self.style.configure(
        "Info.TButton",
        font=("Segoe UI", 11, "bold"),
        background="#3498DB",
        foreground="#330066",  # Dark purple text
        relief="raised",
        borderwidth=2
    )
        
        # "Refresh" button - Cyan Text
        self.style.configure(
        "Refresh.TButton",
        font=("Segoe UI", 11, "bold"),
        background="#2980B9",
        foreground="#006666",  # Dark teal text
        relief="raised",
        borderwidth=2
    )
        
        # "Export" button - Orange Text
        self.style.configure(
        "Export.TButton",
        font=("Segoe UI", 11, "bold"),
        background="#8E44AD",
        foreground="#994400",  # Dark orange text
        relief="raised",
        borderwidth=2
    )
    
    def create_header_frame(self):
        """Create the application header"""
        header_frame = tk.Frame(self.root, bg=self.colors["primary"], padx=20, pady=15)
        header_frame.pack(fill="x")
        
        # App title with rescue symbol
        title_frame = tk.Frame(header_frame, bg=self.colors["primary"])
        title_frame.pack(side="left")
        
        title_label = tk.Label(
            title_frame,
            text="🚨 Rescue Operations Management",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg=self.colors["primary"]
        )
        title_label.pack(side="left")
        
        # User info in header
        user_frame = tk.Frame(header_frame, bg=self.colors["primary"])
        user_frame.pack(side="right")
        
        user_label = tk.Label(
            user_frame,
            text=f"👤 Logged in: {self.username}",
            font=("Segoe UI", 10),
            fg="white",
            bg=self.colors["primary"]
        )
        user_label.pack()
    
    def create_content_frame(self):
        """Create the main content area"""
        self.content_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=20, pady=20)
        self.content_frame.pack(fill="both", expand=True)
        
        # Create left panel (form and stats)
        self.left_panel = tk.Frame(self.content_frame, bg=self.colors["bg"])
        self.left_panel.pack(side="left", fill="both", expand=False, padx=(0, 10))
        
        # Create right panel (table)
        self.right_panel = tk.Frame(self.content_frame, bg=self.colors["bg"])
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        # Add components to each panel
        self.create_form_card()
        self.create_stats_card()
        self.create_table_card()
    
    def create_form_card(self):
        """Create the form for adding new rescue operations"""
        form_card = tk.LabelFrame(
            self.left_panel,
            text=" 🆘 New Rescue Operation ",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["primary"],
            bg=self.colors["card"],
            padx=15,
            pady=15,
            bd=1,
            relief="solid"
        )
        form_card.pack(fill="x", pady=(0, 15))
        
        # Form header
        header_label = tk.Label(
            form_card,
            text="Enter rescue details below:",
            font=("Segoe UI", 10),
            fg=self.colors["text_light"],
            bg=self.colors["card"]
        )
        header_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Species selection
        tk.Label(
            form_card, 
            text="Species:",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["card"]
        ).grid(row=1, column=0, sticky="w", pady=8)
        
        self.species_combo = ttk.Combobox(
            form_card,
            font=("Segoe UI", 10),
            state="readonly",
            width=25
        )
        self.species_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=8)
        
        # Location field
        tk.Label(
            form_card,
            text="Location:",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["card"]
        ).grid(row=2, column=0, sticky="w", pady=8)
        
        self.location_entry = ttk.Entry(form_card, font=("Segoe UI", 10), width=25)
        self.location_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=8)
        
        # Date field (using DateEntry for better date selection)
        tk.Label(
            form_card,
            text="Rescue Date:",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["card"]
        ).grid(row=3, column=0, sticky="w", pady=8)
        
        self.date_entry = DateEntry(
            form_card,
            font=("Segoe UI", 10),
            width=23,
            background=self.colors["primary"],
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-mm-dd"
        )
        self.date_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=8)
        
        # Status dropdown (instead of free text)
        tk.Label(
            form_card,
            text="Status:",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["card"]
        ).grid(row=4, column=0, sticky="w", pady=8)
        
        status_options = ["In Progress", "Completed", "Failed", "Monitoring", "Follow-up Needed"]
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(
            form_card,
            font=("Segoe UI", 10),
            textvariable=self.status_var,
            values=status_options,
            state="readonly",
            width=25
        )
        self.status_combo.current(0)
        self.status_combo.grid(row=4, column=1, sticky="ew", padx=5, pady=8)
        
        # Notes field
        tk.Label(
            form_card,
            text="Notes:",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["card"]
        ).grid(row=5, column=0, sticky="nw", pady=8)
        
        self.notes_entry = tk.Text(
            form_card,
            font=("Segoe UI", 10),
            height=4,
            width=25,
            wrap="word"
        )
        self.notes_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=8)
        
        # Button frame for better alignment
        button_frame = tk.Frame(form_card, bg=self.colors["card"])
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Add Operation button - GREEN TEXT
        add_btn = ttk.Button(
            button_frame,
            text="➕ Add Operation",
            style="Primary.TButton",  # Light green text
            command=self.add_operation,
            width=20
        )
        add_btn.pack(side="left", padx=5)
        
        # Clear Form button - BLUE TEXT
        clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Clear Form",
            style="Secondary.TButton",  # Light blue text
            command=self.clear_fields,
            width=15
        )
        clear_btn.pack(side="left", padx=5)
    
    def create_stats_card(self):
        """Create statistics display card"""
        stats_card = tk.LabelFrame(
            self.left_panel,
            text=" 📊 Rescue Statistics ",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["secondary"],
            bg=self.colors["card"],
            padx=15,
            pady=15,
            bd=1,
            relief="solid"
        )
        stats_card.pack(fill="x")
        
        # Stats grid
        self.stats_frame = tk.Frame(stats_card, bg=self.colors["card"])
        self.stats_frame.pack(fill="x")
        
        # Create placeholders for statistics
        self.total_rescues_label = self.create_stat(0, "Total Rescues", "🔢")
        self.in_progress_label = self.create_stat(1, "In Progress", "⏳")
        self.completed_label = self.create_stat(2, "Completed", "✅")
        self.most_rescued_label = self.create_stat(3, "Most Rescued Species", "🦁")
    
    def create_stat(self, row, label_text, icon):
        """Create a statistic display"""
        frame = tk.Frame(self.stats_frame, bg=self.colors["card"], padx=5, pady=5)
        frame.grid(row=row, column=0, sticky="ew", pady=5)
        
        label = tk.Label(
            frame,
            text=f"{icon} {label_text}:",
            font=("Segoe UI", 10),
            fg=self.colors["text"],
            bg=self.colors["card"],
            anchor="w"
        )
        label.pack(side="left")
        
        value_label = tk.Label(
            frame,
            text="Loading...",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors["secondary"],
            bg=self.colors["card"]
        )
        value_label.pack(side="right", padx=10)
        
        return value_label
    
    def create_table_card(self):
        """Create the operations table display"""
        table_card = tk.LabelFrame(
            self.right_panel,
            text=" 📋 Rescue Operations ",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["text"],
            bg=self.colors["card"],
            padx=15,
            pady=15,
            bd=1,
            relief="solid"
        )
        table_card.pack(fill="both", expand=True)
        
        # Table with scrollbars
        table_frame = tk.Frame(table_card, bg=self.colors["card"])
        table_frame.pack(fill="both", expand=True, pady=10)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame)
        y_scrollbar.pack(side="right", fill="y")
        
        x_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")
        
        # Create treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Species", "Location", "Date", "Status", "Notes"),
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        
        # Configure scrollbars
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        # Define columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Species", text="Species")
        self.tree.heading("Location", text="Location")
        self.tree.heading("Date", text="Rescue Date")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Notes", text="Notes")
        
        # Set column widths
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Species", width=130)
        self.tree.column("Location", width=150)
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Notes", width=200)
        
        self.tree.pack(fill="both", expand=True)
        
        # Button frame below table
        button_frame = tk.Frame(table_card, bg=self.colors["card"], pady=10)
        button_frame.pack(fill="x")
        
        # Delete button - YELLOW TEXT
        delete_btn = ttk.Button(
            button_frame,
            text="🗑️ Delete Selected",
            style="Warning.TButton",  # Light yellow text
            command=self.delete_operation
        )
        delete_btn.pack(side="left", padx=5)
        
        # View Details button - PURPLE TEXT
        view_btn = ttk.Button(
            button_frame,
            text="🔍 View Details",
            style="Info.TButton",  # Light purple text
            command=self.view_operation_details
        )
        view_btn.pack(side="left", padx=5)
        
        # Export button - ORANGE TEXT
        export_btn = ttk.Button(
            button_frame,
            text="📊 Export Data",
            style="Export.TButton",  # Light orange text 
            command=self.export_data
        )
        export_btn.pack(side="right", padx=5)
        
        # Refresh button - CYAN TEXT
        refresh_btn = ttk.Button(
            button_frame,
            text="🔄 Refresh",
            style="Refresh.TButton",  # Cyan text
            command=self.load_data
        )
        refresh_btn.pack(side="right", padx=5)
    
    def create_footer(self):
        """Create application footer"""
        footer_frame = tk.Frame(self.root, bg=self.colors["primary"], padx=20, pady=15)
        footer_frame.pack(fill="x", side="bottom")
        
        # Back to dashboard button with improved contrast
        back_btn = tk.Button(
            footer_frame,
            text="⬅️ Back to Dashboard",
            font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF",  # Pure white text
            bg="#8B0000",  # Dark red background (more distinct)
            padx=15,
            pady=8,
            bd=1,
            relief="raised",  # Added relief
            cursor="hand2",
            command=self.back_to_dashboard,
            activebackground="#6B0000",  # Even darker when clicked
            activeforeground="#FFFFFF"
        )
        back_btn.pack(side="left")
        
        # App version info
        version_label = tk.Label(
            footer_frame,
            text="WildGuard v1.0.2 © 2023",
            font=("Segoe UI", 8),
            fg="white",
            bg=self.colors["primary"]
        )
        version_label.pack(side="right")
    
    def load_species(self):
        """Load species from database for dropdown"""
        try:
            self.cursor.execute("SELECT id, name FROM Species ORDER BY name")
            results = self.cursor.fetchall()
            
            self.species_map = {name: id for id, name in results}
            self.species_combo["values"] = list(self.species_map.keys())
            
            if self.species_map:
                self.species_combo.current(0)
                
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not load species: {str(err)}")
    
    def check_column_name(self):
        """Check if the notes column exists and create it if missing"""
        try:
            # Get columns with improved error handling
            self.cursor.execute("SHOW COLUMNS FROM Rescue_Operations")
            columns = [column[0].lower() for column in self.cursor.fetchall()]
            
            # Print available columns for debugging
            print(f"Available columns: {', '.join(columns)}")
            
            # Check if notes column exists
            if 'notes' in columns:
                return 'notes'
            elif 'note' in columns:
                return 'note'
            else:
                # Column doesn't exist - add it
                print("Notes column missing - adding it now")
                self.cursor.execute("ALTER TABLE Rescue_Operations ADD COLUMN notes TEXT")
                self.conn.commit()
                print("Added 'notes' column successfully")
                return 'notes'
                    
        except mysql.connector.Error as err:
            print(f"Column verification error: {err}")
            # Try to create the entire table from scratch
            self.recreate_rescue_operations_table()
            return 'notes'  # Default after recreation

    def recreate_rescue_operations_table(self):
        """Recreate the table if seriously damaged"""
        try:
            print("Attempting to recreate the Rescue_Operations table...")
            
            # Drop and recreate
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Rescue_Operations_New (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    species_id INT NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    rescue_date DATE NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (species_id) REFERENCES Species(id)
                )
            """)
            
            # Try to migrate data if old table exists
            try:
                self.cursor.execute("""
                    INSERT INTO Rescue_Operations_New 
                    (species_id, location, rescue_date, status, created_at)
                    SELECT species_id, location, rescue_date, status, created_at 
                    FROM Rescue_Operations
                """)
                print("Migrated existing data to new table")
            except:
                print("Could not migrate data - creating fresh table")
            
            # Replace old table with new one
            self.cursor.execute("DROP TABLE IF EXISTS Rescue_Operations")
            self.cursor.execute("RENAME TABLE Rescue_Operations_New TO Rescue_Operations")
            self.conn.commit()
            print("Rescue_Operations table successfully recreated")
            
        except mysql.connector.Error as err:
            print(f"Failed to recreate table: {err}")

    def load_data(self):
        """Load rescue operations from database"""
        try:
            # Clear existing data
            self.tree.delete(*self.tree.get_children())
            
            # Check column name first
            notes_column = self.check_column_name() or "notes"
            
            # Get operations with species names - using dynamic column name
            query = f"""
                SELECT R.id, S.name, R.location, R.rescue_date, R.status, R.{notes_column}
                FROM Rescue_Operations R
                JOIN Species S ON R.species_id = S.id
                ORDER BY R.rescue_date DESC
            """
            self.cursor.execute(query)
            
            # Add alternating row colors for better readability
            i = 0
            for row in self.cursor.fetchall():
                row_values = (
                    row[0],
                    row[1],
                    row[2],
                    row[3].strftime('%Y-%m-%d') if row[3] else "",
                    row[4],
                    (row[5][:30] + "...") if row[5] and len(row[5]) > 30 else row[5] or ""
                )
                
                # Tag for alternating colors
                tag = "even" if i % 2 == 0 else "odd"
                
                # Add status-based tag
                status = row[4].lower() if row[4] else ""
                if "progress" in status:
                    status_tag = "in_progress"
                elif "complete" in status:
                    status_tag = "completed"
                elif "fail" in status:
                    status_tag = "failed"
                else:
                    status_tag = "other"
                
                self.tree.insert("", "end", values=row_values, tags=(tag, status_tag))
                i += 1
            
            # Configure row tags
            self.tree.tag_configure("even", background="#ffffff")
            self.tree.tag_configure("odd", background="#f9f9f9")
            self.tree.tag_configure("in_progress", foreground="#f39c12")  # Orange for in progress
            self.tree.tag_configure("completed", foreground="#2ecc71")    # Green for completed
            self.tree.tag_configure("failed", foreground="#e74c3c")       # Red for failed
            
            # Update statistics
            self.update_statistics()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not load data: {str(err)}")
    
    def update_statistics(self):
        """Update rescue operation statistics"""
        try:
            # Total rescues
            self.cursor.execute("SELECT COUNT(*) FROM Rescue_Operations")
            total = self.cursor.fetchone()[0]
            self.total_rescues_label.config(text=str(total))
            
            # In progress
            self.cursor.execute("SELECT COUNT(*) FROM Rescue_Operations WHERE status LIKE '%progress%'")
            in_progress = self.cursor.fetchone()[0]
            self.in_progress_label.config(text=str(in_progress))
            
            # Completed
            self.cursor.execute("SELECT COUNT(*) FROM Rescue_Operations WHERE status LIKE '%complete%'")
            completed = self.cursor.fetchone()[0]
            self.completed_label.config(text=str(completed))
            
            # Most rescued species
            query = """
                SELECT S.name, COUNT(*) as count
                FROM Rescue_Operations R
                JOIN Species S ON R.species_id = S.id
                GROUP BY S.name
                ORDER BY count DESC
                LIMIT 1
            """
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            if result:
                self.most_rescued_label.config(text=f"{result[0]} ({result[1]})")
            else:
                self.most_rescued_label.config(text="None")
                
        except mysql.connector.Error as err:
            print(f"Error updating statistics: {str(err)}")
    
    def add_operation(self):
        """Add a new rescue operation"""
        species_name = self.species_combo.get()
        location = self.location_entry.get().strip()
        date = self.date_entry.get_date()
        status = self.status_combo.get()
        notes = self.notes_entry.get("1.0", tk.END).strip()
        
        # Validate input
        if not species_name:
            messagebox.showwarning("Input Error", "Please select a species.")
            self.species_combo.focus_set()
            return
            
        if not location:
            messagebox.showwarning("Input Error", "Please enter a location.")
            self.location_entry.focus_set()
            return
            
        if not status:
            messagebox.showwarning("Input Error", "Please select a status.")
            self.status_combo.focus_set()
            return
        
        # Get species ID
        species_id = self.species_map.get(species_name)
        if not species_id:
            messagebox.showerror("Error", "Invalid species selected.")
            return
        
        try:
            # Format date for insertion
            formatted_date = date.strftime('%Y-%m-%d')
            
            # Insert the new operation
            self.cursor.execute(
                """
                INSERT INTO Rescue_Operations 
                (species_id, location, rescue_date, status, notes)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (species_id, location, formatted_date, status, notes)
            )
            self.conn.commit()
            
            # Update UI
            self.load_data()
            self.clear_fields()
            
            # Show success message
            messagebox.showinfo("Success", "Rescue operation added successfully!")
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not add operation: {str(err)}")
    
    def delete_operation(self):
        """Delete selected rescue operation"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an operation to delete.")
            return
            
        # Get details for confirmation
        values = self.tree.item(selected)['values']
        rescue_id = values[0]
        species = values[1]
        location = values[2]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete this rescue operation?\n\n"
            f"ID: {rescue_id}\n"
            f"Species: {species}\n"
            f"Location: {location}\n\n"
            "This action cannot be undone.",
            icon="warning"
        )
        
        if confirm:
            try:
                self.cursor.execute("DELETE FROM Rescue_Operations WHERE id = %s", (rescue_id,))
                self.conn.commit()
                self.load_data()
                messagebox.showinfo("Success", "Rescue operation deleted successfully.")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Could not delete operation: {str(err)}")
    
    def view_operation_details(self):
        """View detailed information about selected operation"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an operation to view.")
            return
            
        # Get operation ID
        rescue_id = self.tree.item(selected)['values'][0]
        
        try:
            # Get detailed information
            query = """
                SELECT 
                    R.id, 
                    S.name, 
                    S.scientific_name,
                    S.conservation_status,
                    R.location, 
                    R.rescue_date, 
                    R.status, 
                    R.notes,
                    R.created_at
                FROM Rescue_Operations R
                JOIN Species S ON R.species_id = S.id
                WHERE R.id = %s
            """
            self.cursor.execute(query, (rescue_id,))
            result = self.cursor.fetchone()
            
            if not result:
                messagebox.showinfo("Not Found", "Operation details not found.")
                return
                
            # Create details window
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Rescue Operation #{result[0]} Details")
            details_window.geometry("500x500")
            details_window.configure(bg=self.colors["card"])
            details_window.grab_set()  # Make window modal
            
            # Window header
            header_frame = tk.Frame(details_window, bg=self.colors["primary"], padx=15, pady=10)
            header_frame.pack(fill="x")
            
            header_label = tk.Label(
                header_frame,
                text=f"Rescue Operation #{result[0]}",
                font=("Segoe UI", 14, "bold"),
                fg="white",
                bg=self.colors["primary"]
            )
            header_label.pack()
            
            # Content frame
            content_frame = tk.Frame(details_window, bg=self.colors["card"], padx=20, pady=20)
            content_frame.pack(fill="both", expand=True)
            
            # Operation details
            fields = [
                ("Species", result[1]),
                ("Scientific Name", result[2] or "N/A"),
                ("Conservation Status", result[3] or "N/A"),
                ("Location", result[4]),
                ("Rescue Date", result[5].strftime('%Y-%m-%d') if result[5] else "N/A"),
                ("Status", result[6]),
                ("Record Created", result[8].strftime('%Y-%m-%d %H:%M:%S') if result[8] else "N/A")
            ]
            
            for i, (field, value) in enumerate(fields):
                tk.Label(
                    content_frame,
                    text=f"{field}:",
                    font=("Segoe UI", 10, "bold"),
                    fg=self.colors["text"],
                    bg=self.colors["card"],
                    anchor="w"
                ).grid(row=i, column=0, sticky="w", pady=5)
                
                tk.Label(
                    content_frame,
                    text=str(value),
                    font=("Segoe UI", 10),
                    fg=self.colors["text"],
                    bg=self.colors["card"],
                    anchor="w"
                ).grid(row=i, column=1, sticky="w", padx=10, pady=5)
            
            # Notes section
            tk.Label(
                content_frame,
                text="Notes:",
                font=("Segoe UI", 10, "bold"),
                fg=self.colors["text"],
                bg=self.colors["card"],
                anchor="w"
            ).grid(row=len(fields), column=0, sticky="nw", pady=5)
            
            notes_text = tk.Text(
                content_frame,
                font=("Segoe UI", 10),
                bg="#f9f9f9",
                wrap="word",
                height=6,
                width=40
            )
            notes_text.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=5)
            notes_text.insert("1.0", result[7] or "No notes available.")
            notes_text.config(state="disabled")  # Make read-only
            
            # Close button
            close_btn = tk.Button(
                details_window,
                text="Close",
                font=("Segoe UI", 11, "bold"),  # Larger font
                bg="#8B0000",  # Darker red
                fg="#FFFFFF",  # Pure white
                padx=20,
                pady=8,
                bd=2,  # Thicker border
                relief="raised",
                cursor="hand2",
                activebackground="#6B0000",
                activeforeground="#FFFFFF",
                command=details_window.destroy
            )
            close_btn.pack(pady=15)
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not load operation details: {str(err)}")
    
    def export_data(self):
        """Export rescue operations data to CSV"""
        try:
            import csv
            from tkinter import filedialog
            from datetime import datetime
            
            # Ask for file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="Export Rescue Operations Data"
            )
            
            if not filename:  # User cancelled
                return
                
            # Get all data for export
            query = """
                SELECT 
                    R.id, 
                    S.name, 
                    S.scientific_name,
                    S.conservation_status, 
                    R.location, 
                    R.rescue_date, 
                    R.status, 
                    R.notes,
                    R.created_at
                FROM Rescue_Operations R
                JOIN Species S ON R.species_id = S.id
                ORDER BY R.rescue_date DESC
            """
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow([
                    "ID", "Species", "Scientific Name", "Conservation Status",
                    "Location", "Rescue Date", "Status", "Notes", "Record Created"
                ])
                
                # Write data rows
                for row in results:
                    # Format dates for CSV
                    rescue_date = row[5].strftime('%Y-%m-%d') if row[5] else ""
                    created_at = row[8].strftime('%Y-%m-%d %H:%M:%S') if row[8] else ""
                    
                    writer.writerow([
                        row[0], row[1], row[2] or "", row[3] or "", 
                        row[4], rescue_date, row[6], row[7] or "", created_at
                    ])
            
            messagebox.showinfo(
                "Export Complete", 
                f"Successfully exported {len(results)} rescue operations to {filename}"
            )
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def clear_fields(self):
        """Clear all form fields"""
        # Reset dropdown to first item if options exist
        if self.species_combo["values"]:
            self.species_combo.current(0)
        
        self.location_entry.delete(0, tk.END)
        self.date_entry.set_date(datetime.now())  # Reset to today
        self.status_combo.current(0)  # Reset to first status
        self.notes_entry.delete("1.0", tk.END)
    
    def back_to_dashboard(self):
        """Return to dashboard"""
        self.root.destroy()
        dashboard.Dashboard(self.username)


def run(username="Admin"):
    """Function to start the Rescue Operations module"""
    try:
        # Before creating UI, check if required packages are installed
        import tkcalendar
        RescueOperations(username)
    except ImportError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Missing Dependency",
            "This module requires additional packages. Please install:\n\n"
            "pip install tkcalendar ttkthemes"
        )
        print(f"Import Error: {str(e)}")
        root.destroy()
    except Exception as e:
        import traceback
        traceback.print_exc()
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to start Rescue Operations: {str(e)}")
        root.destroy()


# Run the application when executed directly
if __name__ == "__main__":
    run()
