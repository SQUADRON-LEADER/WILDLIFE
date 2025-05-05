import tkinter as tk
from tkinter import ttk, messagebox, StringVar
import mysql.connector
import dashboard

class SpeciesSanctuary:
    def __init__(self, username):
        self.username = username
        
        # Connect to database
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="11223344",
                database="WildGuardDB"
            )
            self.cursor = self.conn.cursor()
            
            # Ensure table exists
            self.create_table_if_needed()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Connection Error", f"Failed to connect: {err}")
            return
            
        # Set up the main window
        self.root = tk.Tk()
        self.root.title("Species & Sanctuary Mapping - WildGuard")
        self.root.geometry("1050x650")
        self.root.configure(bg="#f5f7fa")
        
        # Define color scheme
        self.colors = {
            "primary": "#2c3e50",    # Dark blue
            "secondary": "#27ae60",  # Green
            "accent": "#e74c3c",     # Red
            "bg": "#f5f7fa",         # Light background
            "card": "#ffffff",       # White card
            "text": "#2c3e50",       # Dark text
            "text_light": "#7f8c8d", # Light text
            "border": "#ecf0f1"      # Light border
        }
        
        # Set up the UI components
        self.setup_ui()
        
        # Load data from database
        self.load_data()
        self.load_species_data()
        self.load_sanctuary_data()
        
        # Start the main loop
        self.root.mainloop()

    def create_table_if_needed(self):
        """Create the mapping table if it doesn't exist"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Species_Sanctuary (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    species_id INT NOT NULL,
                    sanctuary_id INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_mapping (species_id, sanctuary_id),
                    FOREIGN KEY (species_id) REFERENCES Species(id) ON DELETE CASCADE,
                    FOREIGN KEY (sanctuary_id) REFERENCES Sanctuary(id) ON DELETE CASCADE
                )
            """)
            self.conn.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to create table: {err}")

    def setup_ui(self):
        """Set up the user interface"""
        # Create header
        header_frame = tk.Frame(self.root, bg=self.colors["primary"], padx=20, pady=15)
        header_frame.pack(fill="x")
        
        title = tk.Label(
            header_frame, 
            text="🐾 Species & Sanctuary Mapping", 
            font=("Segoe UI", 18, "bold"), 
            bg=self.colors["primary"], 
            fg="white"
        )
        title.pack(side="left")
        
        user_label = tk.Label(
            header_frame, 
            text=f"Logged in as: {self.username}", 
            font=("Segoe UI", 10), 
            bg=self.colors["primary"], 
            fg="white"
        )
        user_label.pack(side="right")
        
        # Main content area with 2-column layout
        content_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Left panel for form
        left_frame = tk.Frame(content_frame, bg=self.colors["bg"], width=350)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)  # Prevent shrinking
        
        # Right panel for table
        right_frame = tk.Frame(content_frame, bg=self.colors["bg"])
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Species selection card
        species_card = tk.LabelFrame(
            left_frame,
            text=" 🦁 Select Species ",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["primary"],
            bg=self.colors["card"],
            padx=15,
            pady=15,
            bd=1,
            relief="solid"
        )
        species_card.pack(fill="x", pady=(0, 10))
        
        # Species dropdown
        species_frame = tk.Frame(species_card, bg=self.colors["card"], pady=5)
        species_frame.pack(fill="x")
        
        tk.Label(
            species_frame, 
            text="Species:", 
            font=("Segoe UI", 10, "bold"), 
            bg=self.colors["card"], 
            fg=self.colors["text"]
        ).pack(anchor="w", pady=(0, 5))
        
        # Species search and selection
        search_species_frame = tk.Frame(species_card, bg=self.colors["card"])
        search_species_frame.pack(fill="x", pady=5)
        
        self.species_search_var = StringVar()
        self.species_search_entry = ttk.Entry(
            search_species_frame, 
            textvariable=self.species_search_var, 
            font=("Segoe UI", 10), 
            width=20
        )
        self.species_search_entry.pack(side="left", fill="x", expand=True)
        
        search_species_btn = tk.Button(
            search_species_frame, 
            text="🔍", 
            font=("Segoe UI", 10), 
            bg=self.colors["primary"], 
            fg="white",
            command=self.filter_species
        )
        search_species_btn.pack(side="right", padx=(5, 0))
        
        # Species listbox with scrollbar
        species_list_frame = tk.Frame(species_card, bg=self.colors["card"])
        species_list_frame.pack(fill="both", expand=True, pady=5)
        
        species_scrollbar = tk.Scrollbar(species_list_frame)
        species_scrollbar.pack(side="right", fill="y")
        
        self.species_listbox = tk.Listbox(
            species_list_frame,
            font=("Segoe UI", 10),
            height=6,
            selectmode="single",
            yscrollcommand=species_scrollbar.set
        )
        self.species_listbox.pack(side="left", fill="both", expand=True)
        species_scrollbar.config(command=self.species_listbox.yview)
        
        # Add species management buttons
        species_mgmt_frame = tk.Frame(species_card, bg=self.colors["card"], pady=5)
        species_mgmt_frame.pack(fill="x", pady=(5, 0))
        
        # Add species button
        add_species_btn = tk.Button(
            species_mgmt_frame,
            text="➕ Add New Species",
            font=("Segoe UI", 9),
            bg=self.colors["secondary"],
            fg="white",
            padx=5,
            pady=3,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.add_new_species
        )
        add_species_btn.pack(side="left", padx=(0, 5))
        
        # Delete species button
        delete_species_btn = tk.Button(
            species_mgmt_frame,
            text="🗑️ Delete Species",
            font=("Segoe UI", 9),
            bg=self.colors["accent"],
            fg="white",
            padx=5,
            pady=3,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.delete_selected_species
        )
        delete_species_btn.pack(side="right")
        
        # Sanctuary selection card
        sanctuary_card = tk.LabelFrame(
            left_frame,
            text=" 🏞️ Select Sanctuary ",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["primary"],
            bg=self.colors["card"],
            padx=15,
            pady=15,
            bd=1,
            relief="solid"
        )
        sanctuary_card.pack(fill="x", pady=(0, 10))
        
        # Sanctuary dropdown
        sanctuary_frame = tk.Frame(sanctuary_card, bg=self.colors["card"], pady=5)
        sanctuary_frame.pack(fill="x")
        
        tk.Label(
            sanctuary_frame, 
            text="Sanctuary:", 
            font=("Segoe UI", 10, "bold"), 
            bg=self.colors["card"], 
            fg=self.colors["text"]
        ).pack(anchor="w", pady=(0, 5))
        
        # Sanctuary search and selection
        search_sanctuary_frame = tk.Frame(sanctuary_card, bg=self.colors["card"])
        search_sanctuary_frame.pack(fill="x", pady=5)
        
        self.sanctuary_search_var = StringVar()
        self.sanctuary_search_entry = ttk.Entry(
            search_sanctuary_frame, 
            textvariable=self.sanctuary_search_var, 
            font=("Segoe UI", 10), 
            width=20
        )
        self.sanctuary_search_entry.pack(side="left", fill="x", expand=True)
        
        search_sanctuary_btn = tk.Button(
            search_sanctuary_frame, 
            text="🔍", 
            font=("Segoe UI", 10), 
            bg=self.colors["primary"], 
            fg="white",
            command=self.filter_sanctuaries
        )
        search_sanctuary_btn.pack(side="right", padx=(5, 0))
        
        # Sanctuary listbox with scrollbar
        sanctuary_list_frame = tk.Frame(sanctuary_card, bg=self.colors["card"])
        sanctuary_list_frame.pack(fill="both", expand=True, pady=5)
        
        sanctuary_scrollbar = tk.Scrollbar(sanctuary_list_frame)
        sanctuary_scrollbar.pack(side="right", fill="y")
        
        self.sanctuary_listbox = tk.Listbox(
            sanctuary_list_frame,
            font=("Segoe UI", 10),
            height=6,
            selectmode="single",
            yscrollcommand=sanctuary_scrollbar.set
        )
        self.sanctuary_listbox.pack(side="left", fill="both", expand=True)
        sanctuary_scrollbar.config(command=self.sanctuary_listbox.yview)
        
        # Add sanctuary management buttons
        sanctuary_mgmt_frame = tk.Frame(sanctuary_card, bg=self.colors["card"], pady=5)
        sanctuary_mgmt_frame.pack(fill="x", pady=(5, 0))
        
        # Add sanctuary button
        add_sanctuary_btn = tk.Button(
            sanctuary_mgmt_frame,
            text="➕ Add New Sanctuary",
            font=("Segoe UI", 9),
            bg=self.colors["secondary"],
            fg="white",
            padx=5,
            pady=3,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.add_new_sanctuary
        )
        add_sanctuary_btn.pack(side="left", padx=(0, 5))
        
        # Delete sanctuary button
        delete_sanctuary_btn = tk.Button(
            sanctuary_mgmt_frame,
            text="🗑️ Delete Sanctuary",
            font=("Segoe UI", 9),
            bg=self.colors["accent"],
            fg="white",
            padx=5,
            pady=3,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.delete_selected_sanctuary
        )
        delete_sanctuary_btn.pack(side="right")
        
        # Action buttons card
        action_card = tk.LabelFrame(
            left_frame,
            text=" 🔗 Actions ",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["primary"],
            bg=self.colors["card"],
            padx=15,
            pady=15,
            bd=1,
            relief="solid"
        )
        action_card.pack(fill="x")
        
        # Status message
        self.status_var = StringVar()
        status_label = tk.Label(
            action_card,
            textvariable=self.status_var,
            font=("Segoe UI", 9, "italic"),
            bg=self.colors["card"],
            fg=self.colors["text_light"]
        )
        status_label.pack(fill="x", pady=(0, 10))
        
        # Action buttons
        buttons_frame = tk.Frame(action_card, bg=self.colors["card"])
        buttons_frame.pack(fill="x")
        
        link_btn = tk.Button(
            buttons_frame,
            text="🔗 Link Species to Sanctuary",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["secondary"],
            fg="white",
            padx=15,
            pady=8,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.add_link
        )
        link_btn.pack(fill="x", pady=(0, 5))
        
        delete_btn = tk.Button(
            buttons_frame,
            text="🗑️ Remove Selected Link",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["accent"],
            fg="white",
            padx=15,
            pady=8,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.delete_link
        )
        delete_btn.pack(fill="x", pady=5)
        
        refresh_btn = tk.Button(
            buttons_frame,
            text="🔄 Refresh Data",
            font=("Segoe UI", 10),
            bg=self.colors["primary"],
            fg="white",
            padx=15,
            pady=8,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.refresh_all_data
        )
        refresh_btn.pack(fill="x", pady=5)
        
        # Add a more prominent Add/Delete section to the buttons_frame
        button_section = tk.Frame(action_card, bg=self.colors["card"], pady=10)
        button_section.pack(fill="x", pady=10)
        
        # Add bold labels to make the actions clearer
        action_label = tk.Label(
            button_section,
            text="Quick Actions:",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["card"],
            fg=self.colors["primary"]
        )
        action_label.pack(anchor="w", pady=(0, 8))
        
        # Create a row for the new add/delete buttons
        quick_buttons = tk.Frame(button_section, bg=self.colors["card"])
        quick_buttons.pack(fill="x")
        
        # Add button with icon - more visible
        add_btn = tk.Button(
            quick_buttons,
            text="➕ Add Mapping",
            font=("Segoe UI", 10, "bold"),
            bg="#27ae60",  # Bright green
            fg="white",
            padx=15,
            pady=8,
            bd=0,
            relief="raised",
            cursor="hand2",
            activebackground="#219653",
            activeforeground="white",
            command=self.trigger_add_link
        )
        add_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Delete button with icon - more visible
        del_btn = tk.Button(
            quick_buttons,
            text="❌ Delete Mapping",
            font=("Segoe UI", 10, "bold"),
            bg="#e74c3c",  # Bright red
            fg="white",
            padx=15,
            pady=8,
            bd=0,
            relief="raised",
            cursor="hand2",
            activebackground="#c0392b",
            activeforeground="white",
            command=self.trigger_delete_link
        )
        del_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Table card in right frame
        table_card = tk.LabelFrame(
            right_frame,
            text=" 📋 Species-Sanctuary Mappings ",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["primary"],
            bg=self.colors["card"],
            padx=15,
            pady=15,
            bd=1,
            relief="solid"
        )
        table_card.pack(fill="both", expand=True)
        
        # Search bar for table
        search_frame = tk.Frame(table_card, bg=self.colors["card"], pady=5)
        search_frame.pack(fill="x")
        
        tk.Label(
            search_frame, 
            text="🔍 Search:", 
            font=("Segoe UI", 10), 
            bg=self.colors["card"], 
            fg=self.colors["text"]
        ).pack(side="left", padx=(0, 5))
        
        self.search_var = StringVar()
        self.search_var.trace("w", self.search_mapping)
        
        search_entry = ttk.Entry(
            search_frame, 
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            width=30
        )
        search_entry.pack(side="left", fill="x", expand=True)
        
        # Treeview with scrollbars
        tree_frame = tk.Frame(table_card, bg=self.colors["card"])
        tree_frame.pack(fill="both", expand=True, pady=10)
        
        # Create scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        y_scrollbar.pack(side="right", fill="y")
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")
        
        # Configure treeview style
        style = ttk.Style()
        style.configure(
            "Treeview", 
            background=self.colors["card"],
            foreground=self.colors["text"],
            rowheight=25,
            fieldbackground=self.colors["card"],
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background=self.colors["primary"],
            foreground="white"
        )
        style.map("Treeview", background=[("selected", self.colors["secondary"])])
        
        # Add error style for treeview
        style.configure(
            "Error.Treeview", 
            background="#ffe0e0",
            foreground=self.colors["text"],
            rowheight=25,
            fieldbackground="#ffe0e0",
            font=("Segoe UI", 10)
        )
        
        # Create treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Species ID", "Species Name", "Sanctuary ID", "Sanctuary Name"),
            show="headings",
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        
        # Configure scrollbars
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading("ID", text="Mapping ID", command=lambda: self.sort_treeview(self.tree, "ID", False))
        self.tree.heading("Species ID", text="Species ID", command=lambda: self.sort_treeview(self.tree, "Species ID", False))
        self.tree.heading("Species Name", text="Species Name", command=lambda: self.sort_treeview(self.tree, "Species Name", False))
        self.tree.heading("Sanctuary ID", text="Sanctuary ID", command=lambda: self.sort_treeview(self.tree, "Sanctuary ID", False))
        self.tree.heading("Sanctuary Name", text="Sanctuary Name", command=lambda: self.sort_treeview(self.tree, "Sanctuary Name", False))
        
        self.tree.column("ID", width=80, anchor="center")
        self.tree.column("Species ID", width=80, anchor="center")
        self.tree.column("Species Name", width=200)
        self.tree.column("Sanctuary ID", width=80, anchor="center")
        self.tree.column("Sanctuary Name", width=200)
        
        self.tree.pack(fill="both", expand=True)
        
        # Configure row colors
        self.tree.tag_configure('odd', background="#f9fafb")
        self.tree.tag_configure('even', background=self.colors["card"])
        
        # Footer with back button
        footer_frame = tk.Frame(self.root, bg=self.colors["primary"], padx=20, pady=10)
        footer_frame.pack(fill="x", side="bottom")
        
        back_btn = tk.Button(
            footer_frame, 
            text="⬅ Back to Dashboard", 
            font=("Segoe UI", 10, "bold"),
            command=self.back_to_dashboard, 
            bg=self.colors["primary"], 
            fg="white",
            bd=0,
            padx=15,
            pady=5,
            activebackground="#1a252f",
            activeforeground="white"
        )
        back_btn.pack(side="left")
        
        # Status in footer
        status_text = tk.Label(
            footer_frame,
            text="WildGuard v1.0",
            font=("Segoe UI", 9),
            bg=self.colors["primary"],
            fg="white"
        )
        status_text.pack(side="right")
        
        # Double-click event for tree
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        
        # Add keyboard shortcuts
        self.root.bind("<Control-a>", lambda e: self.trigger_add_link())
        self.root.bind("<Control-d>", lambda e: self.trigger_delete_link())
        self.root.bind("<Delete>", lambda e: self.trigger_delete_link())
        self.tree.bind("<Delete>", lambda e: self.trigger_delete_link())

    def load_data(self):
        """Load mapping data from database with species and sanctuary names"""
        self.tree.delete(*self.tree.get_children())
        try:
            self.cursor.execute("""
                SELECT m.id, m.species_id, s.name, m.sanctuary_id, sa.name
                FROM Species_Sanctuary m
                LEFT JOIN Species s ON m.species_id = s.id
                LEFT JOIN Sanctuary sa ON m.sanctuary_id = sa.id
                ORDER BY m.id DESC
            """)
            
            for i, row in enumerate(self.cursor.fetchall()):
                # Add alternating row colors
                tag = 'even' if i % 2 == 0 else 'odd'
                self.tree.insert("", "end", values=row, tags=(tag,))
                
            # Update status message
            count = len(self.tree.get_children())
            self.status_var.set(f"{count} mapping{'s' if count != 1 else ''} found")
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to load data: {err}")

    def load_species_data(self):
        """Load species data for selection"""
        self.species_data = {}  # Clear existing data
        self.species_listbox.delete(0, tk.END)
        
        try:
            # First check if scientific_name column exists
            self.cursor.execute("SHOW COLUMNS FROM Species LIKE 'scientific_name'")
            scientific_name_exists = bool(self.cursor.fetchone())
            
            if scientific_name_exists:
                # Use original query if column exists
                self.cursor.execute("SELECT id, name, scientific_name FROM Species ORDER BY name")
                for row in self.cursor.fetchall():
                    display_text = f"{row[1]} ({row[2]})" if row[2] else row[1]
                    self.species_listbox.insert(tk.END, display_text)
                    self.species_data[display_text] = row[0]
            else:
                # Modified query without scientific_name
                self.cursor.execute("SELECT id, name FROM Species ORDER BY name")
                for row in self.cursor.fetchall():
                    display_text = row[1]
                    self.species_listbox.insert(tk.END, display_text)
                    self.species_data[display_text] = row[0]
                    
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to load species: {err}")

    def load_sanctuary_data(self):
        """Load sanctuary data for selection"""
        self.sanctuary_data = {}  # Clear existing data
        self.sanctuary_listbox.delete(0, tk.END)
        
        try:
            self.cursor.execute("SELECT id, name, location FROM Sanctuary ORDER BY name")
            for row in self.cursor.fetchall():
                display_text = f"{row[1]} ({row[2]})" if row[2] else row[1]
                self.sanctuary_listbox.insert(tk.END, display_text)
                self.sanctuary_data[display_text] = row[0]  # Store ID with display text as key
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to load sanctuaries: {err}")

    def filter_species(self):
        """Filter species listbox based on search text"""
        search_text = self.species_search_var.get().lower()
        self.species_listbox.delete(0, tk.END)
        
        try:
            # Check if scientific_name column exists
            self.cursor.execute("SHOW COLUMNS FROM Species LIKE 'scientific_name'")
            scientific_name_exists = bool(self.cursor.fetchone())
            
            if scientific_name_exists:
                # Use original query with scientific_name
                if search_text:
                    self.cursor.execute(
                        """SELECT id, name, scientific_name FROM Species 
                        WHERE LOWER(name) LIKE %s OR LOWER(scientific_name) LIKE %s
                        ORDER BY name""", 
                        (f"%{search_text}%", f"%{search_text}%")
                    )
                else:
                    self.cursor.execute("SELECT id, name, scientific_name FROM Species ORDER BY name")
            else:
                # Modified query without scientific_name
                if search_text:
                    self.cursor.execute(
                        """SELECT id, name FROM Species 
                        WHERE LOWER(name) LIKE %s
                        ORDER BY name""", 
                        (f"%{search_text}%",)
                    )
                else:
                    self.cursor.execute("SELECT id, name FROM Species ORDER BY name")
                    
            self.species_data = {}  # Reset data
            
            if scientific_name_exists:
                for row in self.cursor.fetchall():
                    display_text = f"{row[1]} ({row[2]})" if row[2] else row[1]
                    self.species_listbox.insert(tk.END, display_text)
                    self.species_data[display_text] = row[0]
            else:
                for row in self.cursor.fetchall():
                    display_text = row[1]
                    self.species_listbox.insert(tk.END, display_text)
                    self.species_data[display_text] = row[0]
                    
        except mysql.connector.Error as err:
            messagebox.showerror("Search Error", f"Failed to search species: {err}")

    def filter_sanctuaries(self):
        """Filter sanctuaries listbox based on search text"""
        search_text = self.sanctuary_search_var.get().lower()
        self.sanctuary_listbox.delete(0, tk.END)
        
        try:
            if search_text:
                self.cursor.execute(
                    """SELECT id, name, location FROM Sanctuary 
                    WHERE LOWER(name) LIKE %s OR LOWER(location) LIKE %s
                    ORDER BY name""", 
                    (f"%{search_text}%", f"%{search_text}%")
                )
            else:
                self.cursor.execute("SELECT id, name, location FROM Sanctuary ORDER BY name")
                
            self.sanctuary_data = {}  # Reset data
            
            for row in self.cursor.fetchall():
                display_text = f"{row[1]} ({row[2]})" if row[2] else row[1]
                self.sanctuary_listbox.insert(tk.END, display_text)
                self.sanctuary_data[display_text] = row[0]
                
        except mysql.connector.Error as err:
            messagebox.showerror("Search Error", f"Failed to search sanctuaries: {err}")

    def search_mapping(self, *args):
        """Search in the treeview as the user types"""
        search_term = self.search_var.get().lower()
        
        # First clear all items and reload
        self.tree.delete(*self.tree.get_children())
        
        try:
            if search_term:
                self.cursor.execute("""
                    SELECT m.id, m.species_id, s.name, m.sanctuary_id, sa.name
                    FROM Species_Sanctuary m
                    LEFT JOIN Species s ON m.species_id = s.id
                    LEFT JOIN Sanctuary sa ON m.sanctuary_id = sa.id
                    WHERE LOWER(s.name) LIKE %s OR LOWER(sa.name) LIKE %s
                    ORDER BY m.id DESC
                """, (f"%{search_term}%", f"%{search_term}%"))
            else:
                self.cursor.execute("""
                    SELECT m.id, m.species_id, s.name, m.sanctuary_id, sa.name
                    FROM Species_Sanctuary m
                    LEFT JOIN Species s ON m.species_id = s.id
                    LEFT JOIN Sanctuary sa ON m.sanctuary_id = sa.id
                    ORDER BY m.id DESC
                """)
            
            for i, row in enumerate(self.cursor.fetchall()):
                tag = 'even' if i % 2 == 0 else 'odd'
                self.tree.insert("", "end", values=row, tags=(tag,))
        
        except mysql.connector.Error as err:
            print(f"Search error: {err}")
            # Silent fail on search - don't disrupt the user

    def sort_treeview(self, treeview, col, reverse):
        """Sort treeview when clicking on column headers"""
        data_list = []
        for item in treeview.get_children(''):
            values = treeview.item(item)["values"]
            data_list.append(values)
        
        # Compare function
        def compare_values(item1, item2):
            # Get the column index
            col_index = treeview["columns"].index(col)
            value1 = item1[col_index]
            value2 = item2[col_index]
            
            # Compare numerically if both values can be converted to float
            try:
                return float(value1) - float(value2)
            except (ValueError, TypeError):
                # Otherwise compare as strings
                return ((value1 or "").lower() > (value2 or "").lower()) - ((value1 or "").lower() < (value2 or "").lower())
        
        # Sort the data
        data_list.sort(reverse=reverse, key=lambda x: (x[treeview["columns"].index(col)] or "", x))
        
        # Clear and refill the treeview
        treeview.delete(*treeview.get_children())
        for i, item in enumerate(data_list):
            tag = 'even' if i % 2 == 0 else 'odd'
            treeview.insert("", "end", values=item, tags=(tag,))
        
        # Reverse sort next time
        treeview.heading(col, command=lambda: self.sort_treeview(treeview, col, not reverse))

    def add_link(self):
        """Link selected species to selected sanctuary"""
        # Get selections
        species_selection = self.species_listbox.curselection()
        sanctuary_selection = self.sanctuary_listbox.curselection()
        
        # Validate selections
        if not species_selection:
            messagebox.showwarning("Selection Required", "Please select a species.")
            return
            
        if not sanctuary_selection:
            messagebox.showwarning("Selection Required", "Please select a sanctuary.")
            return
        
        # Get the selected items
        species_text = self.species_listbox.get(species_selection[0])
        sanctuary_text = self.sanctuary_listbox.get(sanctuary_selection[0])
        
        # Get the IDs from our data dictionaries
        species_id = self.species_data.get(species_text)
        sanctuary_id = self.sanctuary_data.get(sanctuary_text)
        
        if not species_id or not sanctuary_id:
            messagebox.showerror("Data Error", "Could not find IDs for the selected items.")
            return
            
        # Display a confirmation
        confirm = messagebox.askyesno(
            "Confirm Link",
            f"Link the following:\n\n" +
            f"Species: {species_text}\nSanctuary: {sanctuary_text}\n\n" +
            "Are you sure?"
        )
        
        if not confirm:
            return
            
        try:
            # Try to insert the link
            self.cursor.execute(
                "INSERT INTO Species_Sanctuary (species_id, sanctuary_id) VALUES (%s, %s)",
                (species_id, sanctuary_id)
            )
            self.conn.commit()
            
            # Update the status message
            self.status_var.set("✅ Link added successfully!")
            
            # Refresh the data view
            self.load_data()
            
        except mysql.connector.IntegrityError:
            # Handle duplicate entries
            messagebox.showwarning(
                "Duplicate Link", 
                "This species is already linked to this sanctuary."
            )
            
        except mysql.connector.Error as err:
            # Handle other database errors
            messagebox.showerror("Database Error", f"Failed to add link: {err}")

    def delete_link(self):
        """Delete selected link from the treeview"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a mapping to delete.")
            return
            
        # Get the values from the selected row
        values = self.tree.item(selected)['values']
        mapping_id = values[0]
        species_name = values[2]
        sanctuary_name = values[4]
        
        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Delete the link between:\n\n" +
            f"Species: {species_name}\n" +
            f"Sanctuary: {sanctuary_name}\n\n" +
            "Are you sure? This action cannot be undone.",
            icon="warning"
        )
        
        if not confirm:
            return
            
        try:
            # Delete the mapping
            self.cursor.execute("DELETE FROM Species_Sanctuary WHERE id = %s", (mapping_id,))
            self.conn.commit()
            
            # Update the data view
            self.load_data()
            
            # Update status
            self.status_var.set("✅ Link deleted successfully!")
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to delete link: {err}")

    def on_tree_double_click(self, event):
        """Handle double-click on tree item to show details"""
        selected = self.tree.focus()
        if not selected:
            return
            
        # Get values
        values = self.tree.item(selected)['values']
        
        if len(values) < 5:
            return
            
        # Show details in a popup
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Mapping Details")
        detail_window.geometry("400x300")
        detail_window.configure(bg=self.colors["card"])
        detail_window.grab_set()  # Make window modal
        
        # Header
        header = tk.Frame(detail_window, bg=self.colors["primary"], padx=15, pady=10)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="🔗 Mapping Details",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors["primary"],
            fg="white"
        ).pack()
        
        # Content
        content = tk.Frame(detail_window, bg=self.colors["card"], padx=20, pady=15)
        content.pack(fill="both", expand=True)
        
        # Details
        details = [
            {"label": "Mapping ID:", "value": values[0]},
            {"label": "Species ID:", "value": values[1]},
            {"label": "Species Name:", "value": values[2] or "Unknown"},
            {"label": "Sanctuary ID:", "value": values[3]},
            {"label": "Sanctuary Name:", "value": values[4] or "Unknown"}
        ]
        
        # Get additional species details if available
        try:
            # Check if scientific_name column exists
            self.cursor.execute("SHOW COLUMNS FROM Species LIKE 'scientific_name'")
            scientific_name_exists = bool(self.cursor.fetchone())
            
            if scientific_name_exists:
                self.cursor.execute(
                    "SELECT scientific_name, conservation_status FROM Species WHERE id = %s",
                    (values[1],)
                )
            else:
                self.cursor.execute(
                    "SELECT conservation_status FROM Species WHERE id = %s",
                    (values[1],)
                )
                
            species_info = self.cursor.fetchone()
            if species_info:
                if scientific_name_exists:
                    details.append({"label": "Scientific Name:", "value": species_info[0] or "N/A"})
                    details.append({"label": "Conservation Status:", "value": species_info[1] or "N/A"})
                else:
                    details.append({"label": "Conservation Status:", "value": species_info[0] or "N/A"})
        except:
            pass
            
        # Get additional sanctuary details if available
        try:
            self.cursor.execute(
                "SELECT location, area_sq_km FROM Sanctuary WHERE id = %s",
                (values[3],)
            )
            sanctuary_info = self.cursor.fetchone()
            if sanctuary_info:
                details.append({"label": "Sanctuary Location:", "value": sanctuary_info[0] or "N/A"})
                if sanctuary_info[1]:
                    details.append({"label": "Sanctuary Area:", "value": f"{sanctuary_info[1]} sq km"})
        except:
            pass
            
        # Display details
        for i, item in enumerate(details):
            row = tk.Frame(content, bg=self.colors["card"], pady=5)
            row.pack(fill="x")
            
            tk.Label(
                row,
                text=item["label"],
                font=("Segoe UI", 10, "bold"),
                width=15,
                anchor="w",
                bg=self.colors["card"],
                fg=self.colors["primary"]
            ).pack(side="left")
            
            tk.Label(
                row,
                text=str(item["value"]),
                font=("Segoe UI", 10),
                anchor="w",
                bg=self.colors["card"],
                fg=self.colors["text"]
            ).pack(side="left", fill="x", expand=True)
            
        # Close button
        tk.Button(
            detail_window,
            text="Close",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["primary"],
            fg="white",
            padx=20,
            pady=8,
            bd=0,
            command=detail_window.destroy
        ).pack(pady=15)

    def refresh_all_data(self):
        """Refresh all data from database"""
        self.load_data()
        self.load_species_data()
        self.load_sanctuary_data()
        self.status_var.set("✅ Data refreshed successfully!")

    def back_to_dashboard(self):
        """Return to dashboard"""
        self.root.destroy()
        dashboard.Dashboard(self.username)
        
    def trigger_add_link(self):
        """Enhanced add link function with more feedback"""
        # Clear previous status
        self.status_var.set("Preparing to add link...")
        
        # Emphasize the species listbox if nothing selected
        if not self.species_listbox.curselection():
            self.species_listbox.config(bg="#ffe0e0")  # Light red background
            self.species_search_entry.focus_set()
            self.status_var.set("⚠️ Please select a species first")
            # Reset after 2 seconds
            self.root.after(2000, lambda: self.species_listbox.config(bg="white"))
            return
        
        # Emphasize the sanctuary listbox if nothing selected
        if not self.sanctuary_listbox.curselection():
            self.sanctuary_listbox.config(bg="#ffe0e0")  # Light red background
            self.sanctuary_search_entry.focus_set()
            self.status_var.set("⚠️ Please select a sanctuary first")
            # Reset after 2 seconds
            self.root.after(2000, lambda: self.sanctuary_listbox.config(bg="white"))
            return
        
        # Highlight the selected items for visual confirmation
        species_idx = self.species_listbox.curselection()[0]
        self.species_listbox.itemconfig(species_idx, {'bg': '#e0ffe0'})  # Light green
        
        sanctuary_idx = self.sanctuary_listbox.curselection()[0]
        self.sanctuary_listbox.itemconfig(sanctuary_idx, {'bg': '#e0ffe0'})  # Light green
        
        # Call the actual link function
        self.add_link()
        
        # Reset highlights after a delay
        self.root.after(1500, lambda: [
            self.species_listbox.itemconfig(species_idx, {'bg': 'white'}),
            self.sanctuary_listbox.itemconfig(sanctuary_idx, {'bg': 'white'})
        ])

    def trigger_delete_link(self):
        """Enhanced delete function with more feedback"""
        selected = self.tree.focus()
        
        # If nothing selected, flash the treeview and show message
        if not selected:
            self.tree.config(style="Error.Treeview")
            self.status_var.set("⚠️ Please select a mapping to delete")
            # Reset after 2 seconds
            self.root.after(2000, lambda: [
                self.tree.config(style="Treeview"),
                self.status_var.set("Select a mapping and click Delete")
            ])
            return
        
        # Highlight the selected row for visual confirmation
        current_tags = self.tree.item(selected, 'tags')
        self.tree.item(selected, tags=current_tags + ('delete',))
        
        # Configure the delete tag with red background
        self.tree.tag_configure('delete', background='#ffcccc')
        
        # Call the actual delete function
        self.delete_link()

    def add_new_species(self):
        """Add a new species to database"""
        # Create popup window for adding species
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Species")
        add_window.geometry("400x350")
        add_window.configure(bg=self.colors["card"])
        add_window.grab_set()  # Make modal
        
        # Header
        header = tk.Frame(add_window, bg=self.colors["primary"], padx=15, pady=10)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="🦁 Add New Species",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors["primary"],
            fg="white"
        ).pack()
        
        # Content
        content = tk.Frame(add_window, bg=self.colors["card"], padx=20, pady=15)
        content.pack(fill="both", expand=True)
        
        # Form fields
        fields = [
            {"name": "name", "label": "Species Name:", "required": True},
            {"name": "scientific_name", "label": "Scientific Name:", "required": False},
            {"name": "conservation_status", "label": "Conservation Status:", "required": False},
            {"name": "habitat", "label": "Habitat:", "required": False},
            {"name": "population", "label": "Population:", "required": False, "type": "number"}
        ]
        
        entries = {}
        for i, field in enumerate(fields):
            frame = tk.Frame(content, bg=self.colors["card"], pady=5)
            frame.pack(fill="x")
            
            label_text = field["label"]
            if field.get("required", False):
                label_text += " *"
                
            tk.Label(
                frame,
                text=label_text,
                font=("Segoe UI", 10),
                width=15,
                anchor="w",
                bg=self.colors["card"],
                fg=self.colors["text"]
            ).pack(side="left")
            
            entry = ttk.Entry(frame, font=("Segoe UI", 10))
            entry.pack(side="left", fill="x", expand=True)
            entries[field["name"]] = entry
        
        # Status message
        status_var = StringVar()
        status_label = tk.Label(
            content,
            textvariable=status_var,
            font=("Segoe UI", 9, "italic"),
            bg=self.colors["card"],
            fg=self.colors["text_light"]
        )
        status_label.pack(fill="x", pady=10)
        
        # Button frame
        button_frame = tk.Frame(content, bg=self.colors["card"])
        button_frame.pack(fill="x", pady=10)
        
        def save_species():
            # Validate required fields
            name = entries["name"].get().strip()
            if not name:
                status_var.set("⚠️ Species name is required!")
                return
            
            # Collect values
            scientific_name = entries["scientific_name"].get().strip() or None
            conservation_status = entries["conservation_status"].get().strip() or None
            habitat = entries["habitat"].get().strip() or None
            
            # Convert population to int if provided
            population = None
            if entries["population"].get().strip():
                try:
                    population = int(entries["population"].get().strip())
                    if population < 0:
                        status_var.set("⚠️ Population must be a positive number!")
                        return
                except ValueError:
                    status_var.set("⚠️ Population must be a number!")
                    return
            
            try:
                # Insert the species
                self.cursor.execute(
                    """INSERT INTO Species (name, scientific_name, conservation_status, 
                    habitat, population) VALUES (%s, %s, %s, %s, %s)""",
                    (name, scientific_name, conservation_status, habitat, population)
                )
                self.conn.commit()
                
                # Refresh species data
                self.load_species_data()
                
                status_var.set("✅ Species added successfully!")
                
                # Clear fields for another entry
                for entry in entries.values():
                    entry.delete(0, tk.END)
                    
            except mysql.connector.Error as err:
                status_var.set(f"⚠️ Error: {err}")
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="Save Species",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["secondary"],
            fg="white",
            padx=15,
            pady=5,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=save_species
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=("Segoe UI", 10),
            bg=self.colors["primary"],
            fg="white",
            padx=15,
            pady=5,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=add_window.destroy
        )
        close_btn.pack(side="left")

    def delete_selected_species(self):
        """Delete selected species"""
        selection = self.species_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Required", "Please select a species to delete.")
            return
            
        # Get selected species
        species_text = self.species_listbox.get(selection[0])
        species_id = self.species_data.get(species_text)
        
        if not species_id:
            messagebox.showerror("Error", "Could not find ID for the selected species.")
            return
            
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete the species:\n\n{species_text}\n\n" +
            "This will also remove all sanctuary mappings for this species!\n" +
            "This action cannot be undone.",
            icon="warning"
        )
        
        if not confirm:
            return
            
        try:
            # Delete the species (cascading delete will remove mappings)
            self.cursor.execute("DELETE FROM Species WHERE id = %s", (species_id,))
            self.conn.commit()
            
            # Refresh data
            self.load_species_data()
            self.load_data()  # Reload mappings too
            
            self.status_var.set(f"✅ Species '{species_text}' and its mappings deleted successfully!")
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to delete species: {err}")

    def add_new_sanctuary(self):
        """Add a new sanctuary to database"""
        # Create popup window for adding sanctuary
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Sanctuary")
        add_window.geometry("450x400")
        add_window.configure(bg=self.colors["card"])
        add_window.grab_set()  # Make modal
        
        # Header
        header = tk.Frame(add_window, bg=self.colors["primary"], padx=15, pady=10)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="🏞️ Add New Sanctuary",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors["primary"],
            fg="white"
        ).pack()
        
        # Content
        content = tk.Frame(add_window, bg=self.colors["card"], padx=20, pady=15)
        content.pack(fill="both", expand=True)
        
        # Form fields
        fields = [
            {"name": "name", "label": "Sanctuary Name:", "required": True},
            {"name": "location", "label": "Location:", "required": True},
            {"name": "area", "label": "Area (sq km):", "required": False, "type": "float"},
            {"name": "established_year", "label": "Established Year:", "required": False, "type": "int"}
        ]
        
        entries = {}
        for i, field in enumerate(fields):
            frame = tk.Frame(content, bg=self.colors["card"], pady=5)
            frame.pack(fill="x")
            
            label_text = field["label"]
            if field.get("required", False):
                label_text += " *"
                
            tk.Label(
                frame,
                text=label_text,
                font=("Segoe UI", 10),
                width=15,
                anchor="w",
                bg=self.colors["card"],
                fg=self.colors["text"]
            ).pack(side="left")
            
            entry = ttk.Entry(frame, font=("Segoe UI", 10))
            entry.pack(side="left", fill="x", expand=True)
            entries[field["name"]] = entry
        
        # Description field
        desc_frame = tk.Frame(content, bg=self.colors["card"], pady=5)
        desc_frame.pack(fill="x")
        
        tk.Label(
            desc_frame,
            text="Description:",
            font=("Segoe UI", 10),
            width=15,
            anchor="nw",
            bg=self.colors["card"],
            fg=self.colors["text"]
        ).pack(side="left", anchor="n")
        
        desc_text = tk.Text(
            desc_frame,
            font=("Segoe UI", 10),
            height=4,
            width=30,
            wrap="word"
        )
        desc_text.pack(side="left", fill="both", expand=True)
        entries["description"] = desc_text
        
        # Status message
        status_var = StringVar()
        status_label = tk.Label(
            content,
            textvariable=status_var,
            font=("Segoe UI", 9, "italic"),
            bg=self.colors["card"],
            fg=self.colors["text_light"]
        )
        status_label.pack(fill="x", pady=10)
        
        # Button frame
        button_frame = tk.Frame(content, bg=self.colors["card"])
        button_frame.pack(fill="x", pady=10)
        
        def save_sanctuary():
            # Validate required fields
            name = entries["name"].get().strip()
            location = entries["location"].get().strip()
            
            if not name:
                status_var.set("⚠️ Sanctuary name is required!")
                return
                
            if not location:
                status_var.set("⚠️ Location is required!")
                return
            
            # Collect values
            area = None
            if entries["area"].get().strip():
                try:
                    area = float(entries["area"].get().strip())
                    if area <= 0:
                        status_var.set("⚠️ Area must be a positive number!")
                        return
                except ValueError:
                    status_var.set("⚠️ Area must be a number!")
                    return
                    
            year = None
            if entries["established_year"].get().strip():
                try:
                    year = int(entries["established_year"].get().strip())
                    from datetime import datetime
                    current_year = datetime.now().year
                    if year < 1800 or year > current_year:
                        status_var.set(f"⚠️ Year must be between 1800 and {current_year}!")
                        return
                except ValueError:
                    status_var.set("⚠️ Year must be a number!")
                    return
                    
            description = entries["description"].get("1.0", tk.END).strip() or None
            
            try:
                # Insert the sanctuary
                self.cursor.execute(
                    """INSERT INTO Sanctuary (name, location, area_sq_km, established_year, description)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (name, location, area, year, description)
                )
                self.conn.commit()
                
                # Refresh sanctuary data
                self.load_sanctuary_data()
                
                status_var.set("✅ Sanctuary added successfully!")
                
                # Clear fields for another entry
                for key, entry in entries.items():
                    if key == "description":
                        entry.delete("1.0", tk.END)
                    else:
                        entry.delete(0, tk.END)
                    
            except mysql.connector.Error as err:
                status_var.set(f"⚠️ Error: {err}")
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="Save Sanctuary",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["secondary"],
            fg="white",
            padx=15,
            pady=5,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=save_sanctuary
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=("Segoe UI", 10),
            bg=self.colors["primary"],
            fg="white",
            padx=15,
            pady=5,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=add_window.destroy
        )
        close_btn.pack(side="left")

    def delete_selected_sanctuary(self):
        """Delete selected sanctuary"""
        selection = self.sanctuary_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Required", "Please select a sanctuary to delete.")
            return
            
        # Get selected sanctuary
        sanctuary_text = self.sanctuary_listbox.get(selection[0])
        sanctuary_id = self.sanctuary_data.get(sanctuary_text)
        
        if not sanctuary_id:
            messagebox.showerror("Error", "Could not find ID for the selected sanctuary.")
            return
            
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete the sanctuary:\n\n{sanctuary_text}\n\n" +
            "This will also remove all species mappings for this sanctuary!\n" +
            "This action cannot be undone.",
            icon="warning"
        )
        
        if not confirm:
            return
            
        try:
            # Delete the sanctuary (cascading delete will remove mappings)
            self.cursor.execute("DELETE FROM Sanctuary WHERE id = %s", (sanctuary_id,))
            self.conn.commit()
            
            # Refresh data
            self.load_sanctuary_data()
            self.load_data()  # Reload mappings too
            
            self.status_var.set(f"✅ Sanctuary '{sanctuary_text}' and its mappings deleted successfully!")
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to delete sanctuary: {err}")

    def __del__(self):
        """Close database connection when object is destroyed"""
        try:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
        except:
            pass


# For testing purposes
if __name__ == "__main__":
    app = SpeciesSanctuary("Admin")

