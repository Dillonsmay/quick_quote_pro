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
        self.root.title("Quick Quote Pro")
        self.root.geometry("900x700")
        
        # Colors
        self.primary_color = "#2c3e50"
        self.bg_color = "#ecf0f1"
        self.button_color = "#3498db"
        
        self.root.configure(bg=self.bg_color)
        
        # Variables
        self.customer_name = tk.StringVar()
        self.parts_cost = tk.DoubleVar(value=0.0)
        self.labor_hours = tk.DoubleVar(value=0.0)
        
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

        # New action buttons - stacked vertically
        action_frame = ttk.Frame(input_frame)
        action_frame.grid(row=4, column=0, columnspan=2, pady=8)
        ttk.Button(action_frame, text="Print Quote", command=self.print_quote, width=35).grid(row=0, column=0, padx=6, pady=5)
        ttk.Button(action_frame, text="Save to PDF", command=self.export_to_pdf, width=35).grid(row=1, column=0, padx=6, pady=5)

        # Right Preview
        results_frame = ttk.LabelFrame(main_frame, text=" Real-Time Customer Invoice Preview ", padding="15")
        results_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)

        self.result_text = tk.Text(results_frame, width=44, height=22, font=("Consolas", 11), bg="#1e252b", fg="#ecf0f1", relief="solid", bd=1, padx=10, pady=10)
        # Set to disabled state on initialization
        self.result_text.config(state='disabled')
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.result_text.insert(tk.END, "Awaiting input...\nEnter details and click 'Calculate Quote'.")

        # Bind Enter key
        for widget in [self.root]:
            widget.bind('<Return>', lambda e: self.calculate_quote())

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
            'tier_low_markup': row[10],      # New column
            'tier_mid_threshold': row[11],    # New column  
            'tier_mid_markup': row[12],       # New column
            'tier_high_markup': row[13]       # New column
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

            # Temporarily enable text widget for updates
            if not for_print:
                self.result_text.config(state='normal')
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, layout)
                # Set back to disabled state immediately after updating
                self.result_text.config(state='disabled')
            
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

    def export_to_pdf(self):
        # Get the quote details
        total, text = self.calculate_quote(for_print=True)
        if not text: return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not filename:
            return
            
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Create content elements
        story = []
        
        # Company header
        company_header = Paragraph(
            f"<b>{self.company['name'].upper()}</b><br/>"
            f"{self.company['address']}<br/>"
            f"Phone: {self.company['phone']}   |   Email: {self.company['email']}",
            styles['Normal']
        )
        story.append(company_header)
        story.append(Spacer(1, 20))
        
        # Invoice details
        invoice_details = Paragraph(
            "INVOICE / QUOTE<br/>"
            f"Date: {datetime.now().strftime('%B %d, %Y')}<br/>"
            f"Client: {self.customer_name.get()}",
            styles['Normal']
        )
        story.append(invoice_details)
        story.append(Spacer(1, 20))
        
        # Quote text
        quote_text = Paragraph(text.replace('\n', '<br/>'), styles['Normal'])
        story.append(quote_text)
        story.append(Spacer(1, 20))
        
        # Disclaimer and signature lines
        disclaimer = Paragraph(
            "This quote is valid for 30 days from the date of issue.<br/><br/>"
            "<b>Signature Lines:</b><br/>"
            "Customer Signature: _______________________<br/>"
            "Shop Signature: _______________________", 
            styles['Normal']
        )
        story.append(disclaimer)
        
        # Build PDF
        doc.build(story)
        messagebox.showinfo("Success", f"PDF saved to:\n{filename}")

    def print_quote(self):
        total, text = self.calculate_quote(for_print=True)
        if not text: return
        
        # Create temporary HTML for better printing
        html = f"""<html>
<head>
<style>
@page {{
    margin: 0;
}}
@media print {{
    body {{
        margin: 1cm;
    }}
}}
body {{
    font-family: 'Courier New', monospace;
    margin: 0;
    padding: 20px;
    background-color: white;
}}
.container {{
    max-width: 600px;
    margin: 0 auto;
    border: 1px solid #ccc;
    padding: 20px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}}
.invoice-header {{
    text-align: center;
    font-size: 18px;
    margin-bottom: 20px;
}}
.invoice-details {{
    margin-bottom: 20px;
}}
.line-item {{
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px solid #eee;
}}
.total-row {{
    font-weight: bold;
    font-size: 18px;
    margin-top: 10px;
}}
.footer {{
    margin-top: 30px;
    text-align: center;
    font-size: 12px;
    color: #666;
}}
.signature-line {{
    display: flex;
    justify-content: space-between;
    margin-top: 40px;
    border-top: 1px solid #000;
    padding-top: 10px;
}}
</style>
</head>
<body>
<div class="container">
    <div class="invoice-header">
        {self.company['name'].upper()}<br>
        {self.company['address']}<br>
        Phone: {self.company['phone']}   |   Email: {self.company['email']}
    </div>
    
    <div class="invoice-details">
        <div>INVOICE / QUOTE</div>
        <div>Date: {datetime.now().strftime('%B %d, %Y')}</div>
        <div>Client: {self.customer_name.get()}</div>
    </div>

    <pre>{text}</pre>

    <div class="footer">
        This quote is valid for 30 days from the date of issue.
    </div>

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
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        tree.heading("ID", text="ID")
        tree.heading("Customer", text="Customer")
        tree.heading("Parts Cost", text="Parts Cost")
        tree.heading("Labor Hours", text="Labor Hours")
        tree.heading("Total", text="Total")
        tree.heading("Date", text="Date")
        tree.pack(fill=tk.BOTH, expand=True)

        # Populate the treeview with data
        conn = sqlite3.connect('quotes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quotes ORDER BY created_at DESC")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
        
        def on_closing():
            conn.close()
            quotes_window.destroy()

        quotes_window.protocol("WM_DELETE_WINDOW", on_closing)

    def configure_rates(self):
        # This method is now deprecated and replaced by the updated configure_rates
        pass

    def clear_all_data(self):
        # Ask for confirmation
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
