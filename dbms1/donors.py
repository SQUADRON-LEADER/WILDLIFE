import tkinter as tk
from tkinter import ttk, messagebox, font
import mysql.connector
from datetime import date
import dashboard
from tkcalendar import DateEntry  # You may need to install this: pip install tkcalendar

class Donors:
    def __init__(self, username):
        self.username = username
        
        # Connect to database
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="11223344",
            database="WildGuardDB"
        )
        self.cursor = self.conn.cursor(buffered=True)
        
        # Create triggers if they don't exist
        self.setup_triggers()
        
        # Setup UI
        self.root = tk.Tk()
        self.root.title("💰 Donors Management")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f5f7fa")
        self.setup_ui()
        self.load_data()
        self.root.mainloop()

    def setup_triggers(self):
        """Set up MySQL triggers for donors table"""
        try:
            # Trigger to log donation activities
            self.cursor.execute("""
            DROP TRIGGER IF EXISTS after_donor_insert
            """)
            
            self.cursor.execute("""
            CREATE TRIGGER after_donor_insert
            AFTER INSERT ON Donors
            FOR EACH ROW
            BEGIN
                INSERT INTO ActivityLog (activity_type, description, user, timestamp)
                VALUES ('DONATION', CONCAT('New donation of $', NEW.amount_donated, ' received from ', NEW.name), 
                        'system', NOW());
            END
            """)
            
            # Trigger to validate donation amount
            self.cursor.execute("""
            DROP TRIGGER IF EXISTS before_donor_insert
            """)
            
            self.cursor.execute("""
            CREATE TRIGGER before_donor_insert
            BEFORE INSERT ON Donors
            FOR EACH ROW
            BEGIN
                IF NEW.amount_donated <= 0 THEN
                    SIGNAL SQLSTATE '45000' 
                    SET MESSAGE_TEXT = 'Donation amount must be positive';
                END IF;
            END
            """)
            
            # Ensure we have an ActivityLog table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ActivityLog (
                id INT AUTO_INCREMENT PRIMARY KEY,
                activity_type VARCHAR(50),
                description TEXT,
                user VARCHAR(100),
                timestamp DATETIME
            )
            """)
            
            self.conn.commit()
            print("Triggers set up successfully")
        except mysql.connector.Error as err:
            print(f"Error setting up triggers: {err}")

    def setup_ui(self):
        """Setup the user interface"""
        # Custom styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure treeview colors
        self.style.configure("Treeview", 
                            background="#f0f0f0",
                            foreground="black",
                            rowheight=25,
                            fieldbackground="#f0f0f0",
                            font=('Arial', 10))
        
        self.style.map('Treeview', 
                      background=[('selected', '#4a7abc')],
                      foreground=[('selected', 'white')])
        
        # Configure headings
        self.style.configure("Treeview.Heading", 
                            font=('Arial', 11, 'bold'),
                            background="#3a5998",
                            foreground="white")
        
        # Button styles
        self.style.configure("Add.TButton", 
                            font=('Arial', 10, 'bold'),
                            background="#27ae60", 
                            foreground="white")
        
        self.style.configure("Delete.TButton", 
                            font=('Arial', 10, 'bold'),
                            background="#e74c3c", 
                            foreground="white")
        
        # Header with shadow effect
        header_frame = tk.Frame(self.root, bg="#3a5998", height=80)
        header_frame.pack(fill="x")
        
        # Add shadow frame
        shadow_frame = tk.Frame(self.root, height=5, bg="#2c3e50")
        shadow_frame.pack(fill="x")
        
        # Header text
        tk.Label(header_frame, 
                text="💰 Donor Management System", 
                font=("Arial", 22, "bold"), 
                bg="#3a5998", 
                fg="white").pack(pady=20)
        
        # Stats panel
        stats_frame = tk.Frame(self.root, bg="#f5f7fa", padx=20, pady=10)
        stats_frame.pack(fill="x")
        
        # Get statistics
        total_donors, total_amount, avg_donation = self.get_donation_stats()
        
        # Create stat cards
        self.create_stat_card(stats_frame, "Total Donors", total_donors, "#3498db", 0)
        self.create_stat_card(stats_frame, "Total Donations", f"${total_amount:,.2f}", "#27ae60", 1)
        self.create_stat_card(stats_frame, "Average Donation", f"${avg_donation:,.2f}", "#e67e22", 2)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg="#f5f7fa", padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)
        
        # Form panel with title and border
        form_panel = tk.LabelFrame(main_frame, text=" Add New Donor ", font=('Arial', 12, 'bold'), 
                                  bg="white", fg="#3a5998", padx=15, pady=15)
        form_panel.pack(fill="x", pady=10)
        
        # Form grid with better spacing
        form = tk.Frame(form_panel, bg="white")
        form.pack(pady=5)
        
        # Form fields with better labels and styling
        tk.Label(form, text="Name:", font=('Arial', 10, 'bold'), bg="white", fg="#333").grid(row=0, column=0, padx=10, pady=8, sticky="e")
        self.name_entry = ttk.Entry(form, width=25, font=('Arial', 10))
        self.name_entry.grid(row=0, column=1, padx=5, pady=8, sticky="w")
        
        tk.Label(form, text="Email:", font=('Arial', 10, 'bold'), bg="white", fg="#333").grid(row=0, column=2, padx=10, pady=8, sticky="e")
        self.email_entry = ttk.Entry(form, width=25, font=('Arial', 10))
        self.email_entry.grid(row=0, column=3, padx=5, pady=8, sticky="w")
        
        tk.Label(form, text="Amount ($):", font=('Arial', 10, 'bold'), bg="white", fg="#333").grid(row=1, column=0, padx=10, pady=8, sticky="e")
        self.amount_entry = ttk.Entry(form, width=25, font=('Arial', 10))
        self.amount_entry.grid(row=1, column=1, padx=5, pady=8, sticky="w")
        
        tk.Label(form, text="Date:", font=('Arial', 10, 'bold'), bg="white", fg="#333").grid(row=1, column=2, padx=10, pady=8, sticky="e")
        
        # Calendar date picker for better date input
        self.date_entry = DateEntry(form, width=23, background='#3a5998',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                                   font=('Arial', 10))
        self.date_entry.grid(row=1, column=3, padx=5, pady=8, sticky="w")
        
        # Buttons frame for better alignment
        buttons_frame = tk.Frame(form, bg="white")
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=15)
        
        # Styled buttons
        add_btn = tk.Button(buttons_frame, text="➕ Add Donor", command=self.add_donor,
                          bg="#27ae60", fg="white", font=('Arial', 10, 'bold'),
                          padx=15, pady=5, bd=0, cursor="hand2")
        add_btn.pack(side=tk.LEFT, padx=10)
        
        clear_btn = tk.Button(buttons_frame, text="🔄 Clear Form", command=self.clear_fields,
                            bg="#3498db", fg="white", font=('Arial', 10, 'bold'),
                            padx=15, pady=5, bd=0, cursor="hand2")
        clear_btn.pack(side=tk.LEFT, padx=10)
        
        delete_btn = tk.Button(buttons_frame, text="❌ Delete Selected", command=self.delete_donor,
                             bg="#e74c3c", fg="white", font=('Arial', 10, 'bold'),
                             padx=15, pady=5, bd=0, cursor="hand2")
        delete_btn.pack(side=tk.LEFT, padx=10)
        
        # Table panel with title
        table_panel = tk.LabelFrame(main_frame, text=" Donors List ", font=('Arial', 12, 'bold'), 
                                   bg="white", fg="#3a5998", padx=15, pady=15)
        table_panel.pack(fill="both", expand=True, pady=10)
        
        # Search frame
        search_frame = tk.Frame(table_panel, bg="white")
        search_frame.pack(fill="x", pady=5)
        
        tk.Label(search_frame, text="Search:", font=('Arial', 10, 'bold'), bg="white").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.filter_data())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30, font=('Arial', 10))
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Treeview with scrollbar
        tree_frame = tk.Frame(table_panel, bg="white")
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal')
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Email", "Amount", "Date"), show="headings")
        
        # Configure columns
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=200)
        self.tree.column("Email", width=250)
        self.tree.column("Amount", width=100, anchor="e")
        self.tree.column("Date", width=100, anchor="center")
        
        # Configure headings
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            
        # Configure scrollbars
        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        y_scrollbar.configure(command=self.tree.yview)
        x_scrollbar.configure(command=self.tree.xview)
        
        # Pack the treeview
        self.tree.pack(fill="both", expand=True)
        
        # Bind click event for row selection
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        
        # ADD THIS AT THE VERY END of setup_ui method - after all other UI elements
        
        # First destroy any existing footer frame that might be causing conflicts
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) and hasattr(widget, 'is_footer_frame'):
                widget.destroy()
        
        # Create a completely standalone footer frame
        footer_frame = tk.Frame(self.root, bg="#3a5998", height=70)
        footer_frame.is_footer_frame = True  # Mark it for identification
        
        # Use place instead of pack for absolute positioning
        footer_frame.place(x=0, y=self.root.winfo_height()-70, 
                          width=self.root.winfo_width(), height=70)
        
        # Make the back button SUPER prominent - can't be missed
        back_btn = tk.Button(
            footer_frame, 
            text="⬅️ RETURN TO DASHBOARD", 
            command=self.back_to_dashboard,  
            bg="#ff5722",  # Even brighter orange
            fg="white", 
            font=('Arial', 16, 'bold'),
            padx=30, 
            pady=12,
            bd=2,
            cursor="hand2",
            relief="raised"
        )
        
        # Center the button in the footer
        back_btn.place(relx=0.5, rely=0.5, anchor="center")
        
        # Add hover effects
        back_btn.bind("<Enter>", lambda e: back_btn.config(bg="#e64a19", relief="sunken"))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg="#ff5722", relief="raised"))
        
        # Add keyboard shortcut (Escape key returns to dashboard)
        self.root.bind("<Escape>", lambda e: self.back_to_dashboard())
        
        # Update footer position when window resizes
        self.root.bind("<Configure>", lambda e: footer_frame.place(
            x=0, y=self.root.winfo_height()-70, 
            width=self.root.winfo_width(), height=70)
        )

    def create_stat_card(self, parent, title, value, color, column):
        """Create a statistic card with a nice design"""
        card = tk.Frame(parent, bg="white", padx=15, pady=15, bd=0, highlightthickness=1, highlightbackground="#ddd")
        card.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        
        # Configure the grid to expand evenly
        parent.grid_columnconfigure(column, weight=1)
        
        # Title
        tk.Label(card, text=title, font=("Arial", 12), bg="white", fg="#555").pack(anchor="w")
        
        # Value with color
        tk.Label(card, text=value, font=("Arial", 20, "bold"), bg="white", fg=color).pack(anchor="w", pady=(5, 0))

    def get_donation_stats(self):
        """Get donation statistics for dashboard"""
        try:
            # Get total donors
            self.cursor.execute("SELECT COUNT(*) FROM Donors")
            total_donors = self.cursor.fetchone()[0] or 0
            
            self.cursor.execute("SELECT SUM(amount_donated) FROM Donors")
            total_amount = self.cursor.fetchone()[0] or 0
            
            avg_donation = total_amount / total_donors if total_donors > 0 else 0
            
            return total_donors, total_amount, avg_donation
        except mysql.connector.Error as err:
            print(f"Error getting statistics: {err}")
            return 0, 0, 0

    def load_data(self):
        """Load donor data into the treeview"""
        self.tree.delete(*self.tree.get_children())
        
        try:
            self.cursor.execute("SELECT * FROM Donors ORDER BY donation_date DESC")
            rows = self.cursor.fetchall()
            
            
            for i, row in enumerate(rows):
                
                formatted_amount = f"${row[3]:,.2f}"
                values = (row[0], row[1], row[2], formatted_amount, row[4])
                
                
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                
                
                if row[3] >= 1000:
                    amount_tag = "large_donation"
                elif row[3] >= 500:
                    amount_tag = "medium_donation"
                else:
                    amount_tag = "small_donation"
                
                self.tree.insert("", "end", values=values, tags=(tag, amount_tag))
            
           
            self.tree.tag_configure("evenrow", background="#ffffff")
            self.tree.tag_configure("oddrow", background="#f0f8ff")
            self.tree.tag_configure("large_donation", foreground="#27ae60") 
            self.tree.tag_configure("medium_donation", foreground="#e67e22") 
            self.tree.tag_configure("small_donation", foreground="#3498db")  
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading data: {err}")

    def filter_data(self):
        """Filter treeview data based on search term"""
        search_term = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        
        try:
            self.cursor.execute("""
                SELECT * FROM Donors 
                WHERE LOWER(name) LIKE %s OR LOWER(email) LIKE %s 
                ORDER BY donation_date DESC
            """, (f"%{search_term}%", f"%{search_term}%"))
            
            rows = self.cursor.fetchall()
            
            # Add filtered data to the treeview
            for i, row in enumerate(rows):
                formatted_amount = f"${row[3]:,.2f}"
                values = (row[0], row[1], row[2], formatted_amount, row[4])
                
                # Add to treeview with alternating colors
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                
                # Add donation amount color tags
                if row[3] >= 1000:
                    amount_tag = "large_donation"
                elif row[3] >= 500:
                    amount_tag = "medium_donation"
                else:
                    amount_tag = "small_donation"
                
                self.tree.insert("", "end", values=values, tags=(tag, amount_tag))
                
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error filtering data: {err}")

    def add_donor(self):
        """Add a new donor to the database"""
        name = self.name_entry.get()
        email = self.email_entry.get()
        amount = self.amount_entry.get()
        donation_date = self.date_entry.get()

        if not all([name, email, amount, donation_date]):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        try:
            # Convert amount to float for validation
            float_amount = float(amount)
            
            # The trigger will handle validation of positive amount
            self.cursor.execute(
                "INSERT INTO Donors (name, email, amount_donated, donation_date) VALUES (%s, %s, %s, %s)",
                (name, email, float_amount, donation_date)
            )
            self.conn.commit()
            
            # Update stats and reload data
            self.load_data()
            self.clear_fields()
            
            # Update stats display
            stats_frame = self.root.winfo_children()[3]  # Get the stats frame
            for widget in stats_frame.winfo_children():
                widget.destroy()
                
            # Recreate stat cards with updated data
            total_donors, total_amount, avg_donation = self.get_donation_stats()
            self.create_stat_card(stats_frame, "Total Donors", total_donors, "#3498db", 0)
            self.create_stat_card(stats_frame, "Total Donations", f"${total_amount:,.2f}", "#27ae60", 1)
            self.create_stat_card(stats_frame, "Average Donation", f"${avg_donation:,.2f}", "#e67e22", 2)
            
            messagebox.showinfo("Success", "Donor added successfully.")
        except mysql.connector.Error as err:
            if "Donation amount must be positive" in str(err):
                messagebox.showerror("Validation Error", "Donation amount must be positive.")
            else:
                messagebox.showerror("Database Error", f"Error adding donor: {str(err)}")
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a valid number.")

    def delete_donor(self):
        """Delete selected donor"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select a donor", "Please select a donor to delete.")
            return
        
        donor_id = self.tree.item(selected)['values'][0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this donor?")
        
        if confirm:
            try:
                self.cursor.execute("DELETE FROM Donors WHERE id = %s", (donor_id,))
                self.conn.commit()
                
                # Log the activity manually (not through trigger since this is DELETE)
                self.cursor.execute("""
                    INSERT INTO ActivityLog (activity_type, description, user, timestamp)
                    VALUES ('DELETION', %s, %s, NOW())
                """, (f"Donor ID {donor_id} deleted", self.username))
                self.conn.commit()
                
                # Update display
                self.load_data()
                
                # Update stats
                stats_frame = self.root.winfo_children()[3]
                for widget in stats_frame.winfo_children():
                    widget.destroy()
                    
                total_donors, total_amount, avg_donation = self.get_donation_stats()
                self.create_stat_card(stats_frame, "Total Donors", total_donors, "#3498db", 0)
                self.create_stat_card(stats_frame, "Total Donations", f"${total_amount:,.2f}", "#27ae60", 1)
                self.create_stat_card(stats_frame, "Average Donation", f"${avg_donation:,.2f}", "#e67e22", 2)
                
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error deleting donor: {str(err)}")

    def on_tree_double_click(self, event):
        """Handle double-click event to populate form for editing"""
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected)['values']
            
            # Clear form
            self.clear_fields()
            
            # Populate form with selected data
            self.name_entry.insert(0, values[1])
            self.email_entry.insert(0, values[2])
            self.amount_entry.insert(0, values[3].replace('$', '').replace(',', ''))
            self.date_entry.set_date(values[4])
            
            # Instead of updating, we'll delete and re-add
            self.tree.selection_set(selected)

    def clear_fields(self):
        """Clear all form fields"""
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.date_entry.set_date(date.today())

    def back_to_dashboard(self):
        """Guaranteed return to dashboard"""
        try:
            # Close database connections properly first
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
                
            # Destroy the window
            self.root.destroy()
            
            # Create new dashboard directly
            dashboard.Dashboard(self.username)
            
        except Exception as e:
            print(f"Error in back_to_dashboard: {e}")
            
            # Emergency fallback - create a new window and show dashboard
            try:
                top = tk.Tk()
                top.withdraw()  # Hide the empty root window
                messagebox.showinfo("Navigation", "Returning to dashboard...")
                top.destroy()
                
                import os
                import sys
                
                # Restart the application completely as a last resort
                python = sys.executable
                os.execl(python, python, *sys.argv)
                
            except Exception as e2:
                print(f"Critical error: {e2}")
                # If all else fails, exit the application
                sys.exit(0)

if __name__ == "__main__":
    Donors("Admin")
