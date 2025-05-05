import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import importlib
from datetime import datetime
import traceback

class WildlifeResearchApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title("Wildlife Research Database")
        self.root.geometry("950x650")
        self.root.configure(bg="#f0f5e7")
        
        # Database connection
        try:
            print("Attempting to connect to database...")
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="11223344",
                database="WildGuardDB"
            )
            self.cursor = self.conn.cursor(buffered=True)
            print("Database connected successfully")
            
            # Create table if not exists
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS wildlife_research (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                researcher VARCHAR(100) NOT NULL,
                species VARCHAR(100) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                location VARCHAR(100),
                status VARCHAR(20),
                findings TEXT,
                created_by VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            self.conn.commit()
            print("Table created or verified")
            
            # Check if we need to add sample data
            self.cursor.execute("SELECT COUNT(*) FROM wildlife_research")
            count = self.cursor.fetchone()[0]
            print(f"Found {count} existing research records")
            
            if count == 0:
                print("No data found, adding sample data automatically...")
                self.add_sample_data(silent=True)
            
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
            return
        
        # Header with back button
        header_frame = tk.Frame(root, bg="#1e8449", height=60)
        header_frame.pack(fill="x")
        
        back_btn = tk.Button(header_frame, text="← Back to Dashboard", 
                           command=self.back_to_dashboard,
                           bg="#1e8449", fg="white", bd=0)
        back_btn.pack(side="left", padx=10, pady=10)
        
        tk.Label(header_frame, text="🔬 Wildlife Research Database", 
               font=("Helvetica", 16, "bold"), 
               bg="#1e8449", fg="white").pack(pady=10)
        
        # Main content frame
        content_frame = tk.Frame(root, bg="#f0f5e7")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab 1: Research Projects
        projects_tab = tk.Frame(self.notebook, bg="#f0f5e7")
        self.notebook.add(projects_tab, text="Research Projects")
        
        # Tab 2: Add New Research
        add_tab = tk.Frame(self.notebook, bg="#f0f5e7")
        self.notebook.add(add_tab, text="Add New Research")
        
        # Tab 3: Research Statistics
        stats_tab = tk.Frame(self.notebook, bg="#f0f5e7")
        self.notebook.add(stats_tab, text="Statistics")
        
        # Setup Projects Tab
        self.setup_projects_tab(projects_tab)
        
        # Setup Add Research Tab
        self.setup_add_tab(add_tab)
        
        # Setup Statistics Tab
        self.setup_stats_tab(stats_tab)
        
        # Initial load of data
        self.load_research_projects()
    
    def setup_projects_tab(self, parent):
        """Setup the projects listing tab"""
        # Create frame for filters
        filter_frame = tk.Frame(parent, bg="#f0f5e7")
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # Status filter
        tk.Label(filter_frame, text="Filter by Status:", bg="#f0f5e7").pack(side="left", padx=5)
        self.status_var = tk.StringVar(value="All")
        status_cb = ttk.Combobox(filter_frame, textvariable=self.status_var, 
                                values=["All", "Ongoing", "Completed", "Planned", "Cancelled"],
                                width=15, state="readonly")
        status_cb.pack(side="left", padx=5)
        status_cb.bind("<<ComboboxSelected>>", lambda e: self.load_research_projects())
        
        # Species filter
        tk.Label(filter_frame, text="Species:", bg="#f0f5e7").pack(side="left", padx=5)
        self.species_filter = tk.Entry(filter_frame, width=15)
        self.species_filter.pack(side="left", padx=5)
        
        # Search button
        tk.Button(filter_frame, text="Search", 
                 command=self.load_research_projects,
                 bg="#3498db", fg="white").pack(side="left", padx=5)
        
        # Reset button
        tk.Button(filter_frame, text="Reset", 
                 command=self.reset_filters,
                 bg="#95a5a6", fg="white").pack(side="left", padx=5)
        
        # Treeview for research projects
        columns = ('id', 'title', 'researcher', 'species', 'start_date', 'status', 'location')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings')
        
        # Define headings with sortable click
        for col in columns:
            header_text = col.replace('_', ' ').title()
            self.tree.heading(col, text=header_text, command=lambda c=col: self.sort_by(c, False))
        
        # Column widths
        self.tree.column('id', width=40)
        self.tree.column('title', width=200)
        self.tree.column('researcher', width=120)
        self.tree.column('species', width=120)
        self.tree.column('start_date', width=100)
        self.tree.column('status', width=80)
        self.tree.column('location', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        
        # Button frame
        btn_frame = tk.Frame(parent, bg="#f0f5e7")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="View Details", 
                 command=self.view_research,
                 bg="#3498db", fg="white", width=12).pack(side="left", padx=5)
                 
        tk.Button(btn_frame, text="Edit", 
                 command=self.edit_research,
                 bg="#f39c12", fg="white", width=12).pack(side="left", padx=5)
                 
        tk.Button(btn_frame, text="Delete", 
                 command=self.delete_research,
                 bg="#e74c3c", fg="white", width=12).pack(side="left", padx=5)

        # Add reload button
        tk.Button(btn_frame, text="Reload Data", 
                command=self.load_research_projects,
                bg="#27ae60", fg="white", width=12).pack(side="left", padx=5)
        
        # Context menu
        self.context_menu = tk.Menu(parent, tearoff=0)
        self.context_menu.add_command(label="View Details", command=self.view_research)
        self.context_menu.add_command(label="Edit Research", command=self.edit_research)
        self.context_menu.add_command(label="Delete Research", command=self.delete_research)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self.view_research())
    
    def setup_add_tab(self, parent):
        """Setup the add new research tab"""
        # Create form with labels and entries
        form_frame = tk.Frame(parent, bg="#f0f5e7", padx=20, pady=20)
        form_frame.pack(fill="both", expand=True)
        
        # Title
        tk.Label(form_frame, text="Research Title:", bg="#f0f5e7", anchor="e").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.title_entry = tk.Entry(form_frame, width=40)
        self.title_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Researcher
        tk.Label(form_frame, text="Researcher Name:", bg="#f0f5e7", anchor="e").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.researcher_entry = tk.Entry(form_frame, width=40)
        self.researcher_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Species
        tk.Label(form_frame, text="Species Studied:", bg="#f0f5e7", anchor="e").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.species_entry = tk.Entry(form_frame, width=40)
        self.species_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Start Date
        tk.Label(form_frame, text="Start Date (YYYY-MM-DD):", bg="#f0f5e7", anchor="e").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.start_date_entry = tk.Entry(form_frame, width=40)
        self.start_date_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        self.start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # End Date (Optional)
        tk.Label(form_frame, text="End Date (Optional):", bg="#f0f5e7", anchor="e").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.end_date_entry = tk.Entry(form_frame, width=40)
        self.end_date_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        # Location
        tk.Label(form_frame, text="Research Location:", bg="#f0f5e7", anchor="e").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.location_entry = tk.Entry(form_frame, width=40)
        self.location_entry.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        
        # Status
        tk.Label(form_frame, text="Status:", bg="#f0f5e7", anchor="e").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        self.status_var = tk.StringVar(value="Ongoing")
        self.status_combo = ttk.Combobox(form_frame, textvariable=self.status_var, 
                                       values=["Ongoing", "Completed", "Planned", "Cancelled"],
                                       width=38, state="readonly")
        self.status_combo.grid(row=6, column=1, sticky="w", padx=5, pady=5)
        
        # Findings
        tk.Label(form_frame, text="Research Findings:", bg="#f0f5e7", anchor="e").grid(row=7, column=0, sticky="ne", padx=5, pady=5)
        self.findings_text = tk.Text(form_frame, width=40, height=8)
        self.findings_text.grid(row=7, column=1, sticky="w", padx=5, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg="#f0f5e7")
        btn_frame.grid(row=8, column=0, columnspan=2, pady=15)
        
        tk.Button(btn_frame, text="Save Research", 
                 command=self.save_research,
                 bg="#27ae60", fg="white", width=15).pack(side="left", padx=5)
                 
        tk.Button(btn_frame, text="Clear Form", 
                 command=self.clear_form,
                 bg="#e74c3c", fg="white", width=15).pack(side="left", padx=5)
    
    def setup_stats_tab(self, parent):
        """Setup the statistics tab"""
        stats_frame = tk.Frame(parent, bg="#f0f5e7", padx=20, pady=20)
        stats_frame.pack(fill="both", expand=True)
        
        tk.Label(stats_frame, text="Research Statistics", font=("Helvetica", 16, "bold"), 
               bg="#f0f5e7").pack(pady=10)
        
        # Create frames for stats
        stats_boxes = tk.Frame(stats_frame, bg="#f0f5e7")
        stats_boxes.pack(fill="x", pady=20, padx=20)
        
        # Create stat boxes
        stat_bg_colors = ["#3498db", "#2ecc71", "#e67e22", "#e74c3c"]
        self.stat_labels = {}
        
        # Total projects
        self.create_stat_box(stats_boxes, "Total Research Projects", "total", stat_bg_colors[0], 0)
        
        # Ongoing projects
        self.create_stat_box(stats_boxes, "Ongoing Research", "ongoing", stat_bg_colors[1], 1)
        
        # Completed projects
        self.create_stat_box(stats_boxes, "Completed Research", "completed", stat_bg_colors[2], 2)
        
        # Species count
        self.create_stat_box(stats_boxes, "Unique Species Studied", "species", stat_bg_colors[3], 3)
        
        # Stats by researcher frame
        tk.Label(stats_frame, text="Research by Researcher", font=("Helvetica", 14), 
               bg="#f0f5e7").pack(pady=(20,10))
        
        # Treeview for researcher stats
        researcher_frame = tk.Frame(stats_frame, bg="#f0f5e7")
        researcher_frame.pack(fill="both", expand=True)
        
        columns = ('researcher', 'total_projects', 'ongoing', 'completed')
        self.researcher_tree = ttk.Treeview(researcher_frame, columns=columns, show='headings', height=6)
        
        # Define headings
        self.researcher_tree.heading('researcher', text='Researcher')
        self.researcher_tree.heading('total_projects', text='Total Projects')
        self.researcher_tree.heading('ongoing', text='Ongoing')
        self.researcher_tree.heading('completed', text='Completed')
        
        # Column widths
        self.researcher_tree.column('researcher', width=200)
        self.researcher_tree.column('total_projects', width=100)
        self.researcher_tree.column('ongoing', width=100)
        self.researcher_tree.column('completed', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(researcher_frame, orient="vertical", command=self.researcher_tree.yview)
        self.researcher_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.researcher_tree.pack(side="left", fill="both", expand=True)
        
        # Control buttons
        btn_frame = tk.Frame(stats_frame, bg="#f0f5e7")
        btn_frame.pack(pady=10)
        
        # Refresh button
        tk.Button(btn_frame, text="Refresh Statistics", 
                 command=self.load_statistics,
                 bg="#3498db", fg="white", width=15).pack(side="left", padx=5)
                 
        # Add sample data button (only show if needed)
        tk.Button(btn_frame, text="Add Sample Data", 
                 command=lambda: self.add_sample_data(silent=False),
                 bg="#f39c12", fg="white", width=15).pack(side="left", padx=5)
                 
        # Initial load of statistics
        self.load_statistics()
    
    def create_stat_box(self, parent, title, key, bg_color, col_pos):
        """Create a statistics box"""
        box = tk.Frame(parent, bg=bg_color, width=150, height=100, padx=10, pady=10)
        box.grid(row=0, column=col_pos, padx=10)
        box.grid_propagate(False)  # Maintain fixed size
        
        tk.Label(box, text=title, bg=bg_color, fg="white", 
               font=("Helvetica", 10, "bold")).pack(pady=(10,5))
               
        # Create label to hold the value
        value_lbl = tk.Label(box, text="0", bg=bg_color, fg="white", 
                           font=("Helvetica", 24, "bold"))
        value_lbl.pack(pady=5)
        
        # Store reference to update later
        self.stat_labels[key] = value_lbl
    
    def check_db_connection(self):
        """Check and restore database connection if needed"""
        try:
            if not self.conn or not self.conn.is_connected():
                print("Reconnecting to database...")
                self.conn = mysql.connector.connect(
                    host="localhost",
                    user="root", 
                    password="11223344",
                    database="WildGuardDB"
                )
                self.cursor = self.conn.cursor(buffered=True)
                print("Connection restored successfully")
            return True
        except mysql.connector.Error as err:
            print(f"Connection error: {err}")
            messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
            return False
    
    def sort_by(self, col, reverse):
        """Sort treeview by column"""
        try:
            data = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
            
            # Convert ID to integer for proper sorting
            if col == 'id':
                data = [(int(item[0]) if item[0].isdigit() else item[0], item[1]) for item in data]
            
            # Sort data
            data.sort(reverse=reverse)
            
            # Rearrange items in sorted order
            for index, (val, item) in enumerate(data):
                self.tree.move(item, '', index)
            
            # Switch direction for next click
            self.tree.heading(col, command=lambda: self.sort_by(col, not reverse))
        
        except Exception as e:
            print(f"Error sorting data: {e}")
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def reset_filters(self):
        """Reset all filters to default"""
        self.status_var.set("All")
        self.species_filter.delete(0, tk.END)
        self.load_research_projects()
    
    def load_research_projects(self):
        """Load research projects from database using filters"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.check_db_connection():
            return
            
        try:
            # Build query based on filters
            query = "SELECT id, title, researcher, species, start_date, status, location FROM wildlife_research"
            conditions = []
            params = []
            
            # Status filter
            if hasattr(self, 'status_var') and self.status_var.get() != "All":
                conditions.append("status = %s")
                params.append(self.status_var.get())
            
            # Species filter
            if hasattr(self, 'species_filter'):
                species_filter = self.species_filter.get().strip()
                if species_filter:
                    conditions.append("species LIKE %s")
                    params.append(f"%{species_filter}%")
            
            # Add WHERE clause if needed
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY start_date DESC"
            
            print(f"Executing query: {query}")
            print(f"With params: {params}")
            
            self.cursor.execute(query, params)
            projects = self.cursor.fetchall()
            
            print(f"Found {len(projects)} research projects")
            
            # Populate treeview
            for project in projects:
                # Format date for display
                project_list = list(project)
                if project[4]:  # start_date
                    project_list[4] = project[4].strftime("%Y-%m-%d")
                
                self.tree.insert('', 'end', values=project_list)
                
            # If no data found, offer to add sample data
            if len(projects) == 0:
                print("No data found in wildlife_research table")
                if messagebox.askyesno("No Data", "No research projects found. Would you like to add sample data?"):
                    self.add_sample_data()
                
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            print(traceback.format_exc())
            messagebox.showerror("Database Error", f"Failed to load research projects: {err}")
    
    def load_statistics(self):
        """Load and display statistics"""
        if not self.check_db_connection():
            return
            
        try:
            print("Loading statistics...")
            
            # Get total count
            self.cursor.execute("SELECT COUNT(*) FROM wildlife_research")
            total = self.cursor.fetchone()[0]
            self.stat_labels["total"].config(text=str(total))
            print(f"Total count: {total}")
            
            # Get ongoing count
            self.cursor.execute("SELECT COUNT(*) FROM wildlife_research WHERE status='Ongoing'")
            ongoing = self.cursor.fetchone()[0]
            self.stat_labels["ongoing"].config(text=str(ongoing))
            
            # Get completed count
            self.cursor.execute("SELECT COUNT(*) FROM wildlife_research WHERE status='Completed'")
            completed = self.cursor.fetchone()[0]
            self.stat_labels["completed"].config(text=str(completed))
            
            # Get unique species count
            self.cursor.execute("SELECT COUNT(DISTINCT species) FROM wildlife_research")
            species = self.cursor.fetchone()[0]
            self.stat_labels["species"].config(text=str(species))
            
            # Get researcher stats
            try:
                self.cursor.execute("""
                    SELECT 
                        researcher, 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'Ongoing' THEN 1 ELSE 0 END) as ongoing,
                        SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
                    FROM wildlife_research
                    GROUP BY researcher
                    ORDER BY total DESC
                """)
                
                # Clear existing data
                for item in self.researcher_tree.get_children():
                    self.researcher_tree.delete(item)
                    
                # Add researcher stats
                researcher_stats = self.cursor.fetchall()
                print(f"Found stats for {len(researcher_stats)} researchers")
                for stat in researcher_stats:
                    self.researcher_tree.insert('', 'end', values=stat)
                    
            except mysql.connector.Error as err:
                print(f"Error getting researcher stats: {err}")
                print(traceback.format_exc())
                
        except mysql.connector.Error as err:
            print(f"Statistics error: {err}")
            print(traceback.format_exc())
            messagebox.showerror("Statistics Error", f"Failed to load statistics: {err}")
    
    def save_research(self):
        """Save new research to database"""
        # Get values
        title = self.title_entry.get().strip()
        researcher = self.researcher_entry.get().strip()
        species = self.species_entry.get().strip()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip() or None
        location = self.location_entry.get().strip()
        status = self.status_var.get()
        findings = self.findings_text.get("1.0", tk.END).strip()
        
        # Validate
        if not title or not researcher or not species or not start_date or not status:
            messagebox.showwarning("Validation Error", "Title, researcher, species, start date and status are required.")
            return
        
        # Validate dates
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Date Error", "Dates must be in YYYY-MM-DD format.")
            return
        
        if not self.check_db_connection():
            return
            
        try:
            print(f"Saving research: {title} by {researcher}")
            
            # Insert into database
            self.cursor.execute("""
                INSERT INTO wildlife_research 
                (title, researcher, species, start_date, end_date, location, status, findings, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (title, researcher, species, start_date, end_date, location, status, findings, self.username))
            
            self.conn.commit()
            print(f"Research saved with ID: {self.cursor.lastrowid}")
            
            messagebox.showinfo("Success", "Research project saved successfully!")
            
            # Clear form
            self.clear_form()
            
            # Switch to projects tab and refresh
            self.notebook.select(0)
            self.load_research_projects()
            self.load_statistics()
            
        except mysql.connector.Error as err:
            print(f"Database error while saving: {err}")
            print(traceback.format_exc())
            messagebox.showerror("Database Error", f"Failed to save research: {err}")
    
    def clear_form(self):
        """Clear the add research form"""
        try:
            self.title_entry.delete(0, tk.END)
            self.researcher_entry.delete(0, tk.END)
            self.species_entry.delete(0, tk.END)
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Reset to today
            self.end_date_entry.delete(0, tk.END)
            self.location_entry.delete(0, tk.END)
            self.status_var.set("Ongoing")
            self.findings_text.delete("1.0", tk.END)
        except Exception as e:
            print(f"Error clearing form: {e}")
    
    def view_research(self):
        """View selected research details"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a research project to view.")
            return
        
        research_id = self.tree.item(selected[0])['values'][0]
        
        if not self.check_db_connection():
            return
            
        try:
            self.cursor.execute("""
                SELECT title, researcher, species, start_date, end_date, location, status, findings
                FROM wildlife_research
                WHERE id = %s
            """, (research_id,))
            
            research = self.cursor.fetchone()
            if not research:
                messagebox.showinfo("Not Found", "Research project not found.")
                return
                
            title, researcher, species, start_date, end_date, location, status, findings = research
            
            # Create detail window
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"Research: {title}")
            detail_window.geometry("600x500")
            detail_window.configure(bg="#f0f5e7")
            
            # Add details
            tk.Label(detail_window, text=title, font=("Helvetica", 16, "bold"), 
                   bg="#f0f5e7").pack(pady=(20, 5))
            
            # Details frame
            details_frame = tk.Frame(detail_window, bg="#f0f5e7", padx=20, pady=10)
            details_frame.pack(fill="x")
            
            # Two column layout for details
            left_col = tk.Frame(details_frame, bg="#f0f5e7")
            left_col.pack(side="left", padx=10, anchor="n")
            
            right_col = tk.Frame(details_frame, bg="#f0f5e7")
            right_col.pack(side="left", padx=10, anchor="n")
            
            # Left column details
            tk.Label(left_col, text="Researcher:", font=("Helvetica", 10, "bold"), 
                   bg="#f0f5e7", anchor="w").pack(fill="x", pady=2)
            tk.Label(left_col, text=researcher, bg="#f0f5e7", anchor="w").pack(fill="x", pady=(0, 5))
            
            tk.Label(left_col, text="Species:", font=("Helvetica", 10, "bold"), 
                   bg="#f0f5e7", anchor="w").pack(fill="x", pady=2)
            tk.Label(left_col, text=species, bg="#f0f5e7", anchor="w").pack(fill="x", pady=(0, 5))
            
            tk.Label(left_col, text="Status:", font=("Helvetica", 10, "bold"), 
                   bg="#f0f5e7", anchor="w").pack(fill="x", pady=2)
                   
            # Status with color
            status_frame = tk.Frame(left_col, bg="#f0f5e7")
            status_frame.pack(fill="x", pady=(0, 5))
            
            status_color = "#2ecc71" if status == "Ongoing" else "#e74c3c" if status == "Cancelled" else "#f39c12" if status == "Planned" else "#3498db"
            status_indicator = tk.Frame(status_frame, width=12, height=12, bg=status_color)
            status_indicator.pack(side="left", padx=(0, 5))
            tk.Label(status_frame, text=status or "Unknown", bg="#f0f5e7").pack(side="left")
            
            # Right column details
            tk.Label(right_col, text="Start Date:", font=("Helvetica", 10, "bold"), 
                   bg="#f0f5e7", anchor="w").pack(fill="x", pady=2)
            tk.Label(right_col, text=start_date.strftime("%Y-%m-%d") if start_date else "-", 
                   bg="#f0f5e7", anchor="w").pack(fill="x", pady=(0, 5))
            
            tk.Label(right_col, text="End Date:", font=("Helvetica", 10, "bold"), 
                   bg="#f0f5e7", anchor="w").pack(fill="x", pady=2)
            tk.Label(right_col, text=end_date.strftime("%Y-%m-%d") if end_date else "-", 
                   bg="#f0f5e7", anchor="w").pack(fill="x", pady=(0, 5))
            
            tk.Label(right_col, text="Location:", font=("Helvetica", 10, "bold"), 
                   bg="#f0f5e7", anchor="w").pack(fill="x", pady=2)
            tk.Label(right_col, text=location if location else "-", 
                   bg="#f0f5e7", anchor="w").pack(fill="x", pady=(0, 5))
            
            # Findings
            tk.Label(detail_window, text="Research Findings:", font=("Helvetica", 12, "bold"), 
                   bg="#f0f5e7", anchor="w").pack(fill="x", padx=20, pady=(20, 5))
            
            # Scrollable text widget for findings
            findings_frame = tk.Frame(detail_window, bg="#f0f5e7", padx=20)
            findings_frame.pack(fill="both", expand=True, pady=(0, 20))
            
            text_widget = tk.Text(findings_frame, wrap="word", height=10, width=60)
            scrollbar = ttk.Scrollbar(findings_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side="right", fill="y")
            text_widget.pack(side="left", fill="both", expand=True)
            
            text_widget.insert("1.0", findings if findings else "No findings recorded.")
            text_widget.config(state="disabled")  # Read-only
            
            # Close button
            tk.Button(detail_window, text="Close", 
                     command=detail_window.destroy,
                     bg="#3498db", fg="white", width=15).pack(pady=15)
            
        except mysql.connector.Error as err:
            print(f"Error viewing research: {err}")
            print(traceback.format_exc())
            messagebox.showerror("Database Error", f"Failed to retrieve research details: {err}")
    
    def edit_research(self):
        """Edit selected research"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a research project to edit.")
            return
        
        research_id = self.tree.item(selected[0])['values'][0]
        
        if not self.check_db_connection():
            return
            
        try:
            self.cursor.execute("""
                SELECT title, researcher, species, start_date, end_date, location, status, findings
                FROM wildlife_research
                WHERE id = %s
            """, (research_id,))
            
            research = self.cursor.fetchone()
            if not research:
                messagebox.showinfo("Not Found", "Research project not found.")
                return
                
            title, researcher, species, start_date, end_date, location, status, findings = research
            
            # Create edit window
            edit_window = tk.Toplevel(self.root)
            edit_window.title(f"Edit Research: {title}")
            edit_window.geometry("500x550")
            edit_window.configure(bg="#f0f5e7")
            
            tk.Label(edit_window, text="Edit Research Project", font=("Helvetica", 14, "bold"), 
                   bg="#f0f5e7").pack(pady=10)
            
            # Create form
            form_frame = tk.Frame(edit_window, bg="#f0f5e7", padx=20, pady=10)
            form_frame.pack(fill="both", expand=True)
            
            # Title
            tk.Label(form_frame, text="Research Title:", bg="#f0f5e7", anchor="e").grid(row=0, column=0, sticky="e", padx=5, pady=5)
            title_entry = tk.Entry(form_frame, width=30)
            title_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
            title_entry.insert(0, title or "")
            
            # Researcher
            tk.Label(form_frame, text="Researcher Name:", bg="#f0f5e7", anchor="e").grid(row=1, column=0, sticky="e", padx=5, pady=5)
            researcher_entry = tk.Entry(form_frame, width=30)
            researcher_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
            researcher_entry.insert(0, researcher or "")
            
            # Species
            tk.Label(form_frame, text="Species Studied:", bg="#f0f5e7", anchor="e").grid(row=2, column=0, sticky="e", padx=5, pady=5)
            species_entry = tk.Entry(form_frame, width=30)
            species_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
            species_entry.insert(0, species or "")
            
            # Start Date
            tk.Label(form_frame, text="Start Date (YYYY-MM-DD):", bg="#f0f5e7", anchor="e").grid(row=3, column=0, sticky="e", padx=5, pady=5)
            start_date_entry = tk.Entry(form_frame, width=30)
            start_date_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
            if start_date:
                start_date_entry.insert(0, start_date.strftime("%Y-%m-%d"))
            
            # End Date (Optional)
            tk.Label(form_frame, text="End Date (Optional):", bg="#f0f5e7", anchor="e").grid(row=4, column=0, sticky="e", padx=5, pady=5)
            end_date_entry = tk.Entry(form_frame, width=30)
            end_date_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)
            if end_date:
                end_date_entry.insert(0, end_date.strftime("%Y-%m-%d"))
            
            # Location
            tk.Label(form_frame, text="Research Location:", bg="#f0f5e7", anchor="e").grid(row=5, column=0, sticky="e", padx=5, pady=5)
            location_entry = tk.Entry(form_frame, width=30)
            location_entry.grid(row=5, column=1, sticky="w", padx=5, pady=5)
            if location:
                location_entry.insert(0, location)
            
            # Status
            tk.Label(form_frame, text="Status:", bg="#f0f5e7", anchor="e").grid(row=6, column=0, sticky="e", padx=5, pady=5)
            status_var = tk.StringVar(value=status if status else "Ongoing")
            status_combo = ttk.Combobox(form_frame, textvariable=status_var, 
                                      values=["Ongoing", "Completed", "Planned", "Cancelled"],
                                      width=28, state="readonly")
            status_combo.grid(row=6, column=1, sticky="w", padx=5, pady=5)
            
            # Findings
            tk.Label(form_frame, text="Research Findings:", bg="#f0f5e7", anchor="e").grid(row=7, column=0, sticky="ne", padx=5, pady=5)
            findings_text = tk.Text(form_frame, width=30, height=6)
            findings_text.grid(row=7, column=1, sticky="w", padx=5, pady=5)
            if findings:
                findings_text.insert("1.0", findings)
            
            # Save function - This is a nested function that uses variables from the outer scope
            def save_changes():
                # Store reference to self for use inside this function
                app_instance = self  # This is the key fix
                
                # Get values
                new_title = title_entry.get().strip()
                new_researcher = researcher_entry.get().strip()
                new_species = species_entry.get().strip()
                new_start_date = start_date_entry.get().strip()
                new_end_date = end_date_entry.get().strip() or None
                new_location = location_entry.get().strip()
                new_status = status_var.get()
                new_findings = findings_text.get("1.0", tk.END).strip()
                
                # Validate
                if not new_title or not new_researcher or not new_species or not new_start_date or not new_status:
                    messagebox.showwarning("Validation Error", "Title, researcher, species, start date and status are required.")
                    return
                
                # Validate dates
                try:
                    datetime.strptime(new_start_date, "%Y-%m-%d")
                    if new_end_date:
                        datetime.strptime(new_end_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning("Date Error", "Dates must be in YYYY-MM-DD format.")
                    return
                
                if not app_instance.check_db_connection():  # Use app_instance instead of self
                    return
                    
                try:
                    # Update database
                    app_instance.cursor.execute("""  # Use app_instance instead of self
                        UPDATE wildlife_research SET
                        title = %s, researcher = %s, species = %s, start_date = %s,
                        end_date = %s, location = %s, status = %s, findings = %s
                        WHERE id = %s
                    """, (new_title, new_researcher, new_species, new_start_date, 
                         new_end_date, new_location, new_status, new_findings, research_id))
                    
                    app_instance.conn.commit()  # Use app_instance instead of self
                    messagebox.showinfo("Success", "Research project updated successfully!")
                    edit_window.destroy()
                    app_instance.load_research_projects()  # Use app_instance instead of self
                    app_instance.load_statistics()  # Use app_instance instead of self
                    
                except mysql.connector.Error as err:
                    print(f"Error updating research: {err}")
                    print(traceback.format_exc())
                    messagebox.showerror("Database Error", f"Failed to update research: {err}")
            
            # Buttons
            btn_frame = tk.Frame(edit_window, bg="#f0f5e7")
            btn_frame.pack(pady=15)
            
            tk.Button(btn_frame, text="Save Changes", 
                     command=save_changes,  # This will now reference the properly scoped function
                     bg="#27ae60", fg="white", width=15).pack(side="left", padx=5)
                     
            tk.Button(btn_frame, text="Cancel", 
                     command=edit_window.destroy,
                     bg="#e74c3c", fg="white", width=15).pack(side="left", padx=5)
        
        except mysql.connector.Error as err:
            print(f"Error editing research: {err}")
            print(traceback.format_exc())
            messagebox.showerror("Database Error", f"Failed to retrieve research details: {err}")
    
    def delete_research(self):
        """Delete selected research"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a research project to delete.")
            return
        
        research_id = self.tree.item(selected[0])['values'][0]
        research_title = self.tree.item(selected[0])['values'][1]
        
        confirm = messagebox.askyesno("Confirm Delete", 
                                    f"Are you sure you want to delete the research project '{research_title}'?")
        if confirm:
            if not self.check_db_connection():
                return
                
            try:
                self.cursor.execute("DELETE FROM wildlife_research WHERE id = %s", (research_id,))
                self.conn.commit()
                self.load_research_projects()
                self.load_statistics()
                messagebox.showinfo("Success", "Research project deleted successfully!")
            except mysql.connector.Error as err:
                print(f"Error deleting research: {err}")
                print(traceback.format_exc())
                messagebox.showerror("Database Error", f"Failed to delete research: {err}")
    
    def add_sample_data(self, silent=False):
        """Add sample research data for testing"""
        if not self.check_db_connection():
            return
            
        try:
            # Sample data to insert
            sample_data = [
                ("Tiger Population in Sundarbans", "Dr. Anjali Singh", "Bengal Tiger", 
                 "2023-01-15", "2023-06-30", "Sundarbans, West Bengal", "Completed", 
                 "Found stable population of 85 tigers with 12 new cubs identified."),
                
                ("Elephant Migration Patterns", "Dr. Rajiv Kumar", "Asian Elephant", 
                 "2023-03-10", None, "Nilgiri Biosphere Reserve", "Ongoing", 
                 "Tracking 3 herds with GPS collars to identify seasonal migration routes."),
                 
                ("Gharial Conservation Study", "Dr. Meera Patel", "Gharial Crocodile", 
                 "2023-05-22", None, "Chambal River", "Ongoing", 
                 "Monitoring nesting sites and hatchling survival rates."),
                 
                ("Himalayan Snow Leopard Survey", "Dr. Anand Sharma", "Snow Leopard", 
                 "2022-11-05", "2023-04-15", "Hemis National Park", "Completed", 
                 "Camera traps identified 23 unique individuals across survey area."),
                 
                ("Bird Species Diversity", "Dr. Priya Iyer", "Multiple Bird Species", 
                 "2023-07-01", None, "Western Ghats", "Ongoing", 
                 "Cataloging over 150 species in the monsoon season.")
            ]
            
            # Insert sample data
            for data in sample_data:
                self.cursor.execute("""
                    INSERT INTO wildlife_research 
                    (title, researcher, species, start_date, end_date, location, status, findings, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (*data, self.username))
                
            self.conn.commit()
            print("Sample data added successfully")
            
            if not silent:
                messagebox.showinfo("Sample Data", "Sample research projects added successfully!")
                
            self.load_research_projects()
            self.load_statistics()
            
        except mysql.connector.Error as err:
            print(f"Sample data error: {str(err)}")
            print(traceback.format_exc())
            if not silent:
                messagebox.showerror("Database Error", f"Failed to add sample data: {err}")
    
    def back_to_dashboard(self):
        """Return to main dashboard"""
        try:
            # Close connection before destroying window
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
                
            self.root.destroy()
            dashboard = importlib.import_module("dashboard")
            dashboard.Dashboard(username=self.username).mainloop()
        except Exception as e:
            print(f"Error returning to dashboard: {e}")
            print(traceback.format_exc())
            messagebox.showerror("Error", f"Unable to return to dashboard: {str(e)}")


def run(username="Admin"):
    """Function to start the Wildlife Research module"""
    root = tk.Tk()
    app = WildlifeResearchApp(root, username)
    root.mainloop()


# Run only if executed directly
if __name__ == "__main__":
    run()
