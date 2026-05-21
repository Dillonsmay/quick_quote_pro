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
