import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
from datetime import datetime
import importlib
import os
import species_sanctuary  # Add this import at the top
import subprocess
from tkinter import filedialog


class Dashboard(tk.Tk):
    def __init__(self, username):
        super().__init__()

        self.title(f"WildGuard Dashboard - Welcome {username}")
        self.geometry("1200x700")
        self.configure(bg="#f0f0f0")

        self.username = username

        # Enhanced color scheme
        self.sidebar_color = "#1e3d59"  # Darker blue for sidebar
        self.content_color = "#f5f5f5"  # Light gray for content
        self.accent_color = "#28a745"   # Green for accent
        self.text_color = "#ffffff"     # White text
        self.hover_color = "#2b5278"    # Hover effect color
        self.card_bg = "#ffffff"        # Card background
        self.header_color = "#17a2b8"   # Header color

        # Store images
        self.images = {}
        
        # Store PDF paths for reports
        self.pdf_paths = {
            "report1": "",
            "report2": "",
            "report3": "",
            "report4": "",
            "report5": ""
        }
        
        # Try to load saved PDF paths if available
        self.load_pdf_paths()
        
        # Store button references for hover effects
        self.nav_buttons = []
        
        self.load_images()
        self.setup_ui()
        self.apply_styles()

    def apply_styles(self):
        """Apply custom styles to ttk widgets"""
        style = ttk.Style()
        
        # Table style
        style.configure("Treeview", 
                        background="#ffffff",
                        foreground="#333333",
                        rowheight=25,
                        fieldbackground="#ffffff",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', self.accent_color)])
        
        # Headings style
        style.configure("Treeview.Heading",
                        background=self.header_color,
                        foreground="white",
                        relief="flat",
                        font=('Helvetica', 10, 'bold'))
        
        # Button styles
        style.configure("TButton", 
                        background=self.accent_color,
                        foreground="white", 
                        font=('Helvetica', 10, 'bold'),
                        borderwidth=0,
                        padding=8)
        style.map('TButton',
                  background=[('active', self.hover_color),
                             ('pressed', self.hover_color)])

    def setup_ui(self):
        # Main layout frames
        self.sidebar = tk.Frame(self, bg=self.sidebar_color, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)  # Prevent shrinking
        
        # Create a canvas for scrollable sidebar
        self.sidebar_canvas = tk.Canvas(self.sidebar, bg=self.sidebar_color, highlightthickness=0)
        self.sidebar_canvas.pack(side="left", fill="both", expand=True)
        
        # Add scrollbar to sidebar
        sidebar_scrollbar = ttk.Scrollbar(self.sidebar, orient="vertical", command=self.sidebar_canvas.yview)
        sidebar_scrollbar.pack(side="right", fill="y")
        
        # Configure canvas
        self.sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        self.sidebar_canvas.bind('<Configure>', lambda e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all")))
        
        # Create frame inside canvas for sidebar content
        self.sidebar_frame = tk.Frame(self.sidebar_canvas, bg=self.sidebar_color)
        self.sidebar_canvas.create_window((0, 0), window=self.sidebar_frame, anchor="nw", width=200)
        
        # Main content area with right side
        self.right_side = tk.Frame(self, bg=self.content_color)
        self.right_side.pack(side="right", fill="both", expand=True)
        
        # Header
        self.header = tk.Frame(self.right_side, bg=self.header_color, height=70)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)  # Prevent shrinking
        
        # Header content
        header_left = tk.Frame(self.header, bg=self.header_color)
        header_left.pack(side="left", padx=20)
        
        dashboard_label = tk.Label(header_left, 
                                  text="🐾 WILDGUARD ADMIN PANEL", 
                                  font=("Montserrat", 18, "bold"), 
                                  bg=self.header_color, 
                                  fg="white")
        dashboard_label.pack(side="left", pady=18)
        
        # Search bar
        search_frame = tk.Frame(self.header, bg=self.header_color, padx=10, pady=15)
        search_frame.pack(side="right", padx=20)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, 
                               textvariable=self.search_var, 
                               font=("Helvetica", 10),
                               width=25,
                               bg="#f8f9fa",
                               bd=0,
                               highlightthickness=1,
                               highlightbackground="#dee2e6")
        search_entry.pack(side="left", padx=(0, 5))
        search_entry.insert(0, "Search...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, 'end') if search_entry.get() == "Search..." else None)
        search_entry.bind("<FocusOut>", lambda e: search_entry.insert(0, "Search...") if search_entry.get() == "" else None)
        
        search_button = tk.Button(search_frame, 
                                 text="🔍", 
                                 bg=self.accent_color, 
                                 fg="white",
                                 bd=0,
                                 padx=8,
                                 pady=2)
        search_button.pack(side="left")
        
        # Create a logo space in sidebar
        logo_frame = tk.Frame(self.sidebar_frame, bg=self.sidebar_color, height=100)
        logo_frame.pack(fill="x", pady=(20, 10))
        logo_frame.pack_propagate(False)
        
        if "logo" in self.images:
            logo_label = tk.Label(logo_frame, image=self.images["logo"], bg=self.sidebar_color)
            logo_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Divider
        divider = tk.Frame(self.sidebar_frame, height=1, bg="#3a546b")
        divider.pack(fill="x", padx=15, pady=10)

        # User info section
        user_frame = tk.Frame(self.sidebar_frame, bg=self.sidebar_color, pady=10)
        user_frame.pack(fill="x")
        
        user_icon = tk.Label(user_frame, text="👤", font=("Helvetica", 24), bg=self.sidebar_color, fg="white")
        user_icon.pack(pady=5)
        
        tk.Label(user_frame, 
                text=f"{self.username}", 
                font=("Helvetica", 12, "bold"), 
                bg=self.sidebar_color, 
                fg=self.text_color).pack()
        
        tk.Label(user_frame, 
                text=f"Admin", 
                font=("Helvetica", 9), 
                bg=self.sidebar_color, 
                fg="#8a9cb3").pack()
        
        tk.Label(user_frame, 
                text=f"📅 {datetime.now().strftime('%B %d, %Y')}", 
                font=("Helvetica", 9), 
                bg=self.sidebar_color, 
                fg="#8a9cb3").pack(pady=(5, 10))
        
        # Another divider
        divider2 = tk.Frame(self.sidebar_frame, height=1, bg="#3a546b")
        divider2.pack(fill="x", padx=15, pady=10)
        
        # Navigation section with headers
        nav_frame = tk.Frame(self.sidebar_frame, bg=self.sidebar_color)
        nav_frame.pack(fill="x")
        
        # Navigation sections with category headers
        self.add_nav_header("WILDLIFE MANAGEMENT")
        self.add_nav("🦁 Species", self.load_species, highlight=True)
        self.add_nav("🏞️ Sanctuaries", self.load_sanctuary, highlight=True)
        self.add_nav("⚠️ Endangered Species", lambda: self.open_module("endangered_species"))
        self.add_nav("🗺️ Map Locations", self.load_map_locations)
        self.add_nav("🛡️ Protected Areas", self.load_protected_areas)
        self.add_nav("🌳 Species Sanctuary", self.load_species_sanctuary)
        
        self.add_nav_header("CONSERVATION EFFORTS")
        self.add_nav("📋 Projects", self.load_projects, highlight=True)
        self.add_nav("👥 Volunteers", self.load_volunteers, highlight=True)
        self.add_nav("🤝 Volunteer Projects", self.load_volunteer_projects)
        self.add_nav("🚁 Wildlife Patrol", self.load_wildlife_patrol)
        self.add_nav("🚑 Rescue Operations", lambda: self.open_module("rescue_operations"))
        
        self.add_nav_header("INFORMATION & SUPPORT")
        self.add_nav("📰 Wildlife News", self.load_wildlife_news, highlight=True)
        self.add_nav("🔬 Wildlife Research", self.load_wildlife_research)
        self.add_nav("🏪 Wildlife Store", lambda: self.open_module("wildlife_store"))
        self.add_nav("🌍 Sustainable Tourism", self.load_sustainable_tourism)
        self.add_nav("💰 Donors", lambda: self.open_module("donors"))

        self.add_nav_header("REPORTS & DOCUMENTS")
        self.add_nav("📄 Report 1", lambda: self.open_pdf("report1"))
        self.add_nav("📄 Report 2", lambda: self.open_pdf("report2"))
        self.add_nav("📄 Report 3", lambda: self.open_pdf("report3"))
        self.add_nav("📄 Report 4", lambda: self.open_pdf("report4"))
        self.add_nav("📄 Report 5", lambda: self.open_pdf("report5"))
        self.add_nav("📊 Manage Reports", self.load_reports_page)
       

        # Main content area
        self.main_content = tk.Frame(self.right_side, bg=self.content_color)
        self.main_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add mouse wheel scrolling to sidebar
        self.sidebar_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.show_welcome()

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling in sidebar"""
        # Only scroll if mouse is over the sidebar
        x, y = self.sidebar.winfo_pointerxy()
        target = self.winfo_containing(x, y)
        if target and (str(target).startswith(str(self.sidebar)) or 
                      str(target).startswith(str(self.sidebar_canvas)) or 
                      str(target).startswith(str(self.sidebar_frame))):
            self.sidebar_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def add_nav_header(self, text):
        """Add a category header to the sidebar"""
        header_frame = tk.Frame(self.sidebar_frame, bg=self.sidebar_color, pady=5)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, 
                text=text, 
                font=("Helvetica", 9, "bold"), 
                bg=self.sidebar_color, 
                fg="#8a9cb3",
                anchor="w").pack(padx=15, fill="x")

    def add_nav(self, text, callback, category="default", highlight=False):
        """Add a navigation button to the sidebar with hover effect"""
        btn_bg = "#2b5278" if highlight else self.sidebar_color
        
        btn = tk.Button(self.sidebar_frame, 
                       text=text, 
                       font=("Helvetica", 10), 
                       bg=btn_bg, 
                       fg=self.text_color, 
                       bd=0,
                       activebackground=self.hover_color,
                       activeforeground=self.text_color,
                       anchor="w",
                       padx=15,
                       pady=8,
                       width=25,
                       cursor="hand2",
                       command=callback)
        
        btn.pack(fill="x", pady=1)
        
        # Store button reference for hover effects
        self.nav_buttons.append((btn, highlight))
        
        # Add hover events
        btn.bind("<Enter>", lambda event, b=btn: self.on_button_hover(b))
        btn.bind("<Leave>", lambda event, b=btn, h=highlight: self.on_button_leave(b, h))
        
        return btn

    def on_button_hover(self, button):
        """Change button appearance on hover"""
        button.config(bg=self.hover_color)

    def on_button_leave(self, button, highlight=False):
        """Reset button appearance when mouse leaves"""
        button.config(bg="#2b5278" if highlight else self.sidebar_color)

    def show_welcome(self):
        """Show welcome dashboard with statistics and quick access panels"""
        # Clear existing content
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Welcome header
        welcome_frame = tk.Frame(self.main_content, bg=self.content_color)
        welcome_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(welcome_frame, 
                text="Dashboard Overview", 
                font=("Helvetica", 20, "bold"), 
                bg=self.content_color, 
                fg="#333333").pack(anchor="w")
                
        tk.Label(welcome_frame, 
                text="Welcome to your WildGuard control panel", 
                font=("Helvetica", 12), 
                bg=self.content_color, 
                fg="#666666").pack(anchor="w", pady=(5, 0))
        
        # Statistics cards row
        stats_frame = tk.Frame(self.main_content, bg=self.content_color)
        stats_frame.pack(fill="x", pady=15)
        
        # Create 4 stat cards
        stat_data = [
            {"title": "Protected Species", "value": "246", "change": "+12%", "icon": "🦁"},
            {"title": "Active Sanctuaries", "value": "52", "change": "+3", "icon": "🏞️"},
            {"title": "Conservation Projects", "value": "78", "change": "+5", "icon": "📋"},
            {"title": "Active Volunteers", "value": "1,235", "change": "+21%", "icon": "👥"}
        ]
        
        for stat in stat_data:
            self.create_stat_card(stats_frame, stat)
        
        # Two-column layout for bottom section
        bottom_frame = tk.Frame(self.main_content, bg=self.content_color)
        bottom_frame.pack(fill="both", expand=True, pady=15)
        
        # Left column - Table
        left_col = tk.Frame(bottom_frame, bg=self.content_color)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Table header
        table_header = tk.Frame(left_col, bg=self.content_color)
        table_header.pack(fill="x", pady=(0, 10))
        
        tk.Label(table_header, 
                text="Recent Activities", 
                font=("Helvetica", 14, "bold"), 
                bg=self.content_color, 
                fg="#333333").pack(side="left")
        
        # Custom View All button with different color scheme
        view_all_btn = tk.Button(table_header,
                              text="View All",
                              font=("Helvetica", 10, "bold"),
                              bg="#ff7f50",  # Coral color - stands out from green accent
                              fg="white",
                              bd=0,
                              padx=12,
                              pady=6,
                              cursor="hand2")
        view_all_btn.pack(side="right")
        
        # Add hover effects to the View All button
        view_all_btn.bind("<Enter>", lambda event: view_all_btn.config(bg="#ff6347"))  # Tomato color on hover
        view_all_btn.bind("<Leave>", lambda event: view_all_btn.config(bg="#ff7f50"))  # Back to coral when mouse leaves
        
        # Create table
        self.create_activity_table(left_col)
        
        # Right column - Cards
        right_col = tk.Frame(bottom_frame, bg=self.content_color, width=300)
        right_col.pack(side="right", fill="both", padx=(10, 0))
        
        # Quick links card
        self.create_quick_access_card(right_col)
        
        # Wildlife spotlight card with image
        self.create_spotlight_card(right_col)
        
        # Reports Section
        reports_frame = tk.Frame(self.main_content, bg=self.content_color)
        reports_frame.pack(fill="x", pady=15)

        reports_header = tk.Frame(reports_frame, bg=self.content_color)
        reports_header.pack(fill="x", pady=(0, 10))

        tk.Label(reports_header, 
                text="📊 Reports & Documents", 
                font=("Helvetica", 16, "bold"), 
                bg=self.content_color, 
                fg="#333333").pack(side="left")

        # Reports buttons row
        reports_buttons = tk.Frame(reports_frame, bg=self.content_color)
        reports_buttons.pack(fill="x")

        # Create 5 report buttons
        for i in range(1, 6):
            report_frame = tk.Frame(reports_buttons, bg=self.card_bg, padx=15, pady=15, bd=0, 
                                  highlightthickness=1, highlightbackground="#e0e0e0")
            report_frame.pack(side="left", fill="x", expand=True, padx=5)
            
            # Icon and label
            icon_label = tk.Label(report_frame, text="📄", font=("Helvetica", 24), 
                                bg=self.card_bg, fg=self.accent_color)
            icon_label.pack(pady=(0, 5))
            
            tk.Label(report_frame, text=f"Report {i}", font=("Helvetica", 12, "bold"), 
                   bg=self.card_bg, fg="#333333").pack()
            
            # Check if we have a path for this report
            has_pdf = bool(self.pdf_paths[f"report{i}"])
            status_text = "PDF Linked" if has_pdf else "No PDF Set"
            status_color = self.accent_color if has_pdf else "#999999"
            
            status_label = tk.Label(report_frame, text=status_text, font=("Helvetica", 9), 
                                 bg=self.card_bg, fg=status_color)
            status_label.pack(pady=(0, 8))
            
            # Buttons
            btn_frame = tk.Frame(report_frame, bg=self.card_bg)
            btn_frame.pack(fill="x")
            
            # Open button
            open_btn = tk.Button(btn_frame, text="Open", font=("Helvetica", 9, "bold"),
                               bg=self.accent_color, fg="white", padx=10, pady=4, bd=0,
                               command=lambda idx=i: self.open_pdf(f"report{idx}"),
                               cursor="hand2")
            open_btn.pack(side="left", padx=(0, 5))
            
            # Change button
            change_btn = tk.Button(btn_frame, text="Change", font=("Helvetica", 9),
                                 bg="#f0f0f0", fg="#333333", padx=10, pady=4, bd=0,
                                 command=lambda idx=i: self.select_pdf(f"report{idx}"),
                                 cursor="hand2")
            change_btn.pack(side="left")
            
            # Add hover effects
            for btn in (open_btn, change_btn):
                btn_bg = btn.cget("bg")
                btn.bind("<Enter>", lambda e, b=btn, c=btn_bg: b.config(bg=self.hover_color if c == self.accent_color else "#e0e0e0"))
                btn.bind("<Leave>", lambda e, b=btn, c=btn_bg: b.config(bg=c))

    def create_stat_card(self, parent, data):
        """Create a statistics card"""
        card = tk.Frame(parent, bg=self.card_bg, padx=15, pady=15, bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
        card.pack(side="left", fill="x", expand=True, padx=5)
        
        header = tk.Frame(card, bg=self.card_bg)
        header.pack(fill="x")
        
        # Icon and title
        tk.Label(header, 
                text=data["icon"], 
                font=("Helvetica", 18), 
                bg=self.card_bg, 
                fg=self.accent_color).pack(side="left")
                
        tk.Label(header, 
                text=data["title"], 
                font=("Helvetica", 10), 
                bg=self.card_bg, 
                fg="#666666").pack(side="left", padx=(5, 0))
        
        # Value and change
        value_frame = tk.Frame(card, bg=self.card_bg, pady=10)
        value_frame.pack(fill="x")
        
        tk.Label(value_frame, 
                text=data["value"], 
                font=("Helvetica", 24, "bold"), 
                bg=self.card_bg, 
                fg="#333333").pack(anchor="w")
                
        change_label = tk.Label(card, 
                              text=data["change"], 
                              font=("Helvetica", 10), 
                              bg=self.card_bg, 
                              fg=self.accent_color)
        change_label.pack(anchor="w")

    def create_activity_table(self, parent):
        """Create a nice looking table for recent activities with bright colors for better visibility"""
        # Create frame for the table with better styling
        table_frame = tk.Frame(parent, bg="white", bd=0, highlightthickness=2, highlightbackground="#1e88e5")
        table_frame.pack(fill="both", expand=True)
        
        # Apply a custom style specifically for this table
        style = ttk.Style()
        
        # Configure the table style with brighter colors
        style.configure("BrightTree.Treeview", 
                        background="#ffffff",
                        foreground="#333333",
                        rowheight=30,
                        fieldbackground="#ffffff",
                        font=('Helvetica', 10),
                        borderwidth=0)
        
        # Configure the headings with a bright blue background                
        style.configure("BrightTree.Treeview.Heading",
                        background="#1e88e5",  # Bright blue header
                        foreground="green", 
                        relief="flat",
                        font=('Helvetica', 10, 'bold'),
                        padding=6)
                        
        # Change selection color
        style.map('BrightTree.Treeview', 
                  background=[('selected', '#2196f3')],
                  foreground=[('selected', 'white')])
        
        # Create Treeview with adjusted column configuration
        columns = ("timestamp", "activity", "user", "status")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", 
                           style="BrightTree.Treeview", height=8)
        
        # Define headings with better clarity and consistent anchoring
        tree.heading("timestamp", text="TIMESTAMP", anchor="center")
        tree.heading("activity", text="ACTIVITY", anchor="center")
        tree.heading("user", text="USER", anchor="center")
        tree.heading("status", text="STATUS", anchor="center")
        
        # Define column widths with more generous sizing
        tree.column("timestamp", width=150, minwidth=120, anchor="center")
        tree.column("activity", width=350, minwidth=250, anchor="w")
        tree.column("user", width=120, minwidth=100, anchor="center")
        tree.column("status", width=120, minwidth=100, anchor="center")
        
        # Sample data with more descriptive activities
        sample_data = [
            ("2025-04-25 09:15", "Added new species: Bengal Tiger (Panthera tigris)", "Admin", "Completed"),
            ("2025-04-25 08:30", "Updated Bandipur sanctuary information", "John", "Completed"),
            ("2025-04-24 17:45", "Created Save Rhinos conservation project", "Lisa", "Pending"),
            ("2025-04-24 15:20", "Registered new volunteer: Sarah Johnson", "Admin", "Completed"),
            ("2025-04-23 14:10", "Updated endangered species list - added 3 species", "Mark", "Completed"),
            ("2025-04-23 10:30", "Added new protected area in Western Ghats", "Admin", "Pending"),
            ("2025-04-22 16:45", "Created rescue operation report for injured elephants", "Sarah", "Completed"),
            ("2025-04-22 12:30", "Updated wildlife patrol schedule for summer", "Admin", "Completed")
        ]
        
        # Insert data
        for idx, item in enumerate(sample_data):
            tree.insert("", "end", values=item, tags=(f"row{idx % 2}",))
        
        # Set alternating row colors with brighter distinction
        tree.tag_configure("row0", background="#ffffff")
        tree.tag_configure("row1", background="#e3f2fd")  # Light blue for better visibility
        
        # Add status color coding with brighter colors
        for item in tree.get_children():
            status = tree.item(item)["values"][3]
            if status == "Completed":
                tree.item(item, tags=(tree.item(item)["tags"][0], "completed"))
            else:
                tree.item(item, tags=(tree.item(item)["tags"][0], "pending"))
        
        # Configure status colors - brighter and more visible        
        tree.tag_configure("completed", foreground="#00c853")  # Bright green
        tree.tag_configure("pending", foreground="#ff9100")    # Bright orange
        
        # Add horizontal and vertical scrollbars with custom styling
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        
        # Configure the scrollbars to have a more visible appearance
        style.configure("Vertical.TScrollbar", 
                       background="#1e88e5", 
                       troughcolor="#e3f2fd",
                       borderwidth=0,
                       arrowsize=13)
                       
        style.configure("Horizontal.TScrollbar", 
                       background="#1e88e5", 
                       troughcolor="#e3f2fd",
                       borderwidth=0,
                       arrowsize=13)
        
        # Configure tree to use both scrollbars
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack the scrollbars and tree with proper layout management
        tree.pack(side="top", fill="both", expand=True, padx=1, pady=1)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Add visual enhancements to the table frame
        enhancement_frame = tk.Frame(parent, bg=self.content_color, height=10)
        enhancement_frame.pack(fill="x", pady=(10, 0))
        
        # Add row count indicator
        count_label = tk.Label(enhancement_frame, 
                              text=f"Showing {len(sample_data)} records", 
                              font=("Helvetica", 9), 
                              bg=self.content_color,
                              fg="#666666")
        count_label.pack(side="left")
        
        # Add refresh button
        refresh_btn = tk.Button(enhancement_frame,
                              text="↻ Refresh",
                              font=("Helvetica", 9),
                              bg="#e3f2fd",
                              fg="#1e88e5",
                              bd=0,
                              padx=8,
                              pady=2,
                              cursor="hand2")
        refresh_btn.pack(side="right")
        
        # Add double click event to view details with visual feedback
        tree.bind("<Double-1>", lambda event: self.view_activity_details(tree))
        
        # Add single click highlight for better user feedback
        tree.bind("<ButtonRelease-1>", lambda event: count_label.config(
            text=f"Selected: {tree.item(tree.selection()[0])['values'][1]}" if tree.selection() else f"Showing {len(sample_data)} records"
        ))
        
        return tree

    def view_activity_details(self, tree):
        """Show details of selected activity in a popup window"""
        selection = tree.selection()
        if not selection:
            return
        
        item = tree.item(selection[0])
        values = item['values']
        
        # Create a small popup with activity details
        details_window = tk.Toplevel(self)
        details_window.title("Activity Details")
        details_window.geometry("500x300")
        details_window.configure(bg=self.card_bg)
        
        # Add some padding
        frame = tk.Frame(details_window, bg=self.card_bg, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        # Add details with more formatting
        tk.Label(frame, text="Activity Details", font=("Helvetica", 14, "bold"), 
                 bg=self.card_bg, fg="#333333").pack(anchor="w", pady=(0, 15))
        
        tk.Label(frame, text=f"Timestamp: {values[0]}", font=("Helvetica", 11),
                 bg=self.card_bg, fg="#333333").pack(anchor="w", pady=5)
                 
        tk.Label(frame, text=f"Activity: {values[1]}", font=("Helvetica", 11),
                 bg=self.card_bg, fg="#333333", wraplength=450, justify="left").pack(anchor="w", pady=5)
                 
        tk.Label(frame, text=f"User: {values[2]}", font=("Helvetica", 11),
                 bg=self.card_bg, fg="#333333").pack(anchor="w", pady=5)
                 
        status_frame = tk.Frame(frame, bg=self.card_bg)
        status_frame.pack(anchor="w", pady=5)
        
        status_color = "#28a745" if values[3] == "Completed" else "#ffc107"
        tk.Label(status_frame, text="Status: ", font=("Helvetica", 11),
                 bg=self.card_bg, fg="#333333").pack(side="left")
                 
        tk.Label(status_frame, text=f"{values[3]}", font=("Helvetica", 11, "bold"),
                 bg=self.card_bg, fg=status_color).pack(side="left")
        
        # Close button
        tk.Button(frame, text="Close", font=("Helvetica", 10),
                  bg=self.header_color, fg="white", padx=15, pady=5,
                  command=details_window.destroy).pack(pady=20)

    def create_quick_access_card(self, parent):
        """Create quick access links card"""
        card = tk.Frame(parent, bg=self.card_bg, padx=15, pady=15, bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
        card.pack(fill="x", expand=True, pady=(0, 10))
        
        # Header
        tk.Label(card, 
                text="Quick Access", 
                font=("Helvetica", 14, "bold"), 
                bg=self.card_bg, 
                fg="#333333").pack(anchor="w", pady=(0, 10))
        
        # Quick access buttons
        quick_links = [
            ("Add New Species", lambda: self.load_species()),
            ("Register Volunteer", lambda: self.load_volunteers()),
            ("Create Project", lambda: self.load_projects()),
            ("Add News Article", lambda: self.load_wildlife_news())
        ]
        
        for text, cmd in quick_links:
            link_btn = tk.Button(card, 
                               text=text,
                               bg=self.content_color,
                               fg="#333333",
                               bd=0,
                               padx=10,
                               pady=8,
                               anchor="w",
                               cursor="hand2",
                               command=cmd)
            link_btn.pack(fill="x", pady=2)
            
            # Hover effects
            link_btn.bind("<Enter>", lambda e, btn=link_btn: btn.config(bg="#e9ecef"))
            link_btn.bind("<Leave>", lambda e, btn=link_btn: btn.config(bg=self.content_color))

    def create_spotlight_card(self, parent):
        """Create a spotlight card with an image"""
        card = tk.Frame(parent, bg=self.card_bg, bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
        card.pack(fill="both", expand=True)
        
        # Header
        header = tk.Frame(card, bg=self.card_bg, padx=15, pady=15)
        header.pack(fill="x")
        
        tk.Label(header, 
                text="Wildlife Spotlight", 
                font=("Helvetica", 14, "bold"), 
                bg=self.card_bg, 
                fg="#333333").pack(anchor="w")
        
        # Image
        if "wildlife1" in self.images:
            img_label = tk.Label(card, image=self.images["wildlife1"], bg=self.card_bg)
            img_label.pack(fill="x")
            
        # Content
        content = tk.Frame(card, bg=self.card_bg, padx=15, pady=15)
        content.pack(fill="x")
        
        tk.Label(content, 
                text="Sumatran Tiger Conservation", 
                font=("Helvetica", 12, "bold"), 
                bg=self.card_bg, 
                fg="#333333").pack(anchor="w")
                
        tk.Label(content, 
                text="The foundation's latest effort to protect the\ncritically endangered Sumatran tiger.", 
                font=("Helvetica", 10), 
                bg=self.card_bg, 
                justify="left",
                fg="#666666").pack(anchor="w", pady=(5, 10))
                
        ttk.Button(content, 
                  text="Learn More", 
                  style="TButton").pack(anchor="w")

    def load_reports_page(self):
        """Show reports management page with scrolling support"""
        # Clear existing content
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Create a canvas with scrollbar for scrolling
        main_canvas = tk.Canvas(self.main_content, bg=self.content_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_content, orient="vertical", command=main_canvas.yview)
        
        # Configure the canvas
        main_canvas.configure(yscrollcommand=scrollbar.set)
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create a frame inside the canvas to hold content
        reports_frame = tk.Frame(main_canvas, bg=self.content_color)
        
        # Add the frame to the canvas
        canvas_frame = main_canvas.create_window((0, 0), window=reports_frame, anchor="nw")
        
        # Header
        header_frame = tk.Frame(reports_frame, bg=self.content_color)
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="Reports Management", 
               font=("Helvetica", 20, "bold"), 
               bg=self.content_color, fg="#333333").pack(anchor="w")
        
        tk.Label(header_frame, text="Manage and access your important documents and reports", 
               font=("Helvetica", 12), 
               bg=self.content_color, fg="#666666").pack(anchor="w", pady=(5, 0))
        
        # Create a frame for all reports
        reports_container = tk.Frame(reports_frame, bg=self.content_color)
        reports_container.pack(fill="both", expand=True)
        
        # Create 5 report cards
        for i in range(1, 6):
            report_key = f"report{i}"
            report_frame = tk.Frame(reports_container, bg=self.card_bg, padx=20, pady=20, bd=0, 
                                  highlightthickness=2, highlightbackground="#e0e0e0")
            report_frame.pack(fill="x", pady=10)
            
            # Report header
            header = tk.Frame(report_frame, bg=self.card_bg)
            header.pack(fill="x", pady=(0, 15))
            
            tk.Label(header, text=f"Report {i}", font=("Helvetica", 16, "bold"), 
                   bg=self.card_bg, fg="#333333").pack(side="left")
            
            # PDF path and status
            path_frame = tk.Frame(report_frame, bg=self.card_bg)
            path_frame.pack(fill="x", pady=(0, 15))
            
            tk.Label(path_frame, text="Current PDF: ", font=("Helvetica", 10, "bold"), 
                   bg=self.card_bg, fg="#555555").pack(side="left")
            
            path_var = tk.StringVar()
            path_var.set(self.pdf_paths[report_key] or "No PDF selected")
            
            path_label = tk.Label(path_frame, textvariable=path_var, font=("Helvetica", 10), 
                                bg=self.card_bg, fg="#666666", wraplength=500, anchor="w")
            path_label.pack(side="left", fill="x", expand=True)
            
            # Status indicator
            status = "✅ PDF Linked" if self.pdf_paths[report_key] else "❌ No PDF Selected"
            status_color = self.accent_color if self.pdf_paths[report_key] else "#e74c3c"
            
            tk.Label(path_frame, text=status, font=("Helvetica", 10, "bold"), 
                   bg=self.card_bg, fg=status_color).pack(side="right")
            
            # Last modified date if file exists
            if self.pdf_paths[report_key] and os.path.exists(self.pdf_paths[report_key]):
                mtime = os.path.getmtime(self.pdf_paths[report_key])
                mod_time = datetime.fromtimestamp(mtime).strftime("%B %d, %Y at %H:%M")
                
                mod_frame = tk.Frame(report_frame, bg=self.card_bg)
                mod_frame.pack(fill="x", pady=(0, 10))
                
                tk.Label(mod_frame, text="Last Modified: ", font=("Helvetica", 9), 
                       bg=self.card_bg, fg="#555555").pack(side="left")
                       
                tk.Label(mod_frame, text=mod_time, font=("Helvetica", 9), 
                       bg=self.card_bg, fg="#666666").pack(side="left")
            
            # Button frame
            button_frame = tk.Frame(report_frame, bg=self.card_bg)
            button_frame.pack(pady=10)
            
            # Function to update UI after changing PDF
            def update_ui(idx, path_var):
                path_var.set(self.pdf_paths[f"report{idx}"] or "No PDF selected")
                self.load_reports_page()  # Refresh the page
            
            # Select PDF button
            select_btn = tk.Button(button_frame, text="Select PDF", font=("Helvetica", 10, "bold"),
                                 bg=self.accent_color, fg="white", padx=15, pady=8, bd=0,
                                 command=lambda idx=i, pv=path_var: [
                                     self.select_pdf(f"report{idx}"), 
                                     update_ui(idx, pv)
                                 ],
                                 cursor="hand2")
            select_btn.pack(side="left", padx=5)
            
            # Open PDF button
            open_btn = tk.Button(button_frame, text="Open PDF", font=("Helvetica", 10, "bold"),
                               bg=self.header_color, fg="white", padx=15, pady=8, bd=0,
                               command=lambda idx=i: self.open_pdf(f"report{idx}"),
                               cursor="hand2",
                               state="normal" if self.pdf_paths[report_key] else "disabled")
            open_btn.pack(side="left", padx=5)
            
            # Clear PDF button
            clear_btn = tk.Button(button_frame, text="Clear", font=("Helvetica", 10),
                                bg="#f8f9fa", fg="#666666", padx=15, pady=8, bd=0,
                                command=lambda idx=i, pv=path_var: [
                                    self.pdf_paths.__setitem__(f"report{idx}", ""),
                                    self.save_pdf_paths(),
                                    update_ui(idx, pv)
                                ],
                                cursor="hand2",
                                state="normal" if self.pdf_paths[report_key] else "disabled")
            clear_btn.pack(side="left", padx=5)
            
            # Add hover effects
            for btn in (select_btn, open_btn, clear_btn):
                if btn["state"] != "disabled":
                    orig_bg = btn.cget("bg")
                    hover_bg = self.hover_color if orig_bg in (self.accent_color, self.header_color) else "#e9ecef"
                    btn.bind("<Enter>", lambda e, b=btn, h=hover_bg: b.config(bg=h))
                    btn.bind("<Leave>", lambda e, b=btn, o=orig_bg: b.config(bg=o))

        # Back button at bottom
        back_btn = tk.Button(reports_frame, text="← Back to Dashboard", font=("Helvetica", 10),
                           bg="#f8f9fa", fg="#333333", padx=15, pady=8, bd=0,
                           command=self.show_welcome,
                           cursor="hand2")
        back_btn.pack(anchor="w", pady=20)
        
        # Update scrollregion when frames change size
        reports_frame.update_idletasks()
        main_canvas.config(scrollregion=main_canvas.bbox("all"))
        main_canvas.itemconfig(canvas_frame, width=main_canvas.winfo_width())
        
        # Make sure the canvas resizes with the window
        def on_canvas_configure(event):
            main_canvas.itemconfig(canvas_frame, width=event.width)
        
        main_canvas.bind("<Configure>", on_canvas_configure)
        
        # Add mouse wheel scrolling
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Unbind mousewheel when mouse leaves the reports page
        def _unbind_mousewheel(e):
            main_canvas.unbind_all("<MouseWheel>")
        
        def _rebind_mousewheel(e):
            main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        main_canvas.bind("<Leave>", _unbind_mousewheel)
        main_canvas.bind("<Enter>", _rebind_mousewheel)

    # Other methods remain the same
    def load_species(self):
        """Load the species module"""
        self.open_module("species")
        
    def load_sanctuary(self):
        """Load the sanctuary module"""
        import sanctuary
        self.destroy()
        sanctuary.run(username=self.username)  # Pass username to maintain consistency
        
    def load_projects(self):
        """Load the projects module"""
        try:
            # Import projects only when needed
            try:
                import projects
            except ModuleNotFoundError:
                messagebox.showerror("Error", "Projects module not found. Please make sure 'projects.py' exists in the same directory.")
                return
            self.destroy()
            projects.run(username=self.username)
        except ModuleNotFoundError:
            messagebox.showerror("Error", "Projects module not found. Please make sure 'projects.py' exists in the same directory.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load projects: {str(e)}")
            
    def load_volunteers(self):
        """Load the volunteers module"""
        try:
            self.destroy()
            import volunteers
            volunteers.run(username=self.username)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load volunteers: {str(e)}")
            
    def load_volunteer_projects(self):
        """Load the volunteer projects module"""
        try:
            self.destroy()
            import volunteer_projects
            volunteer_projects.VolunteerProjects(username=self.username)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load volunteer projects: {str(e)}")
            
    def load_species_sanctuary(self):
        """Load the species sanctuary module"""
        try:
            self.destroy()
            species_sanctuary.SpeciesSanctuary(username=self.username)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load species sanctuary: {str(e)}")

    def load_map_locations(self):
        """Load the map locations module"""
        try:
            self.destroy()
            import maplocation  # Import the module file
            maplocation.MapLocation(username=self.username)
        except ModuleNotFoundError:
            # Try alternative module name if first attempt fails
            try:
                import maplocation
                self.destroy()
                maplocation.MapLocation(username=self.username)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load map locations: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load map locations: {str(e)}")

    def load_protected_areas(self):
        """Load the protected areas module"""
        try:
            self.destroy()
            import Protected_Areas  # Note the capital letters and underscore
            Protected_Areas.run(username=self.username)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load protected areas: {str(e)}")

    def load_wildlife_news(self):
        """Load the wildlife news module"""
        try:
            self.destroy()
            import wildlife_news
            wildlife_news.run(username=self.username)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load wildlife news: {str(e)}")

    def load_wildlife_research(self):
        """Load the wildlife research module"""
        try:
            self.destroy()
            import wildlife_research
            wildlife_research.run(username=self.username)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load wildlife research: {str(e)}")

    def load_wildlife_patrol(self):
        """Load the wildlife patrol module"""
        try:
            self.destroy()
            import wildlife_patrol
            wildlife_patrol.WildlifePatrol(username=self.username)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load wildlife patrol: {str(e)}")

    def load_rescue_operations(self):
        """Load the rescue operations module"""
        try:
            self.destroy()
            import rescue_operations
            rescue_operations.RescueOperations(username=self.username)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load rescue operations: {str(e)}")

    def load_sustainable_tourism(self):
        """Load the sustainable tourism module"""
        try:
            self.destroy()
            import sustainable_tourism
            sustainable_tourism.SustainableTourism(username=self.username)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sustainable tourism: {str(e)}")

    def open_module(self, module_name):
        """Open a module and destroy the current window"""
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Check what interface the module provides
            if hasattr(module, 'run'):
                # Module has a run function
                self.destroy()  # Close dashboard and open new module
                module.run(username=self.username)
            else:
                # Try class approach based on module name
                class_name = ''.join(word.capitalize() for word in module_name.split('_'))
                if hasattr(module, class_name):
                    # Get the class constructor and call it
                    constructor = getattr(module, class_name)
                    self.destroy()
                    constructor(username=self.username)
                else:
                    # Try with the same name as the module
                    module_class_name = module_name.capitalize()
                    if hasattr(module, module_class_name):
                        constructor = getattr(module, module_class_name)
                        self.destroy()
                        constructor(username=self.username)
                    else:
                        raise AttributeError(f"Could not find run function or appropriate class in {module_name}")
                
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Unable to open {module_name}: {str(e)}")
            print(f"Error opening module {module_name}: {str(e)}")

    def load_images(self):
        """Load images for use in the dashboard"""
        # Use the absolute path for the logo
        logo_path = r"C:\Users\aayus\OneDrive\Desktop\dbms1\logo.jpeg"
        
        # Other image paths (relative)
        image_paths = {
            "logo": logo_path,  # Use absolute path for logo
            
        }
        
        for key, path in image_paths.items():
            try:
                img = Image.open(path)
                # Resize appropriately based on the image type
                if key == "logo":
                    img = img.resize((120, 80), Image.LANCZOS)  # CHANGED: Height increased from 60 to 80
                else:
                    img = img.resize((300, 180), Image.LANCZOS)
                self.images[key] = ImageTk.PhotoImage(img)
                print(f"Successfully loaded image: {path}")
            except Exception as e:
                print(f"Could not load image {path}: {e}")
                # Create a placeholder image
                if key == "logo":
                    self.images[key] = self.create_placeholder_image(120, 80)  # CHANGED: Height increased from 60 to 80
                else:
                    self.images[key] = self.create_placeholder_image(300, 180)

    def create_placeholder_image(self, width, height):
        """Create a placeholder image when actual image can't be loaded"""
        # Create a blank image with PIL instead of using Canvas
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a blank image with the accent color
        image = Image.new('RGB', (width, height), self.accent_color)
        draw = ImageDraw.Draw(image)
        
        # Add text to the image
        text = "WildGuard"
        # Try to use a font, fall back to default if not available
        try:
            # Try to get a nice font if available
            font = ImageFont.truetype("arial.ttf", 14)  # Most Windows systems have this
        except IOError:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Get text dimensions to center it
        text_width = draw.textlength(text, font=font)
        text_position = ((width - text_width) / 2, (height - 14) / 2)
        
        # Draw text in white
        draw.text(text_position, text, fill="white", font=font)
        
        return ImageTk.PhotoImage(image)

    def load_pdf_paths(self):
        """Load saved PDF paths if available"""
        try:
            # Check if paths file exists
            path_file = os.path.join(os.path.dirname(__file__), "report_paths.txt")
            if os.path.exists(path_file):
                with open(path_file, "r") as f:
                    for line in f:
                        if ":" in line:
                            key, path = line.strip().split(":", 1)
                            if key in self.pdf_paths and os.path.exists(path):
                                self.pdf_paths[key] = path
        except Exception as e:
            print(f"Error loading PDF paths: {str(e)}")

    def save_pdf_paths(self):
        """Save PDF paths for future use"""
        try:
            path_file = os.path.join(os.path.dirname(__file__), "report_paths.txt")
            with open(path_file, "w") as f:
                for key, path in self.pdf_paths.items():
                    f.write(f"{key}:{path}\n")
        except Exception as e:
            print(f"Error saving PDF paths: {str(e)}")

    def open_pdf(self, report_key):
        """Open a PDF file with the system's default PDF viewer"""
        pdf_path = self.pdf_paths.get(report_key, "")
        
        if not pdf_path:
            # No path set, ask user to select a PDF
            self.select_pdf(report_key)
            return
            
        if not os.path.exists(pdf_path):
            messagebox.showerror("File Not Found", 
                               f"The PDF file for {report_key.replace('report', 'Report ')} could not be found.\n\nPlease select a valid PDF file.")
            self.select_pdf(report_key)
            return
            
        try:
            # Open the PDF with the default system application
            if os.name == 'nt':  # For Windows
                os.startfile(pdf_path)
            elif os.name == 'posix':  # For macOS and Linux
                subprocess.call(('xdg-open' if os.uname().sysname == 'Linux' else 'open', pdf_path))
        except Exception as e:
            messagebox.showerror("Error", f"Could not open the PDF: {str(e)}")

    def select_pdf(self, report_key):
        """Allow user to select a PDF file for a report"""
        pdf_path = filedialog.askopenfilename(
            title=f"Select PDF for {report_key.replace('report', 'Report ')}",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if pdf_path:
            self.pdf_paths[report_key] = pdf_path
            self.save_pdf_paths()
            
            # Ask if user wants to open the PDF now
            if messagebox.askyesno("Open PDF", "Would you like to open the selected PDF now?"):
                self.open_pdf(report_key)


# Only runs if executed directly, not when imported
if __name__ == "__main__":
    Dashboard(username="Admin").mainloop()
