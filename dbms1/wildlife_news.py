import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import importlib
from datetime import datetime

class WildlifeNewsApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title("Wildlife News Manager")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f5e7")
        
        # Database connection
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="11223344",
                database="WildGuardDB"
            )
            self.cursor = self.conn.cursor()
            
            # First check if the table exists
            self.cursor.execute("SHOW TABLES LIKE 'wildlife_news'")
            table_exists = self.cursor.fetchone() is not None
            
            if not table_exists:
                # Create news table with correct structure
                self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS wildlife_news (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    news_date DATE NOT NULL,
                    location VARCHAR(100),
                    content TEXT,
                    created_by VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                self.conn.commit()
            else:
                # Check if news_date column exists
                self.cursor.execute("SHOW COLUMNS FROM wildlife_news LIKE 'news_date'")
                if not self.cursor.fetchone():
                    # Add news_date column if missing
                    try:
                        self.cursor.execute("ALTER TABLE wildlife_news ADD COLUMN news_date DATE")
                        self.conn.commit()
                    except mysql.connector.Error:
                        pass  # Column might have been added by another process
        
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
            return
            
        # Header with back button
        header_frame = tk.Frame(root, bg="#1e8449", height=60)
        header_frame.pack(fill="x")
        
        back_btn = tk.Button(header_frame, text="← Back to Dashboard", 
                           command=self.back_to_dashboard,
                           bg="#1e8449", fg="white", bd=0)
        back_btn.pack(side="left", padx=10, pady=10)
        
        tk.Label(header_frame, text="📰 Wildlife News Management", 
               font=("Helvetica", 16, "bold"), 
               bg="#1e8449", fg="white").pack(pady=10)
               
        # Main content frame
        content_frame = tk.Frame(root, bg="#f0f5e7")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Split into left and right panels
        left_panel = tk.LabelFrame(content_frame, text="Add News Article", bg="#f0f5e7", font=("Arial", 12))
        left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        right_panel = tk.LabelFrame(content_frame, text="News Articles", bg="#f0f5e7", font=("Arial", 12))
        right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Input Fields in left panel
        self.title_entry = self.create_labeled_entry(left_panel, "Title", 0)
        self.date_entry = self.create_labeled_entry(left_panel, "Date (YYYY-MM-DD)", 1)
        self.location_entry = self.create_labeled_entry(left_panel, "Location", 2)
        
        # Add Text widget for content
        tk.Label(left_panel, text="Content:", bg="#f0f5e7").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.content_entry = tk.Text(left_panel, width=40, height=10)
        self.content_entry.grid(row=3, column=1, padx=5, pady=5)

        # Buttons
        btn_frame = tk.Frame(left_panel, bg="#f0f5e7")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text="Add News Article", bg="#1e8449", fg="white",
                 command=self.add_article, width=15).pack(side="left", padx=5)
                 
        tk.Button(btn_frame, text="Clear Fields", bg="#e74c3c", fg="white",
                 command=self.clear_fields, width=15).pack(side="left", padx=5)

        # News Articles Table in right panel
        # Create Treeview
        columns = ('id', 'title', 'date', 'location')
        self.tree = ttk.Treeview(right_panel, columns=columns, show='headings')
        
        # Define headings
        self.tree.heading('id', text='ID')
        self.tree.heading('title', text='Title')
        self.tree.heading('date', text='Date')
        self.tree.heading('location', text='Location')
        
        # Define column widths
        self.tree.column('id', width=40)
        self.tree.column('title', width=200)
        self.tree.column('date', width=100)
        self.tree.column('location', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tree buttons
        tree_btn_frame = tk.Frame(right_panel, bg="#f0f5e7")
        tree_btn_frame.pack(pady=10)
        
        tk.Button(tree_btn_frame, text="View Article", bg="#3498db", fg="white",
                 command=self.view_article, width=12).pack(side="left", padx=5)
                 
        tk.Button(tree_btn_frame, text="Delete Article", bg="#e74c3c", fg="white",
                 command=self.delete_article, width=12).pack(side="left", padx=5)
                 
        tk.Button(tree_btn_frame, text="Refresh", bg="#27ae60", fg="white",
                 command=self.load_articles, width=12).pack(side="left", padx=5)

        # Add right-click menu
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="View Article", command=self.view_article)
        self.context_menu.add_command(label="Delete Article", command=self.delete_article)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda event: self.view_article())
        
        # Load initial data
        self.load_articles()

    def create_labeled_entry(self, parent, label, row):
        tk.Label(parent, text=label + ":", bg="#f0f5e7").grid(row=row, column=0, padx=5, pady=5, sticky='e')
        entry = tk.Entry(parent, width=40)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky='w')
        return entry

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def load_articles(self):
        """Load articles from database"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            # First check if all required columns exist
            self.cursor.execute("DESCRIBE wildlife_news")
            columns = {row[0].lower(): True for row in self.cursor.fetchall()}
            
            # Check for required columns
            required_columns = ['id', 'title', 'news_date', 'location']
            missing_columns = [col for col in required_columns if col not in columns]
            
            # Add any missing columns
            for col in missing_columns:
                if col == 'news_date':
                    self.cursor.execute("ALTER TABLE wildlife_news ADD COLUMN news_date DATE")
                elif col == 'location':
                    self.cursor.execute("ALTER TABLE wildlife_news ADD COLUMN location VARCHAR(100)")
                elif col == 'title' and 'title' not in columns:
                    self.cursor.execute("ALTER TABLE wildlife_news ADD COLUMN title VARCHAR(200) NOT NULL DEFAULT 'Untitled'")
            
            self.conn.commit()
            
            # Now try loading with safe column selection
            try:
                self.cursor.execute("SELECT id, title, news_date, location FROM wildlife_news ORDER BY news_date DESC")
            except mysql.connector.Error:
                # Fallback query with only existing columns
                select_cols = []
                for col in ['id', 'title', 'news_date', 'location']:
                    if col in columns:
                        select_cols.append(col)
                    else:
                        # Use NULL for missing columns
                        select_cols.append(f"NULL as {col}")
                
                query = f"SELECT {', '.join(select_cols)} FROM wildlife_news"
                if 'news_date' in columns:
                    query += " ORDER BY news_date DESC"
                    
                self.cursor.execute(query)
                
            articles = self.cursor.fetchall()
            
            for article in articles:
                # Format data before display
                formatted_row = []
                for value in article:
                    if value is None:
                        formatted_row.append("")
                    else:
                        formatted_row.append(value)
                self.tree.insert('', 'end', values=formatted_row)
                
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to load articles: {err}")
            print(f"Database error: {err}")  # Debug output

    def add_article(self):
        """Add a new article to the database"""
        title = self.title_entry.get().strip()
        date_str = self.date_entry.get().strip()
        location = self.location_entry.get().strip()
        content = self.content_entry.get("1.0", tk.END).strip()

        # Validate
        if not title or not date_str:
            messagebox.showwarning("Warning", "Title and date are required.")
            return
            
        # Validate date format
        try:
            # Try to parse the date
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Warning", "Date must be in YYYY-MM-DD format.")
            return

        try:
            # Check if all required columns exist
            self.cursor.execute("DESCRIBE wildlife_news")
            columns = {row[0].lower(): True for row in self.cursor.fetchall()}
            
            # Build dynamic insert query based on available columns
            col_names = []
            col_values = []
            placeholders = []
            
            # Always include title and news_date
            if 'title' in columns:
                col_names.append('title')
                col_values.append(title)
                placeholders.append('%s')
                
            if 'news_date' in columns:
                col_names.append('news_date')
                col_values.append(date_str)
                placeholders.append('%s')
            
            # Optional columns
            if 'location' in columns and location:
                col_names.append('location')
                col_values.append(location)
                placeholders.append('%s')
                
            if 'content' in columns and content:
                col_names.append('content')
                col_values.append(content)
                placeholders.append('%s')
                
            if 'created_by' in columns:
                col_names.append('created_by')
                col_values.append(self.username)
                placeholders.append('%s')
                
            # Build and execute query
            query = f"INSERT INTO wildlife_news ({', '.join(col_names)}) VALUES ({', '.join(placeholders)})"
            self.cursor.execute(query, col_values)
            self.conn.commit()
            
            messagebox.showinfo("Success", f"Article '{title}' added successfully!")
            self.clear_fields()
            self.load_articles()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add article: {err}")
            print(f"Database error: {err}")  # Debug output

    def view_article(self):
        """View selected article"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an article to view.")
            return
            
        article_id = self.tree.item(selected[0])['values'][0]
        
        try:
            # Check which columns exist
            self.cursor.execute("DESCRIBE wildlife_news")
            columns = {row[0].lower(): True for row in self.cursor.fetchall()}
            
            # Build query with only existing columns
            select_cols = []
            for col in ['title', 'news_date', 'location', 'content']:
                if col in columns:
                    select_cols.append(col)
                else:
                    # Use empty string for missing columns
                    select_cols.append(f"'' as {col}")
                    
            query = f"SELECT {', '.join(select_cols)} FROM wildlife_news WHERE id = %s"
            self.cursor.execute(query, (article_id,))
            article = self.cursor.fetchone()
            
            if not article:
                messagebox.showwarning("Warning", "Article not found.")
                return
                
            # Extract values (may be less than 4 if some columns don't exist)
            title = article[0] if len(article) > 0 else "Untitled"
            date = article[1] if len(article) > 1 else "Unknown Date"
            location = article[2] if len(article) > 2 else "Unknown Location"
            content = article[3] if len(article) > 3 else "No content available"
            
            # Rest of method is unchanged
            # Create view window
            view_window = tk.Toplevel(self.root)
            view_window.title(f"Article: {title}")
            view_window.geometry("600x500")
            view_window.configure(bg="#f0f5e7")
            
            # Article details
            tk.Label(view_window, text=title, font=("Helvetica", 16, "bold"), bg="#f0f5e7").pack(pady=(20,5))
            tk.Label(view_window, text=f"Date: {date} | Location: {location}", bg="#f0f5e7").pack(pady=(0,15))
            
            # Content in scrollable text widget
            content_frame = tk.Frame(view_window, bg="#f0f5e7")
            content_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            text_widget = tk.Text(content_frame, wrap="word", bg="white", height=15)
            scrollbar = ttk.Scrollbar(content_frame, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side="right", fill="y")
            text_widget.pack(side="left", fill="both", expand=True)
            
            text_widget.insert("1.0", content)
            text_widget.config(state="disabled")  # Make read-only
            
            # Close button
            tk.Button(view_window, text="Close", command=view_window.destroy,
                     bg="#3498db", fg="white", width=15).pack(pady=15)
                
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve article: {err}")

    def delete_article(self):
        """Delete the selected article"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an article to delete.")
            return
            
        article_id = self.tree.item(selected[0])['values'][0]
        article_title = self.tree.item(selected[0])['values'][1]
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the article: {article_title}?")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM wildlife_news WHERE id = %s", (article_id,))
                self.conn.commit()
                self.load_articles()
                messagebox.showinfo("Success", "Article deleted successfully!")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to delete article: {err}")

    def clear_fields(self):
        """Clear form fields"""
        self.title_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        self.content_entry.delete("1.0", tk.END)
        
        # Default to today's date
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)
    
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
            messagebox.showerror("Error", f"Unable to return to dashboard: {str(e)}")


def run(username="Admin"):
    """Function to start the Wildlife News module"""
    root = tk.Tk()
    app = WildlifeNewsApp(root, username)
    root.mainloop()


# Run only if executed directly
if __name__ == "__main__":
    run()
