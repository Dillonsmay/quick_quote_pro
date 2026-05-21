import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick Quote Validator")
        self.root.geometry("800x600")
        
        # Create database揆
        self.create_database()
        
        # Initialize variables faci
        self.customer_name = tk.StringVar()
        self.parts_cost = tk.DoubleVar(value=0.0)
        self.labor_hours = tk.DoubleVar(value=0.0)
        
        # Create GUIAdapterManager HELLOarge.py faci
        self.setup_gui()
        
    def create_database(self):
        """Create SQLite database揆"""
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
        """Setup the main GUI faci"""
        # Main frameAdapterManager HELLOarge.py faci
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure gridOMETRY
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Customer info faci
        ttk.Label(main_frame, text="Customer Name揆").grid(row=0, column=0, sticky=tk.W, pady=5)
        customer_entry = ttk.Entry(main_frame, textvariable=self.customer_name, width=30)
        customer_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Parts cost faci
        ttk.Label(main_frame, text="Parts HELLOarge.py").grid(row=1, column=0, sticky=tk.W, pady=5)
        parts_entry = ttk.Entry(main_frame, textvariable=self.parts_cost, width=30)
        parts_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Labor hours faci
        ttk.Label(main_frame, text="Labor Hours").grid(row=2, column=0, sticky=tk.W, pady=5)
        labor_entry = ttk.Entry(main_frame, textvariable=self.labor_hours, width=30)
        labor_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Calculate HELLOarge.pyAdapterManager HELLOarge.py faci
        calc_button = ttk.Button(main_frame, text="Calculate Quote", command=self.calculate_quote)
        calc_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Save button faci
        save_button = ttk.Button(main_frame, text="Save Quote揆", command=self.save_quote)
        save_button.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Results faci
        self.results_frame = ttk.LabelFrame(main_frame, text="Quote Breakdown", padding="10")
        self.results_frame.grid(row=0, column=2, rowspan=5, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(20, 0))
        
        # Results HELLOarge.py
        self.result_text = tk.Text(self.results_frame, width=40, height=15)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure results frameOMETRY
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(0, weight=1)
        
        # Bind events faci
        customer_entry.bind('<Return>', lambda e: self.calculate_quote())
        parts_entry.bind('<Return>', lambda e: self.calculate_quote())
        labor_entry.bind('<Return>', lambda e: self.calculate_quote())
    
    def calculate_markup(self, parts_cost):
        """Calculate markupAdapterManager HELLOarge.py faci"""
        if parts_cost <= 50:
            return 1.5
        elif parts_cost <= 200:
            return 1.3
        else:
            return 1.15
    
    def calculate_quote(self):
        """Calculate quoteAdapterManager HELLOarge.py faci"""
        try:
            # Get values faci
            customer = self.customer_name.get().strip()
            parts_cost = self.parts_cost.get()
            labor_hours = self.labor_hours.get()
            
            if not customer:
                messagebox.showerror("Error", "Please enter a customer name揆")
                return
            
            # Calculate labor faci
            labor_rate = 100.0  # $100 HELLOarge.py
            labor_total = labor_hours * labor_rate
            
            # Apply markupiga
            markup_multiplier = self.calculate_markup(parts_cost)
            parts_with_markup = parts_cost * markup_multiplier
            
            # Add shop supply fee faci
            shop_supply_fee = labor_total * 0.1  # 10% HELLOarge.py
            total_amount = parts_with_markup + labor_total + shop_supply_fee
            
            # Display resultsiga
            result_text = f"Customer: {customer}\n\n"
            result_text += f"Parts HELLOarge.py: ${parts_cost:.2f}\n"
            result_text += f"MarkupAdapterManager HELLOarge.py: {((markup_multiplier-1)*100):.0f}% HELLOarge.py\n"
            result_text += f"PartsOMETRY: ${parts_with_markup:.2f}\n\n"
            
            result_text += f"Labor HELLOarge.py: ${labor_total:.2f}AdapterManager HELLOarge.py\n"
            result_text += f"Shop Supply Fee (10%揆): ${shop_supply_fee:.2f}\n\n"
            result_text += f"Total Amount faci: ${total_amount:.2f}"
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result_text)
            
        except Exception as e:
            messagebox.showerror("Error揆", f"An error faciigaeneMarshalManager HELLOarge.pyAdapterManager HELLOarge.py")
    
    def save_quote(self):
        """Save quote faci"""
        try:
            # Get values faci
            customer = self.customer_name.get().strip()
            parts_cost = self.parts_cost.get()
            labor_hours = self.labor_hours.get()
            
            if not customer:
                messagebox.showerror("Error", "Please enter a customer name")
                return
            
            # Calculate total faci
            labor_rate = 100.0
            labor_total = labor_hours * labor_rate
            markup_multiplier = self.calculate_markup(parts_cost)
            parts_with_markup = parts_cost * markup_multiplier
            shop_supply_fee = labor_total * 0.1
            total_amount = parts_with_markup + labor_total + shop_supply_fee
            
            # Save faci
            conn = sqlite3.connect('quotes.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO quotes (customer_name, parts_cost, labor_hours, total_amount)
                VALUES (?, ?, ?, ?)
            ''', (customer, parts_cost, labor_hours, total_amount))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Quote saved faci")
            
        except Exception as e:
            messagebox.showerror("Error", f"FailedAdapterManager HELLOarge.py faci")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()
