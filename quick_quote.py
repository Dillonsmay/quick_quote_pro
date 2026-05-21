import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick Quote Validator")
        self.root.geometry("850x500")
        
        # Configure a clean theme
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Create database
        self.create_database()

        # Initialize variables
        self.customer_name = tk.StringVar()
        self.parts_cost = tk.DoubleVar(value=0.0)
        self.labor_hours = tk.DoubleVar(value=0.0)

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
        conn.commit()
        conn.close()

    def setup_gui(self):
        """Setup a clean, split-pane layout"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Left Side: Input Panel
        input_frame = ttk.LabelFrame(main_frame, text=" Cost Calculator ", padding="15")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        ttk.Label(input_frame, text="Customer Name:").grid(row=0, column=0, sticky=tk.W, pady=8)
        customer_entry = ttk.Entry(input_frame, textvariable=self.customer_name, width=35)
        customer_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=8)

        ttk.Label(input_frame, text="Raw Parts Cost ($):").grid(row=1, column=0, sticky=tk.W, pady=8)
        parts_entry = ttk.Entry(input_frame, textvariable=self.parts_cost, width=35)
        parts_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=8)

        ttk.Label(input_frame, text="Labor Hours:").grid(row=2, column=0, sticky=tk.W, pady=8)
        labor_entry = ttk.Entry(input_frame, textvariable=self.labor_hours, width=35)
        labor_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=8)

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

            # Calculations
            labor_rate = 100.0  
            labor_total = labor_hours * labor_rate
            
            markup_multiplier = self.calculate_markup(parts_cost)
            markup_percentage = int((markup_multiplier - 1) * 100)
            parts_with_markup = parts_cost * markup_multiplier
            total_markup_profit = parts_with_markup - parts_cost

            shop_supply_fee = labor_total * 0.1
            total_amount = parts_with_markup + labor_total + shop_supply_fee

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
            layout += f"  - Labor ({labor_hours} hrs @ $100):  ${labor_total:.2f}\n"
            layout += f"  - Shop Supplies (10%):  +${shop_supply_fee:.2f}\n"
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

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()