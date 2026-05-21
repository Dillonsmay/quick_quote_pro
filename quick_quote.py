import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import webbrowser
import os

class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick Quote Professional v1.1")
        self.root.geometry("880x580")  
        
        # Colors
        self.bg_color = '#ecf0f1'
        self.panel_bg = '#ffffff'
        self.primary_color = '#2c3e50'
        self.text_color = '#34495e'
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure('.', background=self.bg_color, foreground=self.text_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.primary_color, font=('Segoe UI', 10))
        self.style.configure('TLabelframe', background=self.bg_color, bordercolor=self.primary_color, relief="solid", borderwidth=1)
        self.style.configure('TLabelframe.Label', background=self.bg_color, foreground=self.primary_color, font=('Segoe UI', 10, 'bold'))
        self.style.configure('TButton', background=self.primary_color, foreground='white', font=('Segoe UI', 10, 'bold'), borderwidth=0)
        self.style.map('TButton', background=[('active', '#34495e'), ('pressed', '#1a252f')])
        self.style.configure('TEntry', fieldbackground='white', bordercolor='#bdc3c7')
        self.style.configure('TCheckbutton', background=self.bg_color, foreground=self.primary_color)

        self.create_database()
        self.load_company_info()

        # Variables
        self.customer_name = tk.StringVar()
        self.parts_cost = tk.DoubleVar(value=0.0)
        self.labor_hours = tk.DoubleVar(value=0.0)

        self.create_menu_bar()
        self.setup_gui()

    def create_database(self):
        conn = sqlite3.connect('quotes.db')
        cursor = conn.cursor()
        
        # Quotes table
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
        
        # Settings table with company info
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                labor_rate REAL NOT NULL,
                shop_supply_fee_percent REAL NOT NULL,
                sales_tax_rate REAL NOT NULL,
                apply_tax_to_parts_only BOOLEAN NOT NULL,
                flat_disposal_fee REAL NOT NULL,
                shop_name TEXT,
                shop_address TEXT,
                shop_phone TEXT,
                shop_email TEXT
            )
        ''')
        
        # Migration for older DBs
        cursor.execute("PRAGMA table_info(settings);")
        cols = [col[1] for col in cursor.fetchall()]
        if 'shop_name' not in cols:
            cursor.execute("ALTER TABLE settings ADD COLUMN shop_name TEXT")
            cursor.execute("ALTER TABLE settings ADD COLUMN shop_address TEXT")
            cursor.execute("ALTER TABLE settings ADD COLUMN shop_phone TEXT")
            cursor.execute("ALTER TABLE settings ADD COLUMN shop_email TEXT")
        
        # Seed defaults
        cursor.execute('SELECT * FROM settings WHERE id = 1')
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO settings (id, labor_rate, shop_supply_fee_percent, sales_tax_rate, 
                                    apply_tax_to_parts_only, flat_disposal_fee, shop_name, shop_address, shop_phone, shop_email)
                VALUES (1, 100.0, 10.0, 8.25, 1, 10.0, 'Your Shop Name', '123 Main St, City, ST 12345', '(555) 123-4567', 'shop@example.com')
            ''')
        
        conn.commit()
        conn.close()

    def load_company_info(self):
        conn = sqlite3.connect('quotes.db')
        cursor = conn.cursor()
        cursor.execute('SELECT shop_name, shop_address, shop_phone, shop_email FROM settings WHERE id=1')
        row = cursor.fetchone()
        conn.close()
        
        self.company = {
            'name': row[0] or 'Your Shop Name',
            'address': row[1] or '',
            'phone': row[2] or '',
            'email': row[3] or ''
        }

    def create_menu_bar(self):
        menubar = tk.Menu(self.root, bg=self.primary_color, fg='white')
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)

        database_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Database", menu=database_menu)
        database_menu.add_command(label="View Saved Quotes", command=self.view_saved_quotes)
        database_menu.add_command(label="Export History to CSV", command=self.export_to_csv)
        database_menu.add_command(label="Purge All Data", command=self.clear_all_data)

        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Configure Shop Rates & Info", command=self.configure_rates)

    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Left Input
        input_frame = ttk.LabelFrame(main_frame, text=" Cost Calculator Engine ", padding="15")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Customer Name:").grid(row=0, column=0, sticky=tk.W, pady=10)
        ttk.Entry(input_frame, textvariable=self.customer_name, width=32).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(input_frame, text="Raw Parts Cost ($):").grid(row=1, column=0, sticky=tk.W, pady=10)
        ttk.Entry(input_frame, textvariable=self.parts_cost, width=32).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(input_frame, text="Labor Hours:").grid(row=2, column=0, sticky=tk.W, pady=10)
        ttk.Entry(input_frame, textvariable=self.labor_hours, width=32).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=25)
        
        ttk.Button(btn_frame, text="Calculate Quote", command=self.calculate_quote, width=16).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="Save to Database", command=self.save_quote, width=16).grid(row=0, column=1, padx=6)

        # New action buttons
        action_frame = ttk.Frame(input_frame)
        action_frame.grid(row=4, column=0, columnspan=2, pady=8)
        ttk.Button(action_frame, text="Print Quote", command=self.print_quote, width=35).grid(row=0, column=0, padx=6)

        # Right Preview
        results_frame = ttk.LabelFrame(main_frame, text=" Real-Time Customer Invoice Preview ", padding="15")
        results_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)

        self.result_text = tk.Text(results_frame, width=44, height=22, font=("Consolas", 10), bg="#f8f9fa", fg="#2c3e50", relief="solid", bd=1, padx=10, pady=10)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.result_text.insert(tk.END, "Awaiting input...\nEnter details and click 'Calculate Quote'.")

        # Bind Enter key
        for widget in [self.root]:
            widget.bind('<Return>', lambda e: self.calculate_quote())

    def calculate_markup(self, parts_cost):
        if parts_cost <= 50: return 1.50
        elif parts_cost <= 200: return 1.30
        else: return 1.15

    def get_current_settings(self):
        conn = sqlite3.connect('quotes.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM settings WHERE id=1')
        row = cursor.fetchone()
        conn.close()
        
        return {
            'labor_rate': row[1],
            'shop_supply_fee_percent': row[2],
            'sales_tax_rate': row[3],
            'apply_tax_to_parts_only': bool(row[4]),
            'flat_disposal_fee': row[5],
        }

    def calculate_quote(self, for_print=False):
        try:
            customer = self.customer_name.get().strip()
            parts = self.parts_cost.get()
            hours = self.labor_hours.get()

            if not customer:
                if not for_print:
                    messagebox.showerror("Error", "Customer Name is required.")
                return None

            settings = self.get_current_settings()
            labor_total = hours * settings['labor_rate']
            markup = self.calculate_markup(parts)
            parts_marked = parts * markup
            supply_fee = labor_total * (settings['shop_supply_fee_percent'] / 100)
            subtotal = parts_marked + labor_total + supply_fee

            if settings['apply_tax_to_parts_only']:
                tax = parts_marked * (settings['sales_tax_rate'] / 100)
            else:
                tax = subtotal * (settings['sales_tax_rate'] / 100)

            total = subtotal + tax + settings['flat_disposal_fee']

            # Build display text
            layout = f"========================================\n"
            layout += f"        {self.company['name'].upper()}\n"
            layout += f"{self.company['address']}\n"
            layout += f"Phone: {self.company['phone']}   |   {self.company['email']}\n"
            layout += f"========================================\n"
            layout += f" INVOICE / QUOTE\n"
            layout += f" Date: {datetime.now().strftime('%B %d, %Y')}\n"
            layout += f" Client: {customer}\n"
            layout += f"----------------------------------------\n"
            layout += f" PARTS: ${parts_marked:.2f} (Markup: {int((markup-1)*100)}%)\n"
            layout += f" LABOR: ${labor_total:.2f} ({hours} hrs @ ${settings['labor_rate']:.2f})\n"
            layout += f" Supplies: ${supply_fee:.2f}\n"
            layout += f" SUBTOTAL: ${subtotal:.2f}\n"
            layout += f" Tax: ${tax:.2f}\n"
            if settings['flat_disposal_fee'] > 0:
                layout += f" Disposal Fee: ${settings['flat_disposal_fee']:.2f}\n"
            layout += f"----------------------------------------\n"
            layout += f" TOTAL DUE: ${total:.2f}\n"
            layout += f"========================================\n"

            if not for_print:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, layout)
            
            # FIXED: Return both values if requested, otherwise just the total
            if for_print:
                return total, layout
            return total

        except Exception as e:
            if not for_print:
                messagebox.showerror("Error", str(e))
            if for_print:
                return None, None
            return None

    def save_quote(self):
        result = self.calculate_quote()
        if not result: return
        total = result

        try:
            conn = sqlite3.connect('quotes.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO quotes (customer_name, parts_cost, labor_hours, total_amount)
                VALUES (?, ?, ?, ?)
            ''', (self.customer_name.get().strip(), self.parts_cost.get(), 
                  self.labor_hours.get(), total))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Quote saved to database!")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def print_quote(self):
        total, text = self.calculate_quote(for_print=True)
        if not text: return
        
        # Create temporary HTML for better printing
        html = f"""<html><body style="font-family: Consolas, monospace; margin: 40px;">
        <pre>{text}</pre>
        </body></html>"""
        
        temp_file = "temp_quote.html"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(html)
        
        webbrowser.open('file://' + os.path.realpath(temp_file))

    def export_to_csv(self):
        conn = sqlite3.connect('quotes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quotes ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            messagebox.showinfo("No Data", "No quotes to export yet.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if filename:
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Customer", "Parts Cost", "Labor Hours", "Total", "Date"])
                writer.writerows(rows)
            messagebox.showinfo("Export Complete", f"History exported to:\n{filename}")

    def view_saved_quotes(self):
        quotes_window = tk.Toplevel(self.root)
        quotes_window.title("Saved Quotes")
        quotes_window.geometry("800x600")
        quotes_window.configure(bg=self.bg_color)

        tree_frame = ttk.Frame(quotes_window, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Customer", "Parts Cost", "Labor Hours", "Total", "Date")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        y_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        x_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        conn = sqlite3.connect('quotes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quotes ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", tk.END, values=row)

    def clear_all_data(self):
        result = messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete ALL saved quotes? This action cannot be undone."
        )
        
        if result: 
            try:
                conn = sqlite3.connect('quotes.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM quotes")
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "All saved quotes have been deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete data: {str(e)}")

    def configure_rates(self):
        """Updated settings window with company info"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Shop Settings & Company Information")
        settings_window.geometry("520x580")
        settings_window.configure(bg=self.bg_color)
        settings_window.resizable(False, False)

        settings = self.get_current_settings()
        conn = sqlite3.connect('quotes.db')
        cursor = conn.cursor()
        cursor.execute('SELECT shop_name, shop_address, shop_phone, shop_email FROM settings WHERE id=1')
        company_row = cursor.fetchone() or ("Your Shop Name", "", "", "")
        conn.close()

        company_frame = ttk.LabelFrame(settings_window, text=" Company Information ", padding=12)
        company_frame.pack(fill=tk.X, padx=20, pady=10)

        entries = {}
        labels = ["Shop Name", "Address", "Phone", "Email"]
        defaults = list(company_row)

        for i, label in enumerate(labels):
            ttk.Label(company_frame, text=label + ":").grid(row=i, column=0, sticky=tk.W, pady=6, padx=5)
            entries[label] = ttk.Entry(company_frame, width=45)
            
            # FIXED: Fallback to an empty string if a column value is None
            val = defaults[i] if defaults[i] is not None else ""
            entries[label].insert(0, val)
            
            entries[label].grid(row=i, column=1, sticky=(tk.W, tk.E), pady=6, padx=5)

        rate_frame = ttk.LabelFrame(settings_window, text=" Rate Configuration ", padding=12)
        rate_frame.pack(fill=tk.X, padx=20, pady=10)
        rate_frame.columnconfigure(1, weight=1)

        ttk.Label(rate_frame, text="Labor Rate ($/hr):").grid(row=0, column=0, sticky=tk.W, pady=6, padx=5)
        labor_entry = ttk.Entry(rate_frame, width=15)
        labor_entry.insert(0, f"{settings['labor_rate']:.2f}")
        labor_entry.grid(row=0, column=1, sticky=tk.W, pady=6, padx=5)

        ttk.Label(rate_frame, text="Shop Supplies (%):").grid(row=1, column=0, sticky=tk.W, pady=6, padx=5)
        supply_entry = ttk.Entry(rate_frame, width=15)
        supply_entry.insert(0, f"{settings['shop_supply_fee_percent']:.2f}")
        supply_entry.grid(row=1, column=1, sticky=tk.W, pady=6, padx=5)

        ttk.Label(rate_frame, text="Sales Tax (%):").grid(row=2, column=0, sticky=tk.W, pady=6, padx=5)
        tax_entry = ttk.Entry(rate_frame, width=15)
        tax_entry.insert(0, f"{settings['sales_tax_rate']:.2f}")
        tax_entry.grid(row=2, column=1, sticky=tk.W, pady=6, padx=5)

        ttk.Label(rate_frame, text="Disposal Fee ($):").grid(row=3, column=0, sticky=tk.W, pady=6, padx=5)
        disposal_entry = ttk.Entry(rate_frame, width=15)
        disposal_entry.insert(0, f"{settings['flat_disposal_fee']:.2f}")
        disposal_entry.grid(row=3, column=1, sticky=tk.W, pady=6, padx=5)

        tax_parts_var = tk.BooleanVar(value=settings['apply_tax_to_parts_only'])
        ttk.Checkbutton(rate_frame, text="Apply sales tax to Parts only (not labor/supplies)", 
                       variable=tax_parts_var).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10, padx=5)

        def save_settings():
            try:
                conn = sqlite3.connect('quotes.db')
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE settings 
                    SET labor_rate=?, shop_supply_fee_percent=?, sales_tax_rate=?, 
                        apply_tax_to_parts_only=?, flat_disposal_fee=?,
                        shop_name=?, shop_address=?, shop_phone=?, shop_email=?
                    WHERE id=1
                ''', (
                    float(labor_entry.get()),
                    float(supply_entry.get()),
                    float(tax_entry.get()),
                    int(tax_parts_var.get()),
                    float(disposal_entry.get()),
                    entries["Shop Name"].get().strip(),
                    entries["Address"].get().strip(),
                    entries["Phone"].get().strip(),
                    entries["Email"].get().strip()
                ))
                conn.commit()
                conn.close()
                
                self.load_company_info()  
                messagebox.showinfo("Success", "Settings saved successfully!")
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid numbers.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        btn_frame = ttk.Frame(settings_window)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Save Settings", command=save_settings, width=15).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=settings_window.destroy, width=15).grid(row=0, column=1, padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()
