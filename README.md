# Quick Quote Professional

A professional quote generation application built with Python and Tkinter, designed for small businesses requiring efficient quoting capabilities.

## 🎯 Key Features

### Data Persistence
- **SQLite Local Database**: All quotes are stored locally using SQLite for reliable data persistence without external dependencies
- **Settings Management**: Configurable shop rates, taxes, and company information saved in database
- **Data Export Options**: CSV export functionality for historical quote management

### Intelligent Pricing Engine
- **Tiered Parts Markup Automation**: 
  - Parts ≤ $50: 50% markup
  - Parts $51-$200: 30% markup  
  - Parts > $200: 15% markup
- **Dynamic Rate Configuration**: Adjustable labor rates, supply fees, and tax settings

### Professional Output Generation
- **PDF Export**: High-quality PDF generation using ReportLab with professional formatting
- **Print-Optimized HTML**: Browser-based printing with clean styling that removes browser artifacts
- **Real-time Preview**: Instant quote preview during calculation process

## 🛠️ Technical Architecture

### Core Components
- **GUI Framework**: Tkinter for cross-platform desktop application
- **Database Layer**: SQLite3 for local data storage and retrieval
- **PDF Rendering**: ReportLab library for professional document generation
- **Print Styling**: Custom CSS with print-specific media queries

### Design Features
- Modern Material-inspired UI with custom styling
- Responsive layout that adapts to different screen sizes
- Intuitive workflow: Input → Calculate → Save/Export
- Comprehensive error handling and user feedback

## 📊 Sample Output

The application generates professional invoice-style quotes with:
- Company branding and contact information
- Detailed cost breakdown (parts, labor, supplies)
- Tax calculations based on configurable rates
- Disposal fee inclusion when applicable
- Validity period disclaimer

## 🔧 Installation & Usage

### Prerequisites
- Python 3.10 or higher
- ReportLab library for PDF generation

### Installation Steps
1. Clone the repository: `git clone <repository-url>`
2. Install dependencies: `pip install reportlab`
3. Run the application: `python quick_quote_pro.py`

## 📋 Usage Workflow

1. **Configure Shop Settings**:
   - Open the application
   - Go to "Settings" → "Configure Shop Rates & Info"
   - Enter your shop's labor rate, supply fee percentage, tax rate, and disposal fee
   - Set company information (name, address, phone, email)
   - Click "Save Settings"

2. **Generate a Quote**:
   - Enter customer name in the input field
   - Input raw parts cost ($)
   - Enter labor hours required
   - Click "Calculate Quote" to see real-time preview

3. **Export or Save Quote**:
   - Click "Save to Database" to store quote locally
   - Click "Save to PDF" to generate a professional PDF document
   - Click "Print Quote" for browser-based printing

4. **Manage Quotes**:
   - View saved quotes via "Database" → "View Saved Quotes"
   - Export historical data as CSV using "Database" → "Export History to CSV"

