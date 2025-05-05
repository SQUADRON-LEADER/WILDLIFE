import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import importlib
from datetime import datetime

class WildlifeStoreApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title("Wildlife Store Inventory")
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
            
            # Create table if not exists
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS wildlife_store (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                quantity INT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            self.conn.commit()
            
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
        
        tk.Label(header_frame, text="🛒 Wildlife Store Inventory", 
               font=("Helvetica", 16, "bold"), 
               bg="#1e8449", fg="white").pack(pady=10)
        
        # Main content
        content_frame = tk.Frame(root, bg="#f0f5e7")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left frame for input forms
        input_frame = tk.LabelFrame(content_frame, text="Add New Product", bg="#f0f5e7", font=("Arial", 12))
        input_frame.pack(side="left", padx=10, pady=10, fill="y")
        
        # Input fields
        fields = ["Product Name", "Category", "Price (₹)", "Quantity", "Description"]
        self.entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(input_frame, text=field + ":", bg="#f0f5e7").grid(row=i, column=0, padx=10, pady=10, sticky="w")
            
            if field == "Description":
                entry = tk.Text(input_frame, width=30, height=4)
                entry.grid(row=i, column=1, padx=10, pady=10)
            else:
                entry = tk.Entry(input_frame, width=30)
                entry.grid(row=i, column=1, padx=10, pady=10)
                
            self.entries[field.lower().replace(" ", "_").replace("(₹)", "")] = entry
        
        # Button Frame
        btn_frame = tk.Frame(input_frame, bg="#f0f5e7")
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)
        
        tk.Button(btn_frame, text="Add Product", bg="#1e8449", fg="white", 
                 command=self.add_product, width=12).pack(side="left", padx=5)
                 
        tk.Button(btn_frame, text="Clear Fields", bg="#e74c3c", fg="white", 
                 command=self.clear_fields, width=12).pack(side="left", padx=5)

        # Add the delete button
        tk.Button(btn_frame, text="Delete Selected", bg="#d35400", fg="white", 
                 command=self.delete_product, width=12).pack(side="left", padx=5)
        
        # Right frame for display table
        table_frame = tk.LabelFrame(content_frame, text="Product Inventory", bg="#f0f5e7", font=("Arial", 12))
        table_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)
        
        # Table
        columns = ('id', 'name', 'category', 'price', 'quantity', 'description')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Define headings
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Product Name')
        self.tree.heading('category', text='Category')
        self.tree.heading('price', text='Price (₹)')
        self.tree.heading('quantity', text='Quantity')
        self.tree.heading('description', text='Description')
        
        # Define column widths
        self.tree.column('id', width=40)
        self.tree.column('name', width=150)
        self.tree.column('category', width=100)
        self.tree.column('price', width=80)
        self.tree.column('quantity', width=70)
        self.tree.column('description', width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Add right-click menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Delete Product", command=self.delete_product)
        self.context_menu.add_command(label="Edit Product", command=self.edit_product)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Load initial data
        self.load_products()

        # Also add a second set of buttons below the tree view for convenience
        tree_btn_frame = tk.Frame(table_frame, bg="#f0f5e7")
        tree_btn_frame.pack(pady=10)

        tk.Button(tree_btn_frame, text="Delete Selected", bg="#d35400", fg="white", 
                 command=self.delete_product, width=15).pack(side="left", padx=5)

        tk.Button(tree_btn_frame, text="Edit Selected", bg="#2980b9", fg="white", 
                 command=self.edit_product, width=15).pack(side="left", padx=5)

        tk.Button(tree_btn_frame, text="Refresh", bg="#27ae60", fg="white", 
                 command=self.load_products, width=15).pack(side="left", padx=5)

    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def load_products(self):
        """Load products from database"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            try:
                # Get table structure to determine actual column names
                self.cursor.execute("DESCRIBE wildlife_store")
                columns = [row[0] for row in self.cursor.fetchall()]
                
                # Construct query based on actual column names
                name_col = "product_name" if "product_name" in columns else "name"
                cat_col = "product_category" if "product_category" in columns else "category"
                
                query = f"SELECT id, {name_col} AS name, {cat_col} AS category, price, quantity, description FROM wildlife_store ORDER BY id"
                self.cursor.execute(query)
                
            except mysql.connector.Error:
                # Fallback query
                self.cursor.execute("SELECT * FROM wildlife_store ORDER BY id")
                
            products = self.cursor.fetchall()
            
            for product in products:
                # Make sure we have at least 6 values for the treeview
                values = list(product)
                while len(values) < 6:
                    values.append("")
                self.tree.insert('', 'end', values=values[:6])
                
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to load products: {err}")
            print(f"Database error in load_products: {err}")  # Debug output
    
    def add_product(self):
        """Add a new product to the database"""
        try:
            # Get values from form
            name = self.entries["product_name"].get()
            category = self.entries["category"].get()
            price_str = self.entries["price"].get()
            quantity_str = self.entries["quantity"].get()
            # For text widget, we need to get from 1.0 to end
            description = self.entries["description"].get("1.0", tk.END).strip()
            
            # Validate
            if not name or not category or not price_str or not quantity_str:
                messagebox.showwarning("Warning", "Please fill in all required fields.")
                return
                
            try:
                price = float(price_str)
                quantity = int(quantity_str)
                
                if price < 0:
                    messagebox.showwarning("Warning", "Price cannot be negative.")
                    return
                if quantity < 0:
                    messagebox.showwarning("Warning", "Quantity cannot be negative.")
                    return
                    
            except ValueError:
                messagebox.showerror("Error", "Price must be a number and quantity must be an integer.")
                return
                
            # Insert into database - handle different column name possibilities
            try:
                # First check the actual column names in the table
                self.cursor.execute("DESCRIBE wildlife_store")
                columns = [row[0] for row in self.cursor.fetchall()]
                
                # Determine correct column names
                name_col = "product_name" if "product_name" in columns else "name"
                cat_col = "product_category" if "product_category" in columns else "category"
                
                # Construct the query dynamically
                query = f"INSERT INTO wildlife_store ({name_col}, {cat_col}, price, quantity, description) VALUES (%s, %s, %s, %s, %s)"
                self.cursor.execute(query, (name, category, price, quantity, description))
                
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to add product: {err}")
                print(f"Insert error: {err}")  # Debug output
                return
            
            self.conn.commit()
            
            messagebox.showinfo("Success", f"{name} added to the store!")
            self.clear_fields()
            self.load_products()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add product: {err}")
    
    def delete_product(self):
        """Delete selected product"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to delete.")
            return
            
        product_id = self.tree.item(selected[0])['values'][0]
        product_name = self.tree.item(selected[0])['values'][1]
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {product_name}?")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM wildlife_store WHERE id = %s", (product_id,))
                self.conn.commit()
                self.load_products()
                messagebox.showinfo("Deleted", f"{product_name} has been removed from the inventory.")
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Failed to delete product: {err}")
    
    def edit_product(self):
        """Edit selected product"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to edit.")
            return
            
        # Get product data
        values = self.tree.item(selected[0])['values']
        product_id = values[0]
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Product")
        edit_window.geometry("400x300")
        edit_window.configure(bg="#f0f5e7")
        
        # Form fields
        fields = ["Product Name", "Category", "Price (₹)", "Quantity", "Description"]
        entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(edit_window, text=field + ":", bg="#f0f5e7").grid(row=i, column=0, padx=10, pady=10, sticky="w")
            
            if field == "Description":
                entry = tk.Text(edit_window, width=30, height=4)
                entry.grid(row=i, column=1, padx=10, pady=10)
                entry.insert("1.0", values[5])  # Insert description
            else:
                entry = tk.Entry(edit_window, width=30)
                entry.grid(row=i, column=1, padx=10, pady=10)
                # Insert current values
                field_index = {"Product Name": 1, "Category": 2, "Price (₹)": 3, "Quantity": 4}
                entry.insert(0, values[field_index[field]])
                
            entries[field.lower().replace(" ", "_").replace("(₹)", "")] = entry
        
        # Save button
        def save_changes():
            try:
                name = entries["product_name"].get()
                category = entries["category"].get()
                price_str = entries["price"].get()
                quantity_str = entries["quantity"].get()
                description = entries["description"].get("1.0", tk.END).strip()
                
                # Validate
                if not name or not category or not price_str or not quantity_str:
                    messagebox.showwarning("Warning", "Please fill in all required fields.")
                    return
                    
                try:
                    price = float(price_str)
                    quantity = int(quantity_str)
                    
                    if price < 0:
                        messagebox.showwarning("Warning", "Price cannot be negative.")
                        return
                    if quantity < 0:
                        messagebox.showwarning("Warning", "Quantity cannot be negative.")
                        return
                        
                except ValueError:
                    messagebox.showerror("Error", "Price must be a number and quantity must be an integer.")
                    return
                    
                # Update in database
                try:
                    # Check actual column names
                    self.cursor.execute("DESCRIBE wildlife_store")
                    columns = [row[0] for row in self.cursor.fetchall()]
                    
                    # Determine correct column names
                    name_col = "product_name" if "product_name" in columns else "name"
                    cat_col = "product_category" if "product_category" in columns else "category"
                    
                    # Construct the query dynamically
                    query = f"UPDATE wildlife_store SET {name_col} = %s, {cat_col} = %s, price = %s, quantity = %s, description = %s WHERE id = %s"
                    self.cursor.execute(query, (name, category, price, quantity, description, product_id))
                    self.conn.commit()
                    
                    edit_window.destroy()
                    self.load_products()
                    messagebox.showinfo("Success", f"{name} has been updated.")
                    
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Failed to update product: {err}")
                    print(f"Update error: {err}")  # Debug output
            
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to update product: {err}")
        
        tk.Button(edit_window, text="Save Changes", bg="#1e8449", fg="white", 
                 command=save_changes, width=15).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def clear_fields(self):
        """Clear all input fields"""
        for field, entry in self.entries.items():
            if field == "description":
                entry.delete("1.0", tk.END)
            else:
                entry.delete(0, tk.END)
    
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
    """Function to start the Wildlife Store module"""
    root = tk.Tk()
    app = WildlifeStoreApp(root, username)
    root.mainloop()


# Run only if executed directly
if __name__ == "__main__":
    run()
