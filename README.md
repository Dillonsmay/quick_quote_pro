# Quick Quote Professional v1.2

**A Premium Desktop Application for Small Business Quote Generation**

Transform your quoting workflow with Quick Quote Professional – a powerful desktop application designed specifically for small businesses that demand precision, efficiency, and professional output. Built with Python and Tkinter, this solution combines modern UI design with robust functionality to streamline your quote creation process.

## 🚀 Key Features

### 💰 Intelligent Tiered Markup Engine
- **Dynamic Pricing Algorithm**: Automatically applies tier-based markup percentages based on part costs:
  - Parts ≤ $50: 50% markup (1.5x pricing)
  - Parts $51-$200: 30% markup (1.3x pricing)  
  - Parts > $200: 15% markup (1.15x pricing)
- **Fully Configurable**: Adjust markup tiers and thresholds to match your business model
- **Real-time Calculation**: Instant preview of pricing changes as you input data

### 📊 Interactive Itemized Parts Table
- **Drag-and-drop Ready Interface**: Add, remove, or modify parts with intuitive controls
- **Live Preview Updates**: See real-time calculations as you add components
- **Professional Formatting**: Clean display of part descriptions and costs in a structured layout

### 🔧 SQLite Data Persistence
- **Local Database Storage**: All quotes stored securely in SQLite for reliable data persistence
- **Comprehensive History Management**: View, export, or purge saved quotes with ease
- **Settings Preservation**: Shop rates, taxes, and company information persist across sessions

### 📄 Professional PDF Generation
- **High-Quality Output**: Generate polished invoices using ReportLab library
- **Customizable Templates**: Includes professional headers, signatures, and validity periods
- **Print-Optimized Design**: Ready-to-print documents with clean formatting

## ⚙️ Technical Architecture

### Core Technologies
- **GUI Framework**: Modern Tkinter interface with Material-inspired design
- **Database Layer**: SQLite3 for local data storage and retrieval
- **PDF Rendering**: ReportLab library for professional document generation
- **Print Styling**: Custom CSS with print-specific media queries

### Design Features
- Cross-platform compatibility (Windows, macOS, Linux)
- Responsive layout that adapts to different screen sizes
- Intuitive workflow: Input → Calculate → Save/Export
- Comprehensive error handling and user feedback

## 📋 Installation & Usage

### Prerequisites
- Python 3.10 or higher
- ReportLab library for PDF generation

### Installation Steps
1. Clone the repository: `git clone <repository-url>`
2. Install dependencies: `pip install reportlab`
3. Run the application: `python quick_quote_pro.py`

## 🎯 Usage Workflow

### 1. Configure Shop Settings
- Open the application
- Go to "Settings" → "Configure Shop Rates & Info"
- Enter your shop's labor rate, supply fee percentage, tax rate, and disposal fee
- Set company information (name, address, phone, email)
- Click "Save Settings"

### 2. Generate a Quote
- Enter customer name in the input field
- Input raw parts cost ($)
- Enter labor hours required
- Add itemized parts using the interactive table
- Click "Calculate Quote" to see real-time preview

### 3. Export or Save Quote
- Click "Save to Database" to store quote locally
- Click "Save to PDF" to generate a professional PDF document
- Click "Print Quote" for browser-based printing

### 4. Manage Quotes
- View saved quotes via "Database" → "View Saved Quotes"
- Export historical data as CSV using "Database" → "Export History to CSV"

## 🎨 Professional Output Sample

The application generates polished invoice-style quotes with:
- Company branding and contact information
- Detailed cost breakdown (parts, labor, supplies)
- Tax calculations based on configurable rates
- Disposal fee inclusion when applicable
- Validity period disclaimer

## 💼 Perfect For:

- Small repair shops requiring precise quoting
- Service businesses needing professional invoices
- Contractors wanting efficient quote generation tools
- Any business that values data persistence and print-ready documents

---

**Ready to streamline your quoting process? Download Quick Quote Professional today and transform how you create professional quotes.**

*Built with Python, Tkinter, and SQLite for maximum reliability and performance.*
