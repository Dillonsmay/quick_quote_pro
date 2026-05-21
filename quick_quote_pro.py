import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import sqlite3
import os
import webbrowser

class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick Quote Professional v1.2")
        self.root.geometry("950x780")
        
        # Colors
        self.primary_color = "#2c3e50"
        self.bg_color = "#ecf0f1"
        self.button_color = "#3498db"
        self.text_color = "#34495e"
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure('.', background=self.bg_color, foreground=self.text_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.primary_color, font=('Segoe UI', 10, 'bold'))
        self.style.configure('TLabelframe', background=self.bg_color, bordercolor=self.primary_color, relief="solid", borderwidth=1)
        self.style.configure('TLabelframe.Label', background=self.bg_color, foreground=self.primary_color, font=('Segoe UI', 10, 'bold'))
        self.style.configure('TButton', background=self.primary_color, foreground='white', font=('Segoe UI', 10, 'bold'), borderwidth=0)
        self.style.map('TButton', background=[('active', '#34495e'), ('pressed', '#1a252f')])
        self.style.configure('TEntry', fieldbackground='white', bordercolor='#bdc3c7')
        self.style.configure('TCheckbutton', background=self.bg_color, foreground=self.primary_color)
        self.style.configure('Treeview', font=('Segoe UI', 9))
        self.style.configure('Treeview.Heading', font=('Segoe UI', 9, 'bold'), background=self.primary_color, foreground='white')
        
        self.root.configure(bg=self.bg_color)
        
        # Variables
        self.customer_name = tk.StringVar()
        self.labor_hours = tk.DoubleVar(value=0.0)
        self.new_part_name = tk.StringVar()
        self.new_part_cost = tk.DoubleVar(value=0.0)
        
        # Initialize database
        self.init_database()
        
        # Load company info
        self.load_company_info()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Setup GUI
        self.setup_gui()

    def init_database(self):
        conn = sqlite3.connect('quotes.db')
        cursor = conn.cursor()
        
        # Create quotes table if it doesn't exist
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
                flat_disposal_fee REAL NOT NULL,
                shop_name TEXT,
                shop_address TEXT,
                shop_phone TEXT,
                shop_email TEXT,
                tier_low_markup REAL DEFAULT 1.50,
                tier_mid_threshold REAL DEFAULT 200.0,
                tier_mid_markup REAL DEFAULT 1.30,
                tier_high_markup REAL DEFAULT 1.15
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
        
        # Migration for new rate columns
        if 'tier_low_markup' not in cols:
            cursor.execute("ALTER TABLE settings ADD COLUMN tier_low_markup REAL DEFAULT 1.50")
            cursor.execute("ALTER TABLE settings ADD COLUMN tier_mid_threshold REAL DEFAULT 200.0")
            cursor.execute("ALTER TABLE settings ADD COLUMN tier_mid_markup REAL DEFAULT 1.30")
            cursor.execute("ALTER TABLE settings ADD COLUMN tier_high_markup REAL DEFAULT 1.15")
        
        # Seed defaults
        cursor.execute('SELECT * FROM settings WHERE id = 1')
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO settings (id, labor_rate, shop_supply_fee_percent, sales_tax_rate, 
                                    apply_tax_to_parts_only, flat_disposal_fee, shop_name, shop_address, shop_phone, shop_email,
                                    tier_low_markup, tier_mid_threshold, tier_mid_markup, tier_high_markup)
                VALUES (1, 100.0, 10.0, 8.25, 1, 10.0, 'Your Shop Name', '123 Main St, City, ST 12345', '(555) 123-4567', 'shop@example.com',
                        1.50, 200.0, 1.30, 1.15)
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

        # Left Input Engine
        input_frame = ttk.LabelFrame(main_frame, text=" Cost Calculator Engine ", padding="15")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Customer Name:").grid(row=0, column=0, sticky=tk.W, pady=10)
        ttk.Entry(input_frame, textvariable=self.customer_name, width=32).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(input_frame, text="Labor Hours:").grid(row=1, column=0, sticky=tk.W, pady=10)
        ttk.Entry(input_frame, textvariable=self.labor_hours, width=32).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10)

        # --- Itemized Parts Section ---
        parts_frame = ttk.LabelFrame(input_frame, text=" Itemized Parts ", padding="10")
        parts_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=15)
        
        # Treeview Table
        columns = ('part_name', 'raw_cost')
        self.parts_tree = ttk.Treeview(parts_frame, columns=columns, show='headings', height=6)
        self.parts_tree.heading('part_name', text='Part Description')
        self.parts_tree.heading('raw_cost', text='Raw Cost ($)')
        self.parts_tree.column('part_name', width=200)
        self.parts_tree.column('raw_cost', width=100, anchor=tk.E)
        self.parts_tree.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        scrollbar = ttk.Scrollbar(parts_frame, orient=tk.VERTICAL, command=self.parts_tree.yview)
        self.parts_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=3, sticky=(tk.N, tk.S))
        
        # Add Part Controls
        ttk.Label(parts_frame, text="Part Name:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Label(parts_frame, text="Raw Cost:").grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        ttk.Entry(parts_frame, textvariable=self.new_part_name, width=22).grid(row=2, column=0, padx=(0, 5), sticky=tk.W)
        ttk.Entry(parts_frame, textvariable=self.new_part_cost, width=12).grid(row=2, column=1, padx=(0, 5), sticky=tk.W)
        ttk.Button(parts_frame, text="Add Part", command=self.add_part, width=10).grid(row=2, column=2, sticky=tk.W)
        
        ttk.Button(parts_frame, text="Remove Selected Item", command=self.remove_part).grid(row=3, column=0, columnspan=3, pady=(10, 0), sticky=(tk.W, tk.E))

        # Action Buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=25)
        
        ttk.Button(btn_frame, text="Calculate Quote", command=self.calculate_quote, width=16).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="Save to Database", command=self.save_quote, width=16).grid(row=0, column=1, padx=6)

        action_frame = ttk.Frame(input_frame)
        action_frame.grid(row=4, column=0, columnspan=2, pady=8)
        ttk.Button(action_frame, text="Print Quote", command=self.print_quote, width=35).grid(row=0, column=0, padx=6, pady=5)
        ttk.Button(action_frame, text="Save to PDF", command=self.export_to_pdf, width=35).grid(row=1, column=0, padx=6, pady=5)

        # Right Preview Window
        results_frame = ttk.LabelFrame(main_frame, text=" Real-Time Customer Invoice Preview ", padding="15")
        results_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)

        self.result_text = tk.Text(results_frame, width=46, height=32, font=("Consolas", 11), bg="#1e252b", fg="#ecf0f1", relief="solid", bd=1, padx=10, pady=10, spacing3=4)
        self.result_text.config(state='disabled')
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.result_text.insert(tk.END, "Awaiting input...\nEnter details and click 'Calculate Quote'.")

        # Bind Enter key
        for widget in [self.root]:
            widget.bind('<Return>', lambda e: self.calculate_quote())

    def add_part(self):
        name = self.new_part_name.get().strip()
        try:
            cost = float(self.new_part_cost.get())
            if not name:
                messagebox.showerror("Error", "Please enter a part name.")
                return
            if cost < 0:
                messagebox.showerror("Error", "Part cost cannot be negative.")
                return
                
            self.parts_tree.insert('', tk.END, values=(name, f"{cost:.2f}"))
            self.new_part_name.set("")
            self.new_part_cost.set(0.0)
            self.calculate_quote()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric cost.")

    def remove_part(self):
        selected = self.parts_tree.selection()
        if not selected:
            return
        for item in selected:
            self.parts_tree.delete(item)
        self.calculate_quote()

    def calculate_markup(self, parts_cost):
        settings = self.get_current_settings()
        
        if parts_cost <= 50:
            return settings['tier_low_markup']
        elif parts_cost <= settings['tier_mid_threshold']:
            return settings['tier_mid_markup']
        else:
            return settings['tier_high_markup']

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
            'tier_low_markup': row[10],
            'tier_mid_threshold': row[11],
            'tier_mid_markup': row[12],
            'tier_high_markup': row[13]
        }

    def calculate_quote(self, for_print=False):
        try:
            customer = self.customer_name.get().strip()
            hours = self.labor_hours.get()

            if not customer:
                if not for_print:
                    messagebox.showerror("Error", "Customer Name is required.")
                return None

            settings = self.get_current_settings()
            
            # --- Itemized Parts Math ---
            total_raw_parts = 0.0
            total_marked_parts = 0.0
            parts_display = ""
            
            for child in self.parts_tree.get_children():
                part_name, raw_cost = self.parts_tree.item(child, 'values')
                raw_cost = float(raw_cost)
                
                markup_multiplier = self.calculate_markup(raw_cost)
                marked_cost = raw_cost * markup_multiplier
                
                total_raw_parts += raw_cost
                total_marked_parts += marked_cost
                
                # Format to align money beautifully
                parts_display += f"  - {part_name:<20} ${marked_cost:>7.2f}\n"

            if total_raw_parts == 0:
                parts_display = "  - No parts added\n"

            # --- Base Math ---
            labor_total = hours * settings['labor_rate']
            supply_fee = labor_total * (settings['shop_supply_fee_percent'] / 100)
            subtotal = total_marked_parts + labor_total + supply_fee

            if settings['apply_tax_to_parts_only']:
                tax = total_marked_parts * (settings['sales_tax_rate'] / 100)
            else:
                tax = subtotal * (settings['sales_tax_rate'] / 100)

            total = subtotal + tax + settings['flat_disposal_fee']

            # Build display text
            layout = f"==============================================\n"
            layout += f"         {self.company['name'].upper()}\n"
            layout += f" {self.company['address']}\n"
            layout += f" Ph: {self.company['phone']} | {self.company['email']}\n"
            layout += f"==============================================\n"
            layout += f" INVOICE / QUOTE\n"
            layout += f" Date: {datetime.now().strftime('%B %d, %Y')}\n"
            layout += f" Client: {customer}\n"
            layout += f"----------------------------------------------\n"
            layout += f" ITEMIZED PARTS:\n"
            layout += parts_display
            layout += f"                       Parts Total: ${total_marked_parts:.2f}\n"
            layout += f"----------------------------------------------\n"
            layout += f" LABOR: ${labor_total:.2f} ({hours} hrs @ ${settings['labor_rate']:.2f})\n"
            layout += f" Supplies: ${supply_fee:.2f}\n"
            layout += f" SUBTOTAL: ${subtotal:.2f}\n"
            layout += f" Tax: ${tax:.2f}\n"
            if settings['flat_disposal_fee'] > 0:
                layout += f" Disposal Fee: ${settings['flat_disposal_fee']:.2f}\n"
            layout += f"----------------------------------------------\n"
            layout += f" TOTAL DUE: ${total:.2f}\n"
            layout += f"==============================================\n"

            if not for_print:
                self.result_text.config(state='normal')
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, layout)
                self.result_text.config(state='disabled')
            
            if for_print:
                return total, layout
            
            # Return tuple so save_quote can extract the raw parts total for the database
            return total, total_raw_parts

        except Exception as e:
            if not for_print:
                messagebox.showerror("Error", str(e))
            if for_print:
                return None, None
            return None

    def save_quote(self):
        result = self.calculate_quote()
        if not result: return
        total_amount, total_raw_parts = result

        try:
            conn = sqlite3.connect('quotes.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO quotes (customer_name, parts_cost, labor_hours, total_amount)
                VALUES (?, ?, ?, ?)
            ''', (self.customer_name.get().strip(), total_raw_parts, 
                  self.labor_hours.get(), total_amount))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Quote saved to database!")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def export_to_pdf(self):
        total, text = self.calculate_quote(for_print=True)
        if not text: return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not filename: return
            
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        company_header = Paragraph(
            f"<b>{self.company['name'].upper()}</b><br/>"
            f"{self.company['address']}<br/>"
            f"Phone: {self.company['phone']}   |   Email: {self.company['email']}",
            styles['Normal']
        )
        story.append(company_header)
        story.append(Spacer(1, 20))
        
        invoice_details = Paragraph(
            "INVOICE / QUOTE<br/>"
            f"Date: {datetime.now().strftime('%B %d, %Y')}<br/>"
            f"Client: {self.customer_name.get()}",
            styles['Normal']
        )
        story.append(invoice_details)
        story.append(Spacer(1, 20))
        
        # We replace spaces with non-breaking spaces &nbsp; to preserve alignment in PDF
        formatted_text = text.replace('\n', '<br/>').replace(' ', '&nbsp;')
        quote_text = Paragraph(f"<font name='Courier'>{formatted_text}</font>", styles['Normal'])
        story.append(quote_text)
        story.append(Spacer(1, 20))
        
        disclaimer = Paragraph(
            "This quote is valid for 30 days from the date of issue.<br/><br/>"
            "<b>Signature Lines:</b><br/>"
            "Customer Signature: _______________________<br/>"
            "Shop Signature: _______________________", 
            styles['Normal']
        )
        story.append(disclaimer)
        
        doc.build(story)
        messagebox.showinfo("Success", f"PDF saved to:\n{filename}")

    def print_quote(self):
        total, text = self.calculate_quote(for_print=True)
        if not text: return
        
        html = f"""<html>
<head>
<style>
@page {{ margin: 0; }}
@media print {{ body {{ margin: 1cm; }} }}
body {{ font-family: 'Courier New', monospace; margin: 0; padding: 20px; background-color: white; }}
.container {{ max-width: 650px; margin: 0 auto; border: 1px solid #ccc; padding: 30px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
.footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #666; }}
.signature-line {{ display: flex; justify-content: space-between; margin-top: 40px; border-top: 1px solid #000; padding-top: 10px; }}
pre {{ white-space: pre-wrap; word-wrap: break-word; font-size: 14px; line-height: 1.5; }}
</style>
</head>
<body>
<div class="container">
    <pre>{text}</pre>
    <div class="footer">This quote is valid for 30 days from the date of issue.</div>
    <div class="signature-line">
        <span>Customer Signature:</span>
        <span>Shop Signature:</span>
    </div>
</div>
</body>
</html>"""
        
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
                writer.writerow(["ID", "Customer", "Parts Cost (Raw Total)", "Labor Hours", "Total Invoice", "Date"])
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
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(fill=tk.BOTH, expand=True)

        # Populate the treeview with formatted data
        conn = sqlite3.connect('quotes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quotes ORDER BY created_at DESC")
        for row in cursor.fetchall():
            # Format the floats into clean currency strings before displaying
            formatted_row = (
                row[0],             # ID
                row[1],             # Customer
                f"${row[2]:.2f}",   # Parts Cost (rounded to 2 decimals)
                f"{row[3]:.1f}",    # Labor Hours (rounded to 1 decimal)
                f"${row[4]:.2f}",   # Total (rounded to 2 decimals)
                row[5][:10]         # Date (truncates the timestamp to just YYYY-MM-DD)
            )
            tree.insert("", tk.END, values=formatted_row)
        
        def on_closing():
            conn.close()
            quotes_window.destroy()

        quotes_window.protocol("WM_DELETE_WINDOW", on_closing)

    def configure_rates(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Shop Settings & Company Information")
        settings_window.geometry("550x760") 
        settings_window.configure(bg=self.bg_color)
        settings_window.resizable(False, False)

        settings = self.get_current_settings()
        conn = sqlite3.connect('quotes.db')
        cursor = conn.cursor()
        cursor.execute('SELECT shop_name, shop_address, shop_phone, shop_email FROM settings WHERE id=1')
        company_row = cursor.fetchone() or ("Your Shop Name", "", "", "")
        conn.close()

        # --- Company Information Frame ---
        company_frame = ttk.LabelFrame(settings_window, text=" Company Information ", padding=12)
        company_frame.pack(fill=tk.X, padx=20, pady=10)

        entries = {}
        labels = ["Shop Name", "Address", "Phone", "Email"]
        defaults = list(company_row)

        for i, label in enumerate(labels):
            ttk.Label(company_frame, text=label + ":").grid(row=i, column=0, sticky=tk.W, pady=6, padx=5)
            entries[label] = ttk.Entry(company_frame, width=45)
            val = defaults[i] if defaults[i] is not None else ""
            entries[label].insert(0, val)
            entries[label].grid(row=i, column=1, sticky=(tk.W, tk.E), pady=6, padx=5)

        # --- Standard Rates Frame ---
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

        # --- Dynamic Parts Matrix Frame ---
        matrix_frame = ttk.LabelFrame(settings_window, text=" Parts Markup Matrix ", padding=12)
        matrix_frame.pack(fill=tk.X, padx=20, pady=10)
        matrix_frame.columnconfigure(1, weight=1)

        ttk.Label(matrix_frame, text="Markup for Parts Under $50 (%):").grid(row=0, column=0, sticky=tk.W, pady=6, padx=5)
        low_markup_entry = ttk.Entry(matrix_frame, width=15)
        low_pct = (settings.get('tier_low_markup', 1.50) - 1) * 100
        low_markup_entry.insert(0, f"{low_pct:.0f}")
        low_markup_entry.grid(row=0, column=1, sticky=tk.W, pady=6, padx=5)

        ttk.Label(matrix_frame, text="High Ticket Threshold ($):").grid(row=1, column=0, sticky=tk.W, pady=6, padx=5)
        mid_thresh_entry = ttk.Entry(matrix_frame, width=15)
        mid_thresh_entry.insert(0, f"{settings.get('tier_mid_threshold', 200.0):.2f}")
        mid_thresh_entry.grid(row=1, column=1, sticky=tk.W, pady=6, padx=5)

        ttk.Label(matrix_frame, text="Markup for Parts between $50 & Threshold (%):").grid(row=2, column=0, sticky=tk.W, pady=6, padx=5)
        mid_markup_entry = ttk.Entry(matrix_frame, width=15)
        mid_pct = (settings.get('tier_mid_markup', 1.30) - 1) * 100
        mid_markup_entry.insert(0, f"{mid_pct:.0f}")
        mid_markup_entry.grid(row=2, column=1, sticky=tk.W, pady=6, padx=5)

        ttk.Label(matrix_frame, text="Markup for Parts Over Threshold (%):").grid(row=3, column=0, sticky=tk.W, pady=6, padx=5)
        high_markup_entry = ttk.Entry(matrix_frame, width=15)
        high_pct = (settings.get('tier_high_markup', 1.15) - 1) * 100
        high_markup_entry.insert(0, f"{high_pct:.0f}")
        high_markup_entry.grid(row=3, column=1, sticky=tk.W, pady=6, padx=5)

        def save_settings():
            try:
                db_low_markup = (float(low_markup_entry.get()) / 100) + 1
                db_mid_markup = (float(mid_markup_entry.get()) / 100) + 1
                db_high_markup = (float(high_markup_entry.get()) / 100) + 1

                conn = sqlite3.connect('quotes.db')
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE settings 
                    SET labor_rate=?, shop_supply_fee_percent=?, sales_tax_rate=?, 
                        apply_tax_to_parts_only=?, flat_disposal_fee=?,
                        shop_name=?, shop_address=?, shop_phone=?, shop_email=?,
                        tier_low_markup=?, tier_mid_threshold=?, tier_mid_markup=?, tier_high_markup=?
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
                    entries["Email"].get().strip(),
                    db_low_markup,
                    float(mid_thresh_entry.get()),
                    db_mid_markup,
                    db_high_markup
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

    def clear_all_data(self):
        result = messagebox.askyesno(
            "Confirm Purge",
            "Are you sure you want to delete ALL saved quotes? This action cannot be undone.",
            icon='warning'
        )
        
        if result:
            try:
                conn = sqlite3.connect('quotes.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM quotes")
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "All quote data has been deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete data: {str(e)}")

if __name__ == '__main__':
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()