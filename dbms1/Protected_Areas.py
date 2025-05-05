import tkinter as tk
from tkinter import ttk, messagebox, font
from tkinter.scrolledtext import ScrolledText
import importlib

class ProtectedArea:
    def __init__(self, name, area_type, location, area_size, species_protected):
        self.name = name
        self.area_type = area_type
        self.location = location
        self.area_size = area_size
        self.species_protected = species_protected

    def __str__(self):
        return f"{self.name} | {self.area_type} | {self.location} | {self.area_size} sq km | Species: {', '.join(self.species_protected)}"


class ProtectedAreaApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title("🌿 WildGuard - Protected Areas Management")
        self.root.geometry("1050x700")  # More space for better layout
        self.root.configure(bg="#f0f5e9")  # Light natural background
        self.areas = []
        
        # Define theme colors
        self.colors = {
            "primary": "#1e8449",      # Forest green
            "secondary": "#27ae60",    # Lighter green
            "accent": "#f39c12",       # Golden accent
            "bg": "#f0f5e9",           # Light natural background
            "card": "#ffffff",         # White for cards
            "text": "#2c3e50",         # Dark blue-gray for text
            "text_secondary": "#7f8c8d",  # ADDED: Secondary text color (lighter gray)
            "error": "#e74c3c",        # Red for alerts/errors
            "success": "#2ecc71",      # Green for success
            "button_hover": "#16a085", # Teal for hover effects
            "dark_accent": "#145a32",  # Dark green for headers
            "subtle": "#ecf0f1"        # Light gray for subtle backgrounds
        }
        
        # Create ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use clam theme as base
        
        # Configure styles for entry fields
        self.style.configure("TEntry", 
                            fieldbackground=self.colors["card"],
                            borderwidth=1)
                            
        self.style.configure("TButton", 
                            font=("Helvetica", 11, "bold"),
                            background=self.colors["secondary"],
                            foreground="white")
                            
        self.style.map("TButton",
                      background=[("active", self.colors["button_hover"])])
                      
        self.style.configure("Accent.TButton", 
                            font=("Helvetica", 11, "bold"),
                            background=self.colors["accent"],
                            foreground="white")
                            
        self.style.map("Accent.TButton",
                      background=[("active", "#e67e22")])
                      
        # Create main frames
        self.create_header()
        self.main_frame = self.create_main_frame()
        
        # Create footer FIRST (before panels)
        self.create_footer()
        
        # Then create panels
        self.create_input_panel()
        self.create_areas_panel()
        
        # Load data at the end when everything is set up
        self.load_mysql_data()
        
    def create_header(self):
        """Create the application header with title and back button"""
        header_frame = tk.Frame(self.root, bg=self.colors["primary"], height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)  # Prevent shrinking
        
        # Back button with enhanced styling
        back_btn = tk.Button(
            header_frame, 
            text="⬅ Back to Dashboard", 
            command=self.back_to_dashboard,
            bg=self.colors["dark_accent"], 
            fg="white", 
            font=("Helvetica", 11, "bold"),
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            activebackground="#0e4429",
            activeforeground="white"
        )
        back_btn.pack(side="left", padx=20, pady=15)
        
        # Page title with icon
        title_label = tk.Label(
            header_frame, 
            text="🌳 Protected Areas Management", 
            font=("Helvetica", 18, "bold"), 
            bg=self.colors["primary"], 
            fg="white"
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        # User info display
        user_frame = tk.Frame(header_frame, bg=self.colors["primary"])
        user_frame.pack(side="right", padx=20, pady=15)
        
        user_icon = tk.Label(
            user_frame, 
            text="👤", 
            font=("Helvetica", 14), 
            bg=self.colors["primary"], 
            fg="white"
        )
        user_icon.pack(side="left")
        
        user_label = tk.Label(
            user_frame, 
            text=f"{self.username}", 
            font=("Helvetica", 12), 
            bg=self.colors["primary"], 
            fg="white"
        )
        user_label.pack(side="left", padx=5)
        
        # Add shadow effect below header
        shadow_frame = tk.Frame(self.root, height=5, bg=self.colors["dark_accent"])
        shadow_frame.pack(fill="x")

    def create_main_frame(self):
        """Create the main content frame"""
        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        return main_frame
    
    def create_input_panel(self):
        """Create the left panel with input fields"""
        input_frame = tk.LabelFrame(
            self.main_frame, 
            text=" Add Protected Area ", 
            font=("Helvetica", 14, "bold"),
            bg=self.colors["card"],
            fg=self.colors["primary"],
            padx=20,
            pady=20
        )
        input_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Input field styles
        label_style = {"font": ("Helvetica", 11), "bg": self.colors["card"], "fg": self.colors["text"], "anchor": "w"}
        entry_width = 30
        pady_value = 8
        
        # Name field
        tk.Label(input_frame, text="🏷️ Name:", **label_style).grid(row=0, column=0, sticky="w", pady=pady_value)
        self.name_entry = ttk.Entry(input_frame, width=entry_width, font=("Helvetica", 11))
        self.name_entry.grid(row=0, column=1, sticky="w", pady=pady_value)
        
        # Type field with dropdown instead of entry
        tk.Label(input_frame, text="🌿 Type:", **label_style).grid(row=1, column=0, sticky="w", pady=pady_value)
        types = ["National Park", "Wildlife Sanctuary", "Reserved Forest", "Conservation Area", "Marine Protected Area", "Biosphere Reserve", "Other"]
        self.type_var = tk.StringVar()
        self.type_dropdown = ttk.Combobox(
            input_frame, 
            textvariable=self.type_var, 
            values=types,
            width=entry_width-3,
            font=("Helvetica", 11),
            state="readonly"
        )
        self.type_dropdown.grid(row=1, column=1, sticky="w", pady=pady_value)
        self.type_dropdown.current(0)
        
        # Location field
        tk.Label(input_frame, text="📍 Location:", **label_style).grid(row=2, column=0, sticky="w", pady=pady_value)
        self.location_entry = ttk.Entry(input_frame, width=entry_width, font=("Helvetica", 11))
        self.location_entry.grid(row=2, column=1, sticky="w", pady=pady_value)
        
        # Area size field
        tk.Label(input_frame, text="📏 Area Size (sq km):", **label_style).grid(row=3, column=0, sticky="w", pady=pady_value)
        self.size_entry = ttk.Entry(input_frame, width=entry_width, font=("Helvetica", 11))
        self.size_entry.grid(row=3, column=1, sticky="w", pady=pady_value)
        
        # Species field - using scrolled text for better UX with multiple species
        tk.Label(input_frame, text="🦁 Species Protected:", **label_style).grid(row=4, column=0, sticky="nw", pady=pady_value)
        self.species_text = ScrolledText(input_frame, width=entry_width, height=6, font=("Helvetica", 11), wrap=tk.WORD)
        self.species_text.grid(row=4, column=1, sticky="w", pady=pady_value)
        
        # Help text
        help_text = tk.Label(
            input_frame, 
            text="Enter species names separated by commas", 
            font=("Helvetica", 9, "italic"), 
            fg=self.colors["text_secondary"],
            bg=self.colors["card"]
        )
        help_text.grid(row=5, column=1, sticky="w")
        
        # Button frame for better layout
        button_frame = tk.Frame(input_frame, bg=self.colors["card"], pady=10)
        button_frame.grid(row=6, column=0, columnspan=2, sticky="ew")
        
        # Add button with styling
        add_btn = tk.Button(
            button_frame,
            text="➕ Add Protected Area",
            font=("Helvetica", 12, "bold"),
            bg=self.colors["secondary"],
            fg="white",
            padx=20,
            pady=10,
            bd=0,
            cursor="hand2",
            command=self.add_area,
            activebackground=self.colors["button_hover"]
        )
        add_btn.pack(pady=10)
        
        # Clear button 
        clear_btn = tk.Button(
            button_frame,
            text="🔄 Clear Form",
            font=("Helvetica", 11),
            bg=self.colors["subtle"],
            fg=self.colors["text"],
            padx=15,
            pady=8,
            bd=0,
            cursor="hand2",
            command=self.clear_entries
        )
        clear_btn.pack(pady=5)

    def create_areas_panel(self):
        """Create the right panel showing existing areas"""
        areas_frame = tk.LabelFrame(
            self.main_frame, 
            text=" Protected Areas List ", 
            font=("Helvetica", 14, "bold"),
            bg=self.colors["card"],
            fg=self.colors["primary"],
            padx=20,
            pady=20
        )
        areas_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Create treeview instead of listbox for better display
        columns = ("ID", "Name", "Type", "Location", "Size", "Species")
        self.tree = ttk.Treeview(areas_frame, columns=columns, show="headings", height=15)
        
        # Define column headings
        self.tree.heading("ID", text="#")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Location", text="Location")
        self.tree.heading("Size", text="Size (sq km)")
        self.tree.heading("Species", text="Species")
        
        # Define column widths
        self.tree.column("ID", width=30, anchor="center")
        self.tree.column("Name", width=120)
        self.tree.column("Type", width=120)
        self.tree.column("Location", width=100)
        self.tree.column("Size", width=80, anchor="center")
        self.tree.column("Species", width=180)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(areas_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, pady=10)
        
        # Style the treeview rows
        self.style.configure("Treeview", 
                           background=self.colors["card"],
                           foreground=self.colors["text"],
                           rowheight=25,
                           fieldbackground=self.colors["card"])
        
        self.style.map("Treeview",
                     background=[("selected", self.colors["primary"])],
                     foreground=[("selected", "white")])
        
        # Button frame
        button_frame = tk.Frame(areas_frame, bg=self.colors["card"])
        button_frame.pack(fill="x", pady=10)
        
        # Delete button
        delete_btn = tk.Button(
            button_frame,
            text="🗑️ Delete Selected",
            font=("Helvetica", 11, "bold"),
            bg=self.colors["error"],
            fg="white",
            padx=15,
            pady=8,
            bd=0,
            cursor="hand2",
            command=self.delete_selected,
            activebackground="#c0392b"
        )
        delete_btn.pack(side="left", padx=5)
        
        # View details button
        details_btn = tk.Button(
            button_frame,
            text="🔍 View Details",
            font=("Helvetica", 11, "bold"),
            bg=self.colors["accent"],
            fg="white",
            padx=15,
            pady=8,
            bd=0,
            cursor="hand2",
            command=self.view_details,
            activebackground="#d35400"
        )
        details_btn.pack(side="left", padx=5)
        
        # Refresh button
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh List",
            font=("Helvetica", 11),
            bg=self.colors["subtle"],
            fg=self.colors["text"],
            padx=15,
            pady=8,
            bd=0,
            cursor="hand2",
            command=self.update_tree,
            activebackground="#bdc3c7"
        )
        refresh_btn.pack(side="right", padx=5)
        
        # Initial tree update to show empty state
        self.update_tree()

    def create_footer(self):
        """Create application footer"""
        footer_frame = tk.Frame(self.root, bg=self.colors["primary"], height=40)
        footer_frame.pack(fill="x", side="bottom")
        
        # Copyright info
        footer_label = tk.Label(
            footer_frame, 
            text="© 2023 WildGuard - Conservation Management System", 
            font=("Helvetica", 9), 
            bg=self.colors["primary"], 
            fg="white"
        )
        footer_label.pack(side="left", padx=20, pady=10)
        
        # Area count
        self.count_label = tk.Label(
            footer_frame, 
            text="Total Areas: 0", 
            font=("Helvetica", 9), 
            bg=self.colors["primary"], 
            fg="white"
        )
        self.count_label.pack(side="right", padx=20, pady=10)

    def add_area(self):
        """Add a new protected area with enhanced validation"""
        name = self.name_entry.get().strip()
        area_type = self.type_var.get()
        location = self.location_entry.get().strip()
        
        # Validate size
        try:
            area_size = float(self.size_entry.get().strip())
            if area_size <= 0:
                messagebox.showerror("Error", "Area size must be a positive number")
                return
        except ValueError:
            messagebox.showerror("Error", "Area size must be a valid number")
            return

        # Get species from text widget
        species_input = self.species_text.get("1.0", tk.END).strip()
        species_list = [s.strip() for s in species_input.split(",") if s.strip()]

        # Validate required fields
        if not name:
            messagebox.showwarning("Input Error", "Please enter a name for the protected area")
            self.name_entry.focus()
            return

        if not location:
            messagebox.showwarning("Input Error", "Please enter a location")
            self.location_entry.focus()
            return

        if not species_list:
            messagebox.showwarning("Input Error", "Please enter at least one protected species")
            self.species_text.focus()
            return

        # Create and add the new area
        area = ProtectedArea(name, area_type, location, area_size, species_list)
        self.areas.append(area)
        
        # Show success message with more information
        messagebox.showinfo("Success", f"Protected area '{name}' added successfully!\n\nTotal areas: {len(self.areas)}")
        
        # Clear form and update tree
        self.clear_entries()
        self.update_tree()

    def clear_entries(self):
        """Clear all input fields"""
        self.name_entry.delete(0, tk.END)
        self.type_dropdown.current(0)
        self.location_entry.delete(0, tk.END)
        self.size_entry.delete(0, tk.END)
        self.species_text.delete("1.0", tk.END)
        self.name_entry.focus()  # Set focus to first field

    def update_tree(self):
        """Update the treeview with current areas"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Update the counter - with error handling in case count_label isn't created yet
            if hasattr(self, 'count_label'):
                self.count_label.config(text=f"Total Areas: {len(self.areas)}")
        except Exception as e:
            print(f"Error updating count label: {str(e)}")
        
        if not self.areas:
            # If no areas, show empty message
            self.tree.insert('', 'end', values=('', 'No protected areas found', '', '', '', ''))
            return
            
        # Populate with areas data
        for idx, area in enumerate(self.areas, 1):
            # Format species list for display - limit to first 3 with count
            if len(area.species_protected) <= 3:
                species_display = ", ".join(area.species_protected)
            else:
                species_display = f"{', '.join(area.species_protected[:3])} +{len(area.species_protected)-3}"
                
            # Add tree item with all data
            values = (
                idx,
                area.name,
                area.area_type,
                area.location,
                area.area_size,
                species_display
            )
            
            # Set tag for row color alternation
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.tree.insert('', 'end', values=values, tags=(tag,))
        
        # Configure row colors for better readability
        self.tree.tag_configure('odd', background=self.colors["subtle"])
        self.tree.tag_configure('even', background=self.colors["card"])

    def delete_selected(self):
        """Delete the selected area with confirmation"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an area to delete")
            return
            
        # Get the selected item's ID
        item = self.tree.item(selection[0])
        values = item['values']
        
        # Check if it's the "No protected areas found" message
        if not values[0]:  # Empty ID means it's our placeholder
            return
            
        # Get the index (ID column - 1)
        idx = int(values[0]) - 1
        area = self.areas[idx]
        
        # Ask for confirmation with details
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete the following protected area?\n\n" +
            f"Name: {area.name}\n" +
            f"Type: {area.area_type}\n" +
            f"Location: {area.location}\n\n" +
            "This action cannot be undone.",
            icon="warning"
        )
        
        if confirm:
            # Delete the area and update the display
            del self.areas[idx]
            messagebox.showinfo("Success", f"Area '{area.name}' has been deleted")
            self.update_tree()

    def view_details(self):
        """Show detailed information about selected area"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an area to view")
            return
            
        # Get the selected item's ID
        item = self.tree.item(selection[0])
        values = item['values']
        
        # Check if it's the "No protected areas found" message
        if not values[0]:  # Empty ID means it's our placeholder
            return
            
        # Get the index (ID column - 1)
        idx = int(values[0]) - 1
        area = self.areas[idx]
        
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Details: {area.name}")
        details_window.geometry("600x400")
        details_window.configure(bg=self.colors["card"])
        
        # Set transient to make it modal-like
        details_window.transient(self.root)
        details_window.grab_set()
        
        # Header with area name
        header = tk.Frame(details_window, bg=self.colors["primary"], padx=15, pady=10)
        header.pack(fill="x")
        
        title_label = tk.Label(
            header,
            text=f"🌳 {area.name}",
            font=("Helvetica", 16, "bold"),
            bg=self.colors["primary"],
            fg="white"
        )
        title_label.pack(pady=5)
        
        # Content frame with area details
        content = tk.Frame(details_window, bg=self.colors["card"], padx=20, pady=20)
        content.pack(fill="both", expand=True)
        
        # Area details as key-value pairs
        details = [
            ("Type", f"🌿 {area.area_type}"),
            ("Location", f"📍 {area.location}"),
            ("Size", f"📏 {area.area_size} square kilometers"),
            ("Species Count", f"🔢 {len(area.species_protected)} protected species")
        ]
        
        # Add each detail row
        for i, (key, value) in enumerate(details):
            tk.Label(
                content, 
                text=key, 
                font=("Helvetica", 11, "bold"),
                bg=self.colors["card"],
                fg=self.colors["text"]
            ).grid(row=i, column=0, sticky="w", pady=8)
            
            tk.Label(
                content, 
                text=value, 
                font=("Helvetica", 11),
                bg=self.colors["card"],
                fg=self.colors["text"]
            ).grid(row=i, column=1, sticky="w", padx=20, pady=8)
        
        # Species list in a scrolled text widget
        tk.Label(
            content, 
            text="Protected Species", 
            font=("Helvetica", 11, "bold"),
            bg=self.colors["card"],
            fg=self.colors["text"]
        ).grid(row=len(details), column=0, sticky="nw", pady=8)
        
        species_text = ScrolledText(content, width=40, height=8, font=("Helvetica", 10), wrap=tk.WORD)
        species_text.grid(row=len(details), column=1, sticky="w", padx=20, pady=8)
        species_text.insert(tk.END, "\n".join(f"• {species}" for species in area.species_protected))
        species_text.configure(state="disabled")  # Make read-only
        
        # Close button
        close_btn = tk.Button(
            details_window,
            text="Close",
            font=("Helvetica", 11, "bold"),
            bg=self.colors["primary"],
            fg="white",
            padx=20,
            pady=8,
            bd=0,
            cursor="hand2",
            command=details_window.destroy
        )
        close_btn.pack(pady=15)
    
    def back_to_dashboard(self):
        """Return to the main dashboard with better error handling"""
        try:
            self.root.destroy()
            import dashboard
            dashboard.Dashboard(username=self.username)
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Try to show a message box if possible
            try:
                messagebox.showerror("Error", f"Unable to return to dashboard: {str(e)}")
            except:
                print(f"Error returning to dashboard: {str(e)}")

    def create_table_if_needed(self):
        """Create the protected_areas table with proper column names"""
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="11223344",
                database="WildGuardDB"
            )
            cursor = conn.cursor()
            
            # Create table if it doesn't exist - note the backticks around 'type'
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS protected_areas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    `type` VARCHAR(50) NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    area_size FLOAT NOT NULL,
                    species TEXT NOT NULL
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Database setup error: {str(e)}")
            return False

    def load_mysql_data(self):
        """Load protected areas from MySQL database with improved error handling"""
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="11223344",
                database="WildGuardDB"
            )
            cursor = conn.cursor()
            
            # First check if table exists with correct structure
            try:
                # First try with backticks as defined in create_table
                cursor.execute("""
                    SELECT name, `type`, location, area_size, species 
                    FROM protected_areas
                """)
            except mysql.connector.Error as err:
                if "Unknown column" in str(err):
                    # The table might exist but with area_type instead of type
                    try:
                        cursor.execute("""
                            SELECT name, area_type, location, area_size, species 
                            FROM protected_areas
                        """)
                    except mysql.connector.Error:
                        # If that fails too, recreate the table with the right structure
                        self.recreate_table(cursor, conn)
                        return
            
            # Process results
            for (name, area_type, location, area_size, species_str) in cursor.fetchall():
                species_list = [s.strip() for s in species_str.split(",") if s.strip()]
                area = ProtectedArea(name, area_type, location, float(area_size), species_list)
                self.areas.append(area)
            
            # Update the display
            self.update_tree()
            
            # Close connection
            cursor.close()
            conn.close()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.add_sample_areas()  # Add fallback sample data
        
    def recreate_table(self, cursor, conn):
        """Recreate the table with correct structure"""
        try:
            # Drop the existing table if it exists
            cursor.execute("DROP TABLE IF EXISTS protected_areas")
            
            # Create table with area_type instead of type to avoid reserved word issues
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS protected_areas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    area_type VARCHAR(50) NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    area_size FLOAT NOT NULL,
                    species TEXT NOT NULL
                )
            """)
            conn.commit()
            
            # Add sample data
            sample_areas = [
                ("Yellowstone National Park", "National Park", "Wyoming, USA", 8991.0, "Gray Wolf, Grizzly Bear, Bison, Elk"),
                ("Serengeti", "Wildlife Reserve", "Tanzania", 14750.0, "Lion, Elephant, Zebra, Wildebeest"),
                ("Great Barrier Reef", "Marine Protected Area", "Australia", 344400.0, "Coral, Sea Turtle, Shark, Clownfish")
            ]
            
            cursor.executemany("""
                INSERT INTO protected_areas (name, area_type, location, area_size, species)
                VALUES (%s, %s, %s, %s, %s)
            """, sample_areas)
            conn.commit()
            
            # Load the new data
            cursor.execute("""
                SELECT name, area_type, location, area_size, species 
                FROM protected_areas
            """)
            
            # Process results
            for (name, area_type, location, area_size, species_str) in cursor.fetchall():
                species_list = [s.strip() for s in species_str.split(",") if s.strip()]
                area = ProtectedArea(name, area_type, location, float(area_size), species_list)
                self.areas.append(area)
                
            # Update display
            self.update_tree()
            messagebox.showinfo("Database Reset", "The database table has been recreated with sample data.")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not recreate table: {str(e)}")
            self.add_sample_areas()  # Add fallback sample data

    def add_sample_areas(self):
        """Add sample data when database connection fails"""
        if not self.areas:
            sample_data = [
                ("Yellowstone", "National Park", "Wyoming, USA", 8991.0, 
                 ["Gray Wolf", "Grizzly Bear", "Bison", "Elk"]),
                ("Serengeti", "National Park", "Tanzania", 14750.0, 
                 ["Lion", "Elephant", "Zebra", "Wildebeest"]),
                ("Great Barrier Reef", "Marine Protected Area", "Australia", 344400.0,
                 ["Coral", "Sea Turtle", "Shark", "Clownfish"])
            ]
            
            for name, area_type, location, area_size, species_list in sample_data:
                area = ProtectedArea(name, area_type, location, area_size, species_list)
                self.areas.append(area)
                
            self.update_tree()
            messagebox.showinfo("Notice", "Using sample data as database connection failed.")


def run(username="Admin"):
    """Function to start the Protected Areas module"""
    try:
        root = tk.Tk()
        root.title("🌿 WildGuard - Protected Areas")
        root.geometry("800x600")
        
        # Show basic content to verify Tkinter works
        label = tk.Label(root, text="Loading Protected Areas...")
        label.pack(pady=20)
        
        # Try initializing the full app after 1 second
        root.after(1000, lambda: initialize_app(root, username))
        root.mainloop()
    except Exception as e:
        print(f"Error: {str(e)}")

def initialize_app(root, username):
    try:
        app = ProtectedAreaApp(root, username)
    except Exception as e:
        import traceback
        traceback.print_exc()
        tk.Label(root, text=f"Error: {str(e)}", fg="red").pack(pady=20)


# Only run if executed directly
if __name__ == "__main__":
    run()
