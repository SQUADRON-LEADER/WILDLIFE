import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import importlib

class MapLocation:
    def __init__(self, username):
        self.username = username
        
        # Initialize root window
        self.root = tk.Tk()
        self.root.title("🌍Map Locations - WildGuard")
        self.root.geometry("950x600")
        
        # Wildlife-themed colors
        self.colors = {
            "primary": "#2e7d32",       # Forest green
            "secondary": "#4caf50",     # Lighter green
            "accent": "#ff9800",        # Orange accent
            "danger": "#d32f2f",        # Red for delete/warning
            "background": "#f5f5e9",    # Light natural background
            "card": "#ffffff",          # White for cards
            "text": "#424242",          # Dark gray for text
            "text_light": "#fafafa"     # Light text
        }
        
        self.root.configure(bg=self.colors["background"])
        
        # Setup database connection
        self.setup_database()
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_data()
        
        # Start the application
        self.root.mainloop()
    
    def setup_database(self):
        """Establish database connection"""
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="11223344",
                database="WildGuardDB"
            )
            self.cursor = self.conn.cursor(buffered=True)
            
            # Create table if it doesn't exist
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS map_location (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sanctuary_id INT NOT NULL,
                    latitude DECIMAL(10, 6) NOT NULL,
                    longitude DECIMAL(10, 6) NOT NULL,
                    FOREIGN KEY (sanctuary_id) REFERENCES Sanctuaries(id) ON DELETE CASCADE
                )
            """)
            self.conn.commit()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Connection Error", f"Failed to connect to database: {err}")
            print(f"Database error: {err}")  # Debug output
    
    def setup_ui(self):
        """Set up the user interface with improved styling"""
        # Configure styles
        self.configure_styles()
        
        # Header section with gradient effect
        header_frame = tk.Frame(self.root, bg=self.colors["primary"], height=80)
        header_frame.pack(fill="x")
        
        # Create shadow effect
        shadow_frame = tk.Frame(self.root, bg="#1b5e20", height=5)
        shadow_frame.pack(fill="x")
        
        # Header content
        title_label = tk.Label(
            header_frame, 
            text="🌍 Map Location Management", 
            font=("Helvetica", 22, "bold"), 
            bg=self.colors["primary"], 
            fg=self.colors["text_light"],
            pady=20
        )
        title_label.pack()
        
        # Main content area
        main_frame = tk.Frame(self.root, bg=self.colors["background"], padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)
        
        # Form section with card styling
        form_card = tk.LabelFrame(
            main_frame, 
            text=" Add New Location ", 
            font=("Helvetica", 12, "bold"),
            bg=self.colors["card"],
            fg=self.colors["primary"],
            padx=15, 
            pady=15
        )
        form_card.pack(fill="x", pady=10)
        
        # Form layout with grid
        form_frame = tk.Frame(form_card, bg=self.colors["card"], padx=10)
        form_frame.pack(fill="x", pady=5)
        
        # Row 1
        tk.Label(
            form_frame, 
            text="🏞️Sanctuary ID:", 
            font=("Helvetica", 10, "bold"),
            bg=self.colors["card"],
            fg=self.colors["text"]
        ).grid(row=0, column=0, padx=(10, 5), pady=10, sticky="e")
        
        self.sanctuary_id_entry = ttk.Entry(
            form_frame, 
            width=15, 
            font=("Helvetica", 10),
            style="Custom.TEntry"
        )
        self.sanctuary_id_entry.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        
        tk.Label(
            form_frame, 
            text="📍 Latitude:", 
            font=("Helvetica", 10, "bold"),
            bg=self.colors["card"],
            fg=self.colors["text"]
        ).grid(row=0, column=2, padx=(20, 5), pady=10, sticky="e")
        
        self.latitude_entry = ttk.Entry(
            form_frame, 
            width=15, 
            font=("Helvetica", 10),
            style="Custom.TEntry"
        )
        self.latitude_entry.grid(row=0, column=3, padx=5, pady=10, sticky="w")
        
        # Row 2
        tk.Label(
            form_frame, 
            text="🧭 Longitude:", 
            font=("Helvetica", 10, "bold"),
            bg=self.colors["card"],
            fg=self.colors["text"]
        ).grid(row=1, column=0, padx=(10, 5), pady=10, sticky="e")
        
        self.longitude_entry = ttk.Entry(
            form_frame, 
            width=15, 
            font=("Helvetica", 10),
            style="Custom.TEntry"
        )
        self.longitude_entry.grid(row=1, column=1, padx=5, pady=10, sticky="w")
        
        # Row 3 - Buttons
        button_frame = tk.Frame(form_card, bg=self.colors["card"], pady=10)
        button_frame.pack()
        
        # Add button with hover effect
        self.add_btn = tk.Button(
            button_frame, 
            text="➕Add Location", 
            font=("Helvetica", 10, "bold"),
            bg=self.colors["secondary"], 
            fg=self.colors["text_light"],
            padx=15, 
            pady=8,
            bd=0,
            cursor="hand2",
            command=self.add_location
        )
        self.add_btn.pack(side="left", padx=10)
        
        # Bind hover events
        self.add_btn.bind("<Enter>", lambda e: self.add_btn.config(bg="#3da142"))
        self.add_btn.bind("<Leave>", lambda e: self.add_btn.config(bg=self.colors["secondary"]))
        
        # Delete button with hover effect
        self.delete_btn = tk.Button(
            button_frame, 
            text="🗑️Delete Selected", 
            font=("Helvetica", 10, "bold"),
            bg=self.colors["danger"], 
            fg=self.colors["text_light"],
            padx=15, 
            pady=8,
            bd=0,
            cursor="hand2",
            command=self.delete_location
        )
        self.delete_btn.pack(side="left", padx=10)
        
        # Bind hover events
        self.delete_btn.bind("<Enter>", lambda e: self.delete_btn.config(bg="#b71c1c"))
        self.delete_btn.bind("<Leave>", lambda e: self.delete_btn.config(bg=self.colors["danger"]))
        
        # Table section with card styling
        table_card = tk.LabelFrame(
            main_frame, 
            text=" Location Database ", 
            font=("Helvetica", 12, "bold"),
            bg=self.colors["card"],
            fg=self.colors["primary"],
            padx=15, 
            pady=15
        )
        table_card.pack(fill="both", expand=True, pady=10)
        
        # Table with scrollbar
        table_frame = tk.Frame(table_card, bg=self.colors["card"])
        table_frame.pack(fill="both", expand=True)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame)
        y_scrollbar.pack(side="right", fill="y")
        
        x_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")
        
        # Treeview setup with improved styling
        self.tree = ttk.Treeview(
            table_frame, 
            columns=("ID", "Sanctuary ID", "Latitude", "Longitude"), 
            show='headings',
            style="Custom.Treeview", 
            height=8,  # Reduced height to accommodate taller rows
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )

        # Configure scrollbars
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)

        # Configure columns with fixed widths and better visibility
        self.tree.column("ID", width=150, anchor="center", minwidth=150, stretch=False)
        self.tree.column("Sanctuary ID", width=200, anchor="center", minwidth=200, stretch=False)
        self.tree.column("Latitude", width=225, anchor="center", minwidth=225, stretch=False)
        self.tree.column("Longitude", width=225, anchor="center", minwidth=225, stretch=False)

        # Configure headings with more prominent titles
        self.tree.heading("ID", text="LOCATION ID")
        self.tree.heading("Sanctuary ID", text="SANCTUARY ID")
        self.tree.heading("Latitude", text="LATITUDE")
        self.tree.heading("Longitude", text="LONGITUDE")
        
        self.tree.pack(fill="both", expand=True)
        
        # Footer section
        footer_frame = tk.Frame(self.root, bg=self.colors["primary"], height=60)
        footer_frame.pack(side="bottom", fill="x")
        
        # Back button in footer
        back_btn = tk.Button(
            footer_frame, 
            text="⬅️Back to Dashboard", 
            font=("Helvetica", 11, "bold"),
            bg="#1b5e20", 
            fg=self.colors["text_light"],
            padx=20, 
            pady=10,
            bd=0,
            cursor="hand2",
            command=self.back_to_dashboard
        )
        back_btn.pack(side="left", padx=20, pady=10)
        
        # Add hover effect
        back_btn.bind("<Enter>", lambda e: back_btn.config(bg=self.colors["secondary"]))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg="#1b5e20"))
        
        # User info in footer
        user_label = tk.Label(
            footer_frame, 
            text=f"Logged in as: {self.username}", 
            font=("Helvetica", 9),
            bg=self.colors["primary"], 
            fg=self.colors["text_light"]
        )
        user_label.pack(side="right", padx=20, pady=15)
    
    def configure_styles(self):
        """Configure ttk styles for custom look with enhanced table visibility"""
        style = ttk.Style()
        
        # ENHANCED TABLE STYLING WITH BETTER VISIBILITY
        style.configure(
            "Custom.Treeview", 
            background="#e8f5e9",           # Light green background
            foreground="#000000",           # Black text for contrast
            rowheight=35,                   # Taller rows
            fieldbackground="#e8f5e9",
            font=("Arial", 12, "bold"),     # Larger, bolder text
            borderwidth=1                   # Add borders
        )
        
        # IMPROVED HEADER VISIBILITY - UPDATED TEXT COLOR
        style.configure(
            "Custom.Treeview.Heading", 
            background="#004d40",           # Darker teal green for headers
            foreground="#FFEB3B",           # BRIGHT YELLOW text for maximum visibility
            font=("Arial", 14, "bold"),     # Larger, bolder text
            relief="raised",                # Raised effect for headers
            borderwidth=2,                  # Thicker border
            padding=10                      # More padding in headers
        )
        
        # Add extra visual emphasis to headers by enabling hover effect
        style.map(
            "Custom.Treeview.Heading",
            background=[("active", "#00796b")],  # Slightly lighter when hovered
            foreground=[("active", "#FFF176")]   # Even brighter yellow when hovered
        )
        
        style.map(
            "Custom.Treeview",
            background=[("selected", "#43a047")],     # Brighter green when selected
            foreground=[("selected", "#ffffff")]      # White text when selected
        )
        
        # Style for Entry widgets
        style.configure(
            "Custom.TEntry", 
            fieldbackground="white"
        )
    
    def load_data(self):
        """Load map locations with high contrast styling for better visibility"""
        try:
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Use the correct table name with underscore
            self.cursor.execute("SELECT * FROM map_location ORDER BY id DESC")
            rows = self.cursor.fetchall()
            
            if not rows:
                # Insert a placeholder message when no data exists
                self.tree.insert("", "end", values=("NO DATA AVAILABLE", "-", "-", "-"), tags=("nodata",))
                self.tree.tag_configure("nodata", background="#ffcdd2", foreground="#d32f2f", font=("Arial", 13, "bold"))
                return
            
            # Add data to treeview with higher contrast colors
            for i, row in enumerate(rows):
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                self.tree.insert("", "end", values=row, tags=(tag,))
            
            # Configure tag colors with better contrast
            self.tree.tag_configure("evenrow", background="#c8e6c9", foreground="#000000")  # Darker green bg
            self.tree.tag_configure("oddrow", background="#e8f5e9", foreground="#000000")   # Lighter green bg
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load map location data: {str(e)}")
            print(f"Database error: {e}")  # Debug output
    
    def add_location(self):
        """Add a new location with improved validation and feedback"""
        sanctuary_id = self.sanctuary_id_entry.get().strip()
        latitude = self.latitude_entry.get().strip()
        longitude = self.longitude_entry.get().strip()
        
        # Input validation
        if not sanctuary_id or not latitude or not longitude:
            messagebox.showwarning(
                "Input Error", 
                "Please provide all the required details.",
                icon="warning"
            )
            return
        
        # Validate numeric inputs
        try:
            sanctuary_id = int(sanctuary_id)
            latitude = float(latitude)
            longitude = float(longitude)
            
            # Basic coordinate validation
            if not (-90 <= latitude <= 90):
                messagebox.showwarning("Input Error", "Latitude must be between -90 and 90.")
                return
                
            if not (-180 <= longitude <= 180):
                messagebox.showwarning("Input Error", "Longitude must be between -180 and 180.")
                return
                
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter valid numeric values.")
            return
        
        try:
            # Verify the sanctuary exists
            self.cursor.execute("SELECT * FROM Sanctuaries WHERE id = %s", (sanctuary_id,))
            if not self.cursor.fetchone():
                messagebox.showwarning(
                    "Invalid Reference", 
                    f"No sanctuary found with ID {sanctuary_id}. Please verify the ID."
                )
                return
            
            # Insert the new location
            self.cursor.execute(
                "INSERT INTO map_location (sanctuary_id, latitude, longitude) VALUES (%s, %s, %s)",
                (sanctuary_id, latitude, longitude)
            )
            self.conn.commit()
            
            # Success message
            messagebox.showinfo(
                "Success", 
                "Location added successfully!",
                icon="info"
            )
            
            # Refresh the table and clear form
            self.load_data()
            self.sanctuary_id_entry.delete(0, tk.END)
            self.latitude_entry.delete(0, tk.END)
            self.longitude_entry.delete(0, tk.END)
            
        except mysql.connector.Error as e:
            error_msg = str(e)
            if "foreign key constraint fails" in error_msg.lower():
                messagebox.showerror(
                    "Database Error", 
                    f"The sanctuary ID {sanctuary_id} does not exist. Please enter a valid sanctuary ID."
                )
            else:
                messagebox.showerror("Database Error", error_msg)
    
    def delete_location(self):
        """Delete a location with improved confirmation and feedback"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning(
                "Selection Required", 
                "Please select a location to delete.",
                icon="warning"
            )
            return
        
        # Get the values from the selected row
        values = self.tree.item(selected)['values']
        
        # Check if it's the placeholder "No data" row
        if values[0] == "No data":
            return
        
        location_id = values[0]
        
        # Confirmation with more details
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete location ID {location_id}?\n\n"
            f"Sanctuary ID: {values[1]}\n"
            f"Coordinates: {values[2]}, {values[3]}\n\n"
            "This action cannot be undone.",
            icon="question"
        )
        
        if confirm:
            try:
                self.cursor.execute("DELETE FROM map_location WHERE id = %s", (location_id,))
                self.conn.commit()
                
                # Success message
                messagebox.showinfo(
                    "Success", 
                    "Location deleted successfully!",
                    icon="info"
                )
                
                self.load_data()
                
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", str(e))
    
    def back_to_dashboard(self):
        """Return to dashboard with proper cleanup"""
        # Close db connection
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        
        self.root.destroy()
        # Use importlib for better import handling
        dashboard_module = importlib.import_module("dashboard")
        dashboard_module.Dashboard(self.username)

# For direct testing
if __name__ == "__main__":
    MapLocation("Admin")
