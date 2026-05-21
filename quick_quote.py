import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import os

class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick Quote Validator")
        self.root.geometry("850x500")
        
        # Configure a clean theme with custom colors
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Apply custom styling
        self.style.configure('TFrame', background='#ecf0f1')
        self.style.configure('TLabel', background='#ecf0f1', foreground='#2c3e50')
        self.style.configure('TLabelframe', background='#ecf0f1', foreground='#2c3e50')
        self.style.configure('TLabelframe.Label', background='#ecf0f1', foreground='#2c3e50')
        self.style.configure('TButton', background='#2c3e50', foreground='white')
        self.style.map('TButton', background=[('active', '#34495e')])
        
        # Create database
        self.create_database()

        # Initialize variables
        self.customer_name = tk.StringVar()
        self.parts_cost = tk.DoubleVar(value=0.0)
        self.labor_hours = tk.DoubleVar(value=0.0)

        # Create menu bar
        self.create_menu_bar()

        # Create GUI
        self.setup_gui()

    def create_database(self):
        """Create a clean local SQLite database"""
        conn = sqlite3.connect('quotes.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                parts_cost REAL NOT NULL,
                labor_hours REAL NOT NULL,
                total_amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create settings table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                labor_rate REAL NOT NULL,
                shop_supply_fee_percent REAL NOT NULL,
                sales_tax_rate REAL NOT NULL,
                apply_tax_to_parts_only BOOLEAN NOT NULL,
                flat_disposal_fee REAL NOT NULL
            )
        ''')
        
        # Insert default values if no settings exist
        cursor.execute('SELECT * FROM settings WHERE id = 1')
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO settings (id, labor_rate, shop_supply_fee_percent, sales_tax_rate, apply_tax_to_parts_only, flat_disposal_fee)
                VALUES (1, 100.0, 10.0, 8.5, 0, 25.0)
            ''')
        
        conn.commit()
        conn.close()

    def create_menu_bar(self):
        """Create the top menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.exit_app)

        # Database Menu
        database_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Database", menu=database_menu)
        database_menu.add_command(label="View Saved Quotes", command=self.view_saved_quotes)
        database_menu.add_command(label="Clear All Data", command=self.clear_all_data)

        # Settings Menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Configure Rates", command=self.configure_rates)

    def exit_app(self):
        """Exit the application"""
        self.root.quit()

    def setup_gui(self):
        """Setup a clean, split-pane layout with modern styling"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Left Side: Input Panel
        input_frame = ttk.LabelFrame(main_frame, text=" Cost Calculator ", padding="15")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        input_frame.configure(style='TLabelframe')

        # Configure grid weights for responsive layout
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Customer Name:").grid(row=0, column=0, sticky=tk.W, pady=8)
        customer_entry = ttk.Entry(input_frame, textvariable=self.customer_name, width=35)
        customer_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=8)
        customer_entry.configure(style='TEntry')

        ttk.Label(input_frame, text="Raw Parts Cost ($):").grid(row=1, column=0, sticky=tk.W, pady=8)
        parts_entry = ttk.Entry(input_frame, textvariable=self.parts_cost, width=35)
        parts_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=8)
        parts_entry.configure(style='TEntry')

        ttk.Label(input_frame, text="Labor Hours:").grid(row=2, column=0, sticky=tk.W, pady=8)
        labor_entry = ttk.Entry(input_frame, textvariable=self.labor_hours, width=35)
        labor_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=8)
        labor_entry.configure(style='TEntry')

        # Buttons Panel
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        calc_button = ttk.Button(btn_frame, text="Calculate Quote", command=self.calculate_quote, width=18)
        calc_button.grid(row=0, column=0, padx=5)

        save_button = ttk.Button(btn_frame, text="Save to Database", command=self.save_quote, width=18)
        save_button.grid(row=0, column=1, padx=5)

        # Right Side: Preview Breakdown Panel
        results_frame = ttk.LabelFrame(main_frame, text=" Customer Quote Breakdown ", padding="15")
        results_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        results_frame.configure(style='TLabelframe')

        self.result_text = tk.Text(results_frame, width=42, height=18, font=("Consolas", 10), bg="#f8f9fa", fg="#212529", relief="solid", bd=1)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Simple placeholder instructions
        self.result_text.insert(tk.END, "Enter details on the left and click\n'Calculate Quote' to generate invoice visual.")

        # Key binds for instant recalculation
        customer_entry.bind('<Return>', lambda e: self.calculate_quote())
        parts_entry.bind('<Return>', lambda e: self.calculate_quote())
        labor_entry.bind('<Return>', lambda e: self.calculate_quote())

    def calculate_markup(self, parts_cost):
        """Sliding scale markup calculation matrix"""
        if parts_cost <= 50:
            return 1.50  # 50% markup
        elif parts_cost <= 200:
            return 1.30  # 30% markup
        else:
            return 1.15  # 15% markup

    def calculate_quote(self):
        try:
            customer = self.customer_name.get().strip()
            parts_cost = self.parts_cost.get()
            labor_hours = self.labor_hours.get()

            if not customer:
                messagebox.showerror("Validation Error", "Please provide a Customer Name.")
                return

            # Get current settings
            settings = self.get_current_settings()

            # Calculations
            labor_total = labor_hours * settings['labor_rate']
            
            markup_multiplier = self.calculate_markup(parts_cost)
            markup_percentage = int((markup_multiplier - 1) * 100)
            parts_with_markup = parts_cost * markup_multiplier
            total_markup_profit = parts_with_markup - parts_cost

            shop_supply_fee = labor_total * (settings['shop_supply_fee_percent'] / 100)
            subtotal = parts_with_markup + labor_total + shop_supply_fee
            
            # Apply tax if enabled
            tax_amount = 0
            if settings['sales_tax_rate'] > 0:
                if settings['apply_tax_to_parts_only']:
                    tax_amount = parts_cost * (settings['sales_tax_rate'] / 100)
                else:
                    tax_amount = subtotal * (settings['sales_tax_rate'] / 100)
            
            # Add flat disposal fee
            total_amount = subtotal + tax_amount + settings['flat_disposal_fee']

            # Build a clean, professional print layout text string
            layout =  f"========================================\n"
            layout += f"        INVOICE / QUOTE PREVIEW         \n"
            layout += f"========================================\n"
            layout += f" Client Name: {customer}\n"
            layout += f"----------------------------------------\n"
            layout += f" PARTS BREAKDOWN:\n"
            layout += f"  - Base Cost:           ${parts_cost:.2f}\n"
            layout += f"  - Matrix Markup ({markup_percentage}%):  +${total_markup_profit:.2f}\n"
            layout += f"  - Total Parts Charge:  ${parts_with_markup:.2f}\n"
            layout += f"\n"
            layout += f" LABOR & FEES BREAKDOWN:\n"
            layout += f"  - Labor ({labor_hours} hrs @ ${settings['labor_rate']:.2f}):  ${labor_total:.2f}\n"
            layout += f"  - Shop Supplies ({settings['shop_supply_fee_percent']}%):  +${shop_supply_fee:.2f}\n"
            layout += f"\n"
            
            if settings['sales_tax_rate'] > 0:
                tax_type = "Parts Only" if settings['apply_tax_to_parts_only'] else "Total Amount"
                layout += f" TAX BREAKDOWN:\n"
                layout += f"  - Sales Tax ({settings['sales_tax_rate']}% of {tax_type}):  +${tax_amount:.2f}\n"
            
            if settings['flat_disposal_fee'] > 0:
                layout += f" DISPOSAL FEES:\n"
                layout += f"  - Environmental/Disposal Fee:  +${settings['flat_disposal_fee']:.2f}\n"
            
            layout += f"----------------------------------------\n"
            layout += f" TOTAL ESTIMATED INVESTMENT:\n"
            layout += f"  >>> ${total_amount:.2f} <<<\n"
            layout += f"========================================\n"

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, layout)
            return total_amount

        except Exception as e:
            messagebox.showerror("Calculation Error", "Please check your inputs. Make sure fields contain valid numbers.")

    def save_quote(self):
        try:
            total = self.calculate_quote()
            if not total: 
                return # Stop if verification calculation fails
                
            customer = self.customer_name.get().strip()
            parts_cost = self.parts_cost.get()
            labor_hours = self.labor_hours.get()

            conn = sqlite3.connect('quotes.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO quotes (customer_name, parts_cost, labor_hours, total_amount)
                VALUES (?, ?, ?, ?)
            ''', (customer, parts_cost, labor_hours, total))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Quote for {customer} saved locally to quotes.db!")

        except Exception as e:
            messagebox.showerror("Database Error", "Failed to write record to the local ledger.")

    def get_current_settings(self):
        """Get current settings from database"""
        conn = sqlite3.connect('quotes.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT labor_rate, shop_supply_fee_percent, sales_tax_rate, 
                   apply_tax_to_parts_only, flat_disposal_fee 
            FROM settings WHERE id = 1
        ''')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'labor_rate': result[0],
                'shop_supply_fee_percent': result[1],
                'sales_tax_rate': result[2],
                'apply_tax_to_parts_only': bool(result[3]),
                'flat_disposal_fee': result[4]
            }
        else:
            # Return default values
            return {
                'labor_rate': 100.0,
                'shop_supply_fee_percent': 10.0,
                'sales_tax_rate': 8.5,
                'apply_tax_to_parts_only': False,
                'flat_disposal_fee': 25.0
            }

    def view_saved_quotes(self):
        """Open a window showing all saved quotes"""
        # Create a new top-level window
        quote_window = tk.Toplevel(self.root)
        quote_window.title("Saved Quotes")
        quote_window.geometry("800x600")

        # Create a frame for the treeview and scrollbar
        main_frame = ttk.Frame(quote_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create Treeview widget
        columns = ("ID", "Customer Name", "Parts Cost", "Labor Hours", "Total Amount", "Created At")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)
        
        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack the tree and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate with data from database
        conn = sqlite3.connect('quotes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quotes ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", tk.END, values=row)

    def clear_all_data(self):
        """Securely purge all data from the database"""
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to delete ALL saved quotes? This action cannot be undone."):
            try:
                conn = sqlite3.connect('quotes.db')
                cursor = conn.cursor()
                
                # Delete all records from quotes table
                cursor.execute("DELETE FROM quotes")
                
                # Reset auto-increment counter for the ID column
                cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='quotes'")
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "All saved quotes have been cleared from the database.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear data: {str(e)}")

    def configure_rates(self):
        """Open a window to configure labor rate and shop supply fee"""
        # Create a new top-level window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configure Rates")
        settings_window.geometry("400x350")
        settings_window.configure(bg='#ecf0f1')
        
        # Get current values
        settings = self.get_current_settings()
        
        # Create frame for inputs
        input_frame = ttk.LabelFrame(settings_window, text="Rate Configuration", padding="20")
        input_frame.pack(fill=tk.BOTH, expand=True)
        input_frame.configure(style='TLabelframe')

        # Labor Rate Input
        labor_frame = ttk.Frame(input_frame)
        labor_frame.pack(pady=10)
        
        ttk.Label(labor_frame, text="Labor Rate ($/hr):").pack(side=tk.LEFT)
        labor_entry = ttk.Entry(labor_frame, width=15)
        labor_entry.insert(0, str(settings['labor_rate']))
        labor_entry.pack(side=tk.RIGHT)
        
        # Shop Supply Fee Input
        shop_frame = ttk.Frame(input_frame)
        shop_frame.pack(pady=10)
        
        ttk.Label(shop_frame, text="Shop Supply Fee (%):").pack(side=tk.LEFT)
        shop_entry = ttk.Entry(shop_frame, width=15)
        shop_entry.insert(0, str(settings['shop_supply_fee_percent']))
        shop_entry.pack(side=tk.RIGHT)
        
        # Sales Tax Rate Input
        tax_frame = ttk.Frame(input_frame)
        tax_frame.pack(pady=10)
        
        ttk.Label(tax_frame, text="Sales Tax Rate (%):").pack(side=tk.LEFT)
        tax_entry = ttk.Entry(tax_frame, width=15)
        tax_entry.insert(0, str(settings['sales_tax_rate']))
        tax_entry.pack(side=tk.RIGHT)
        
        # Apply Tax to Parts Only Checkbox
        self.apply_tax_var = tk.BooleanVar(value=settings['apply_tax_to_parts_only'])
        apply_tax_frame = ttk.Frame(input_frame)
        apply_tax_frame.pack(pady=10)
        
        ttk.Checkbutton(apply_tax_frame, text="Apply Tax to Parts Only", variable=self.apply_tax_var).pack(side=tk.LEFT)
        
        # Flat Disposal Fee Input
        disposal_frame = ttk.Frame(input_frame)
        disposal_frame.pack(pady=10)
        
        ttk.Label(disposal_frame, text="Flat Environmental/Disposal Fee ($):").pack(side=tk.LEFT)
        disposal_entry = ttk.Entry(disposal_frame, width=15)
        disposal_entry.insert(0, str(settings['flat_disposal_fee']))
        disposal_entry.pack(side=tk.RIGHT)
        
        # Save button
        def save_settings():
            try:
                new_labor_rate = float(labor_entry.get())
                new_shop_fee = float(shop_entry.get())
                new_tax_rate = float(tax_entry.get())
                new_apply_tax_parts_only = self.apply_tax_var.get()
                new_disposal_fee = float(disposal_entry.get())
                
                conn = sqlite3.connect('quotes.db')
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE settings 
                    SET labor_rate=?, shop_supply_fee_percent=?, sales_tax_rate=?,
                        apply_tax_to_parts_only=?, flat_disposal_fee=?
                    WHERE id=1
                ''', (new_labor_rate, new_shop_fee, new_tax_rate, 
                      int(new_apply_tax_parts_only), new_disposal_fee))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Settings updated successfully!")
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for all fields.")
        
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(pady=20)
        
        save_btn = ttk.Button(button_frame, text="Save Settings", command=save_settings)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=settings_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()
