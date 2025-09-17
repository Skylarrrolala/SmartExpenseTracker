"""
Smart Expense Tracker Module

A comprehensive expense tracking system with OCR receipt processing capabilities.
This module provides functions for adding, viewing, and totaling expenses,
with support for both CSV and JSON storage formats.

Features:
- Add, view, and calculate expenses
- OCR receipt parsing with pytesseract
- Smart category suggestions
- CSV and JSON storage options
- Streamlit UI integration ready

Author: Smart Expense Tracker
"""

import csv
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
from PIL import Image
import pytesseract

# Configuration
DEFAULT_DATA_FILE = "expenses.csv"
DEFAULT_JSON_FILE = "expenses.json"
EXPENSE_CATEGORIES = [
    "Food & Dining", "Transportation", "Shopping", "Entertainment", 
    "Bills & Utilities", "Healthcare", "Travel", "Education", 
    "Business", "Personal Care", "Groceries", "Gas", "Other"
]


class ExpenseTracker:
    """
    Main class for expense tracking functionality.
    
    This class handles all expense operations including adding, viewing,
    totaling expenses, and OCR processing of receipts.
    """
    
    def __init__(self, data_file: str = DEFAULT_DATA_FILE, storage_format: str = "csv"):
        """
        Initialize the ExpenseTracker.
        
        Args:
            data_file (str): Path to the data file
            storage_format (str): Storage format - "csv" or "json"
        """
        self.data_file = data_file
        self.storage_format = storage_format.lower()
        self.expenses = []
        self._load_expenses()
    
    def _load_expenses(self) -> None:
        """Load existing expenses from the data file."""
        if not os.path.exists(self.data_file):
            self.expenses = []
            return
            
        try:
            if self.storage_format == "csv":
                self._load_from_csv()
            elif self.storage_format == "json":
                self._load_from_json()
            else:
                raise ValueError(f"Unsupported storage format: {self.storage_format}")
        except Exception as e:
            print(f"Error loading expenses: {e}")
            self.expenses = []
    
    def _load_from_csv(self) -> None:
        """Load expenses from CSV file."""
        self.expenses = []
        with open(self.data_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert amount to float and ensure proper data types
                row['amount'] = float(row['amount'])
                self.expenses.append(row)
    
    def _load_from_json(self) -> None:
        """Load expenses from JSON file."""
        with open(self.data_file, 'r', encoding='utf-8') as file:
            self.expenses = json.load(file)
    
    def _save_expenses(self) -> None:
        """Save expenses to the data file."""
        try:
            if self.storage_format == "csv":
                self._save_to_csv()
            elif self.storage_format == "json":
                self._save_to_json()
        except Exception as e:
            print(f"Error saving expenses: {e}")
    
    def _save_to_csv(self) -> None:
        """Save expenses to CSV file."""
        if not self.expenses:
            return
            
        fieldnames = ['date', 'amount', 'category', 'vendor', 'description']
        with open(self.data_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.expenses)
    
    def _save_to_json(self) -> None:
        """Save expenses to JSON file."""
        with open(self.data_file, 'w', encoding='utf-8') as file:
            json.dump(self.expenses, file, indent=2, ensure_ascii=False)
    
    def add_expense(self, 
                   amount: float, 
                   category: str, 
                   vendor: str = "", 
                   description: str = "", 
                   date: Optional[str] = None) -> Dict:
        """
        Add a new expense to the tracker.
        
        Args:
            amount (float): Expense amount
            category (str): Expense category
            vendor (str): Vendor name (optional)
            description (str): Expense description (optional)
            date (str): Date in YYYY-MM-DD format (optional, defaults to today)
        
        Returns:
            Dict: The added expense record
        
        Raises:
            ValueError: If amount is negative or category is invalid
        """
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        
        if category not in EXPENSE_CATEGORIES:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(EXPENSE_CATEGORIES)}")
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            # Validate date format
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        
        expense = {
            'date': date,
            'amount': amount,
            'category': category,
            'vendor': vendor,
            'description': description
        }
        
        self.expenses.append(expense)
        self._save_expenses()
        
        return expense
    
    def view_expenses(self, 
                     category: Optional[str] = None, 
                     start_date: Optional[str] = None, 
                     end_date: Optional[str] = None) -> List[Dict]:
        """
        View expenses with optional filtering.
        
        Args:
            category (str): Filter by category (optional)
            start_date (str): Start date in YYYY-MM-DD format (optional)
            end_date (str): End date in YYYY-MM-DD format (optional)
        
        Returns:
            List[Dict]: List of expense records matching the criteria
        """
        filtered_expenses = self.expenses.copy()
        
        # Filter by category
        if category:
            if category not in EXPENSE_CATEGORIES:
                raise ValueError(f"Invalid category. Must be one of: {', '.join(EXPENSE_CATEGORIES)}")
            filtered_expenses = [exp for exp in filtered_expenses if exp['category'] == category]
        
        # Filter by date range
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                filtered_expenses = [exp for exp in filtered_expenses 
                                   if datetime.strptime(exp['date'], "%Y-%m-%d") >= start_dt]
            except ValueError:
                raise ValueError("start_date must be in YYYY-MM-DD format")
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                filtered_expenses = [exp for exp in filtered_expenses 
                                   if datetime.strptime(exp['date'], "%Y-%m-%d") <= end_dt]
            except ValueError:
                raise ValueError("end_date must be in YYYY-MM-DD format")
        
        return filtered_expenses
    
    def total_expenses(self, 
                      category: Optional[str] = None, 
                      start_date: Optional[str] = None, 
                      end_date: Optional[str] = None) -> float:
        """
        Calculate total expenses with optional filtering.
        
        Args:
            category (str): Filter by category (optional)
            start_date (str): Start date in YYYY-MM-DD format (optional)
            end_date (str): End date in YYYY-MM-DD format (optional)
        
        Returns:
            float: Total amount of filtered expenses
        """
        filtered_expenses = self.view_expenses(category, start_date, end_date)
        return sum(expense['amount'] for expense in filtered_expenses)
    
    def get_expenses_by_category(self) -> Dict[str, float]:
        """
        Get expenses grouped by category.
        
        Returns:
            Dict[str, float]: Dictionary with categories as keys and totals as values
        """
        category_totals = {}
        for expense in self.expenses:
            category = expense['category']
            category_totals[category] = category_totals.get(category, 0) + expense['amount']
        return category_totals
    
    def get_expense_summary(self) -> Dict:
        """
        Get a comprehensive expense summary.
        
        Returns:
            Dict: Summary including total, count, categories, and date range
        """
        if not self.expenses:
            return {
                'total_amount': 0,
                'expense_count': 0,
                'categories': {},
                'date_range': {'start': None, 'end': None}
            }
        
        dates = [exp['date'] for exp in self.expenses]
        
        return {
            'total_amount': sum(exp['amount'] for exp in self.expenses),
            'expense_count': len(self.expenses),
            'categories': self.get_expenses_by_category(),
            'date_range': {
                'start': min(dates),
                'end': max(dates)
            }
        }


class ReceiptOCR:
    """
    OCR processing class for receipt image analysis.
    
    This class handles the extraction of expense information from receipt images
    using pytesseract OCR technology.
    """
    
    def __init__(self):
        """Initialize the ReceiptOCR processor."""
        self.vendor_categories = self._load_vendor_categories()
    
    def _load_vendor_categories(self) -> Dict[str, str]:
        """
        Load vendor-to-category mappings.
        
        Returns:
            Dict[str, str]: Mapping of vendor patterns to categories
        """
        return {
            # Food & Dining
            'mcdonalds': 'Food & Dining',
            'burger king': 'Food & Dining',
            'starbucks': 'Food & Dining',
            'subway': 'Food & Dining',
            'pizza': 'Food & Dining',
            'restaurant': 'Food & Dining',
            'cafe': 'Food & Dining',
            'diner': 'Food & Dining',
            
            # Groceries
            'walmart': 'Groceries',
            'target': 'Groceries',
            'kroger': 'Groceries',
            'safeway': 'Groceries',
            'grocery': 'Groceries',
            'supermarket': 'Groceries',
            'market': 'Groceries',
            
            # Gas
            'shell': 'Gas',
            'exxon': 'Gas',
            'chevron': 'Gas',
            'bp': 'Gas',
            'gas station': 'Gas',
            'fuel': 'Gas',
            
            # Transportation
            'uber': 'Transportation',
            'lyft': 'Transportation',
            'taxi': 'Transportation',
            'bus': 'Transportation',
            'metro': 'Transportation',
            'transit': 'Transportation',
            
            # Shopping
            'amazon': 'Shopping',
            'ebay': 'Shopping',
            'best buy': 'Shopping',
            'costco': 'Shopping',
            'mall': 'Shopping',
            'store': 'Shopping',
            
            # Healthcare
            'pharmacy': 'Healthcare',
            'cvs': 'Healthcare',
            'walgreens': 'Healthcare',
            'clinic': 'Healthcare',
            'hospital': 'Healthcare',
            'doctor': 'Healthcare',
            
            # Default fallback
            'other': 'Other'
        }
    
    def preprocess_image(self, image_path: str) -> Image.Image:
        """
        Preprocess image for better OCR results.
        
        Args:
            image_path (str): Path to the receipt image
        
        Returns:
            PIL.Image: Preprocessed image
        """
        try:
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # You can add more preprocessing steps here like:
            # - Resize for better OCR
            # - Enhance contrast
            # - Noise reduction
            
            return image
        except Exception as e:
            raise ValueError(f"Error preprocessing image: {e}")
    
    def extract_text_from_receipt(self, image_path: str) -> str:
        """
        Extract text from receipt image using OCR.
        
        Args:
            image_path (str): Path to the receipt image
        
        Returns:
            str: Extracted text from the receipt
        
        Raises:
            ValueError: If image cannot be processed
        """
        try:
            image = self.preprocess_image(image_path)
            
            # Configure tesseract for better receipt reading
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, config=custom_config)
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error extracting text from receipt: {e}")
    
    def parse_amount(self, text: str) -> Optional[float]:
        """
        Extract monetary amount from receipt text.
        
        Args:
            text (str): Receipt text
        
        Returns:
            Optional[float]: Extracted amount or None if not found
        """
        # Common patterns for monetary amounts
        patterns = [
            r'total\s*:?\s*\$?(\d+\.?\d*)',
            r'amount\s*:?\s*\$?(\d+\.?\d*)',
            r'subtotal\s*:?\s*\$?(\d+\.?\d*)',
            r'\$(\d+\.?\d*)',
            r'(\d+\.\d{2})\s*$',  # Amount at end of line
        ]
        
        text_lower = text.lower()
        amounts = []
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.MULTILINE)
            for match in matches:
                try:
                    amount = float(match)
                    if 0.01 <= amount <= 10000:  # Reasonable amount range
                        amounts.append(amount)
                except ValueError:
                    continue
        
        # Return the largest reasonable amount (likely the total)
        return max(amounts) if amounts else None
    
    def parse_date(self, text: str) -> Optional[str]:
        """
        Extract date from receipt text.
        
        Args:
            text (str): Receipt text
        
        Returns:
            Optional[str]: Extracted date in YYYY-MM-DD format or None if not found
        """
        # Common date patterns
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
            r'(\w{3,9})\s+(\d{1,2}),?\s+(\d{2,4})',  # Month Day, Year
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    if len(match) == 3:
                        # Try different date formats
                        if match[0].isalpha():  # Month name
                            date_str = f"{match[1]} {match[0]} {match[2]}"
                            date_obj = datetime.strptime(date_str, "%d %B %Y")
                        elif len(match[2]) == 4:  # YYYY
                            if len(match[0]) == 4:  # YYYY-MM-DD
                                date_obj = datetime(int(match[0]), int(match[1]), int(match[2]))
                            else:  # MM/DD/YYYY
                                date_obj = datetime(int(match[2]), int(match[0]), int(match[1]))
                        else:  # YY
                            year = int(match[2])
                            if year < 50:
                                year += 2000
                            else:
                                year += 1900
                            date_obj = datetime(year, int(match[0]), int(match[1]))
                        
                        return date_obj.strftime("%Y-%m-%d")
                except (ValueError, IndexError):
                    continue
        
        # If no date found, return today's date
        return datetime.now().strftime("%Y-%m-%d")
    
    def parse_vendor(self, text: str) -> str:
        """
        Extract vendor name from receipt text.
        
        Args:
            text (str): Receipt text
        
        Returns:
            str: Extracted vendor name
        """
        lines = text.split('\n')
        
        # Usually vendor name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 2 and not re.match(r'^\d+.*', line):
                # Filter out lines that look like addresses or phone numbers
                if not re.search(r'\d{3}-\d{3}-\d{4}|\d{10}', line):
                    return line.title()
        
        return "Unknown Vendor"
    
    def suggest_category(self, vendor: str) -> str:
        """
        Suggest expense category based on vendor name.
        
        Args:
            vendor (str): Vendor name
        
        Returns:
            str: Suggested category
        """
        vendor_lower = vendor.lower()
        
        for keyword, category in self.vendor_categories.items():
            if keyword in vendor_lower:
                return category
        
        return "Other"
    
    def process_receipt(self, image_path: str, user_confirmation: bool = True) -> Dict:
        """
        Process a receipt image and extract expense information.
        
        Args:
            image_path (str): Path to the receipt image
            user_confirmation (bool): Whether to ask for user confirmation on category
        
        Returns:
            Dict: Extracted expense information
        
        Raises:
            ValueError: If image cannot be processed
        """
        if not os.path.exists(image_path):
            raise ValueError(f"Image file not found: {image_path}")
        
        # Extract text from receipt
        text = self.extract_text_from_receipt(image_path)
        
        # Parse information
        amount = self.parse_amount(text)
        date = self.parse_date(text)
        vendor = self.parse_vendor(text)
        suggested_category = self.suggest_category(vendor)
        
        result = {
            'amount': amount,
            'date': date,
            'vendor': vendor,
            'suggested_category': suggested_category,
            'extracted_text': text,
            'needs_review': amount is None or vendor == "Unknown Vendor"
        }
        
        return result


# Convenience functions for Streamlit integration
def create_expense_tracker(data_file: str = DEFAULT_DATA_FILE, 
                          storage_format: str = "csv") -> ExpenseTracker:
    """
    Create and return an ExpenseTracker instance.
    
    Args:
        data_file (str): Path to the data file
        storage_format (str): Storage format - "csv" or "json"
    
    Returns:
        ExpenseTracker: Configured expense tracker instance
    """
    return ExpenseTracker(data_file, storage_format)


def create_receipt_ocr() -> ReceiptOCR:
    """
    Create and return a ReceiptOCR instance.
    
    Returns:
        ReceiptOCR: Configured OCR processor instance
    """
    return ReceiptOCR()


def add_expense_from_receipt(tracker: ExpenseTracker, 
                           image_path: str, 
                           user_confirmation_callback=None) -> Dict:
    """
    Add an expense from a receipt image with optional user confirmation.
    
    Args:
        tracker (ExpenseTracker): The expense tracker instance
        image_path (str): Path to the receipt image
        user_confirmation_callback: Function to call for user confirmation
    
    Returns:
        Dict: The processed receipt information and added expense
    """
    ocr = ReceiptOCR()
    receipt_info = ocr.process_receipt(image_path)
    
    if receipt_info['amount'] is None:
        raise ValueError("Could not extract amount from receipt. Please add manually.")
    
    # Use callback for user confirmation if provided
    final_category = receipt_info['suggested_category']
    if user_confirmation_callback and callable(user_confirmation_callback):
        final_category = user_confirmation_callback(receipt_info['suggested_category'])
    
    # Add the expense
    expense = tracker.add_expense(
        amount=receipt_info['amount'],
        category=final_category,
        vendor=receipt_info['vendor'],
        description=f"Receipt processed: {os.path.basename(image_path)}",
        date=receipt_info['date']
    )
    
    return {
        'receipt_info': receipt_info,
        'added_expense': expense
    }


if __name__ == "__main__":
    # Example usage for testing
    print("Smart Expense Tracker Module")
    print("=" * 40)
    
    # Create tracker instance
    tracker = ExpenseTracker("test_expenses.csv", "csv")
    
    # Add sample expenses
    tracker.add_expense(25.50, "Food & Dining", "Starbucks", "Morning coffee")
    tracker.add_expense(45.99, "Groceries", "Walmart", "Weekly groceries")
    tracker.add_expense(12.75, "Transportation", "Uber", "Ride to airport")
    
    # View expenses
    print("\nAll Expenses:")
    for expense in tracker.view_expenses():
        print(f"  {expense['date']}: ${expense['amount']:.2f} - {expense['category']} - {expense['vendor']}")
    
    # Get totals
    print(f"\nTotal Expenses: ${tracker.total_expenses():.2f}")
    
    # Category breakdown
    print("\nExpenses by Category:")
    for category, total in tracker.get_expenses_by_category().items():
        print(f"  {category}: ${total:.2f}")
    
    print("\nModule loaded successfully!")