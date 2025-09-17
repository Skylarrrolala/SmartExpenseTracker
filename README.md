# Smart Expense Tracker

A comprehensive expense tracking application with OCR receipt processing and Streamlit UI integration.

## Features

- **📝 Manual Expense Entry**: Add expenses manually with detailed categorization
- **📷 Receipt OCR Processing**: Extract expense details from receipt images using pytesseract
- **💾 Flexible Storage**: Support for both CSV and JSON data formats
- **🏷️ Smart Categorization**: AI-powered category suggestions based on vendor names
- **📊 Analytics Dashboard**: Comprehensive expense analytics and visualizations
- **🖥️ Streamlit Integration**: Ready-to-use web interface for easy expense management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Skylarrrolala/SmartExpenseTracker.git
cd SmartExpenseTracker
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Install tesseract OCR engine (for receipt processing):
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
```

## Quick Start

### Using the Python Module

```python
from expense_tracker import ExpenseTracker, ReceiptOCR

# Create expense tracker
tracker = ExpenseTracker("my_expenses.csv", "csv")

# Add expenses manually
tracker.add_expense(25.50, "Food & Dining", "Starbucks", "Morning coffee")
tracker.add_expense(45.99, "Groceries", "Walmart", "Weekly groceries")

# View expenses
expenses = tracker.view_expenses()
total = tracker.total_expenses()

# Process receipt images
ocr = ReceiptOCR()
receipt_info = ocr.process_receipt("receipt.jpg")
```

### Using the Streamlit Web Interface

```bash
streamlit run streamlit_demo.py
```

Then open your browser to `http://localhost:8501` to use the web interface.

## Module Overview

### ExpenseTracker Class

Main class for expense management:

- `add_expense(amount, category, vendor, description, date)` - Add a new expense
- `view_expenses(category, start_date, end_date)` - View filtered expenses
- `total_expenses(category, start_date, end_date)` - Calculate total expenses
- `get_expenses_by_category()` - Get expenses grouped by category
- `get_expense_summary()` - Get comprehensive expense summary

### ReceiptOCR Class

OCR processing for receipt images:

- `extract_text_from_receipt(image_path)` - Extract text using OCR
- `parse_amount(text)` - Parse monetary amount from text
- `parse_date(text)` - Parse date from text
- `parse_vendor(text)` - Extract vendor name from text
- `suggest_category(vendor)` - Suggest expense category based on vendor
- `process_receipt(image_path)` - Complete receipt processing

### Supported Categories

- Food & Dining
- Transportation
- Shopping
- Entertainment
- Bills & Utilities
- Healthcare
- Travel
- Education
- Business
- Personal Care
- Groceries
- Gas
- Other

## Storage Formats

### CSV Format
```csv
date,amount,category,vendor,description
2025-09-17,25.50,Food & Dining,Starbucks,Morning coffee
```

### JSON Format
```json
[
  {
    "date": "2025-09-17",
    "amount": 25.50,
    "category": "Food & Dining",
    "vendor": "Starbucks",
    "description": "Morning coffee"
  }
]
```

## API Reference

### Creating an Expense Tracker

```python
# CSV storage
tracker = ExpenseTracker("expenses.csv", "csv")

# JSON storage
tracker = ExpenseTracker("expenses.json", "json")

# Using convenience function
tracker = create_expense_tracker("expenses.csv", "csv")
```

### Adding Expenses

```python
# Manual entry
expense = tracker.add_expense(
    amount=25.50,
    category="Food & Dining",
    vendor="Starbucks",
    description="Morning coffee",
    date="2025-09-17"  # Optional, defaults to today
)

# From receipt with user confirmation
def confirm_category(suggested):
    return input(f"Suggested category: {suggested}. Confirm? (y/n): ")

result = add_expense_from_receipt(
    tracker, 
    "receipt.jpg", 
    user_confirmation_callback=confirm_category
)
```

### Viewing and Filtering Expenses

```python
# All expenses
all_expenses = tracker.view_expenses()

# Filter by category
food_expenses = tracker.view_expenses(category="Food & Dining")

# Filter by date range
recent_expenses = tracker.view_expenses(
    start_date="2025-09-01",
    end_date="2025-09-17"
)

# Combined filters
filtered = tracker.view_expenses(
    category="Food & Dining",
    start_date="2025-09-01",
    end_date="2025-09-17"
)
```

### OCR Processing

```python
ocr = ReceiptOCR()

# Process receipt image
receipt_info = ocr.process_receipt("receipt.jpg")
print(f"Amount: ${receipt_info['amount']}")
print(f"Vendor: {receipt_info['vendor']}")
print(f"Category: {receipt_info['suggested_category']}")
print(f"Date: {receipt_info['date']}")
```

## Error Handling

The module includes comprehensive error handling:

```python
try:
    tracker.add_expense(-10, "Food", "Test")  # Negative amount
except ValueError as e:
    print(f"Error: {e}")  # "Amount cannot be negative"

try:
    tracker.add_expense(10, "InvalidCategory", "Test")
except ValueError as e:
    print(f"Error: {e}")  # "Invalid category"
```

## Testing

Run the test suite:

```bash
python test_expense_tracker.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.
