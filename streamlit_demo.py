"""
Streamlit Demo App for Smart Expense Tracker

This demo shows how to integrate the expense tracker module with a Streamlit UI.
Run with: streamlit run streamlit_demo.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import tempfile
from expense_tracker import (
    ExpenseTracker, 
    ReceiptOCR, 
    EXPENSE_CATEGORIES,
    add_expense_from_receipt
)

# Page configuration
st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
if 'tracker' not in st.session_state:
    st.session_state.tracker = ExpenseTracker("app_expenses.csv", "csv")

if 'ocr' not in st.session_state:
    st.session_state.ocr = ReceiptOCR()

# Main app
def main():
    st.title("💰 Smart Expense Tracker")
    st.markdown("Track your expenses with ease! Add manually or upload receipt images for automatic processing.")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Add Expense", "Receipt Scanner", "View Expenses", "Analytics"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Add Expense":
        show_add_expense()
    elif page == "Receipt Scanner":
        show_receipt_scanner()
    elif page == "View Expenses":
        show_view_expenses()
    elif page == "Analytics":
        show_analytics()

def show_dashboard():
    """Display the main dashboard with expense overview."""
    st.header("📊 Dashboard")
    
    # Get expense summary
    summary = st.session_state.tracker.get_expense_summary()
    
    if summary['expense_count'] == 0:
        st.info("No expenses recorded yet. Start by adding your first expense!")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Expenses", f"${summary['total_amount']:.2f}")
    
    with col2:
        st.metric("Number of Expenses", summary['expense_count'])
    
    with col3:
        if summary['date_range']['start']:
            st.metric("Date Range", f"{summary['date_range']['start']} to {summary['date_range']['end']}")
    
    with col4:
        avg_expense = summary['total_amount'] / summary['expense_count']
        st.metric("Average Expense", f"${avg_expense:.2f}")
    
    # Category breakdown chart
    if summary['categories']:
        st.subheader("💳 Expenses by Category")
        
        # Create pie chart
        fig = px.pie(
            values=list(summary['categories'].values()),
            names=list(summary['categories'].keys()),
            title="Expense Distribution by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent expenses
    st.subheader("📝 Recent Expenses")
    recent_expenses = st.session_state.tracker.view_expenses()[-5:]  # Last 5 expenses
    
    if recent_expenses:
        df = pd.DataFrame(recent_expenses)
        df['amount'] = df['amount'].apply(lambda x: f"${x:.2f}")
        st.dataframe(df, use_container_width=True)

def show_add_expense():
    """Show the manual expense addition form."""
    st.header("➕ Add New Expense")
    
    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
            category = st.selectbox("Category", EXPENSE_CATEGORIES)
            vendor = st.text_input("Vendor (optional)")
        
        with col2:
            description = st.text_area("Description (optional)")
            date = st.date_input("Date", value=datetime.now())
        
        submit = st.form_submit_button("Add Expense", type="primary")
        
        if submit:
            try:
                expense = st.session_state.tracker.add_expense(
                    amount=float(amount),
                    category=category,
                    vendor=vendor,
                    description=description,
                    date=date.strftime("%Y-%m-%d")
                )
                st.success(f"✅ Added expense: ${amount:.2f} for {category}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error adding expense: {e}")

def show_receipt_scanner():
    """Show the receipt scanning functionality."""
    st.header("📷 Receipt Scanner")
    st.markdown("Upload a receipt image and let AI extract the expense details!")
    
    uploaded_file = st.file_uploader(
        "Choose a receipt image",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear image of your receipt"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(uploaded_file, caption="Uploaded Receipt", use_container_width=True)
        
        with col2:
            with st.spinner("Processing receipt..."):
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Process receipt
                    receipt_info = st.session_state.ocr.process_receipt(tmp_path)
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
                    
                    # Display extracted information
                    st.subheader("🔍 Extracted Information")
                    
                    if receipt_info['needs_review']:
                        st.warning("⚠️ Some information may need review")
                    
                    # Editable form with extracted data
                    with st.form("receipt_expense_form"):
                        amount = st.number_input(
                            "Amount ($)", 
                            value=receipt_info['amount'] if receipt_info['amount'] else 0.0,
                            min_value=0.01, 
                            step=0.01
                        )
                        
                        suggested_category = receipt_info['suggested_category']
                        category_index = EXPENSE_CATEGORIES.index(suggested_category) if suggested_category in EXPENSE_CATEGORIES else 0
                        category = st.selectbox(
                            "Category", 
                            EXPENSE_CATEGORIES,
                            index=category_index
                        )
                        
                        vendor = st.text_input(
                            "Vendor", 
                            value=receipt_info['vendor'] if receipt_info['vendor'] else ""
                        )
                        
                        date = st.date_input(
                            "Date", 
                            value=datetime.strptime(receipt_info['date'], "%Y-%m-%d") if receipt_info['date'] else datetime.now()
                        )
                        
                        description = st.text_input(
                            "Description", 
                            value=f"Receipt scan: {uploaded_file.name}"
                        )
                        
                        if st.form_submit_button("Add Expense from Receipt", type="primary"):
                            try:
                                expense = st.session_state.tracker.add_expense(
                                    amount=float(amount),
                                    category=category,
                                    vendor=vendor,
                                    description=description,
                                    date=date.strftime("%Y-%m-%d")
                                )
                                st.success(f"✅ Added expense from receipt: ${amount:.2f} for {category}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error adding expense: {e}")
                    
                    # Show extracted text for debugging
                    with st.expander("🔍 Raw Extracted Text"):
                        st.text(receipt_info['extracted_text'])
                
                except Exception as e:
                    st.error(f"❌ Error processing receipt: {e}")

def show_view_expenses():
    """Show expense viewing and filtering options."""
    st.header("📋 View Expenses")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + EXPENSE_CATEGORIES
        )
    
    with col2:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30)
        )
    
    with col3:
        end_date = st.date_input(
            "End Date",
            value=datetime.now()
        )
    
    # Get filtered expenses
    try:
        category = category_filter if category_filter != "All" else None
        expenses = st.session_state.tracker.view_expenses(
            category=category,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        
        if expenses:
            # Display summary
            total = sum(exp['amount'] for exp in expenses)
            st.metric("Total for Selected Period", f"${total:.2f}")
            
            # Display expenses table
            df = pd.DataFrame(expenses)
            df['amount'] = df['amount'].apply(lambda x: f"${x:.2f}")
            
            # Format the table
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "date": "Date",
                    "amount": "Amount",
                    "category": "Category",
                    "vendor": "Vendor",
                    "description": "Description"
                }
            )
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"expenses_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )
        else:
            st.info("No expenses found for the selected criteria.")
            
    except Exception as e:
        st.error(f"❌ Error filtering expenses: {e}")

def show_analytics():
    """Show expense analytics and charts."""
    st.header("📈 Analytics")
    
    expenses = st.session_state.tracker.view_expenses()
    
    if not expenses:
        st.info("No expenses to analyze yet. Add some expenses first!")
        return
    
    df = pd.DataFrame(expenses)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    
    # Monthly spending trend
    st.subheader("📅 Monthly Spending Trend")
    monthly_spending = df.groupby('month')['amount'].sum().reset_index()
    monthly_spending['month'] = monthly_spending['month'].astype(str)
    
    fig_trend = px.line(
        monthly_spending, 
        x='month', 
        y='amount',
        title="Monthly Spending Trend",
        labels={'amount': 'Amount ($)', 'month': 'Month'}
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Category analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💳 Spending by Category")
        category_spending = df.groupby('category')['amount'].sum().reset_index()
        
        fig_category = px.bar(
            category_spending,
            x='category',
            y='amount',
            title="Total Spending by Category",
            labels={'amount': 'Amount ($)', 'category': 'Category'}
        )
        fig_category.update_xaxis(tickangle=45)
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        st.subheader("🏪 Top Vendors")
        vendor_spending = df.groupby('vendor')['amount'].sum().sort_values(ascending=False).head(10)
        
        if not vendor_spending.empty:
            fig_vendor = px.bar(
                x=vendor_spending.values,
                y=vendor_spending.index,
                orientation='h',
                title="Top 10 Vendors by Spending",
                labels={'x': 'Amount ($)', 'y': 'Vendor'}
            )
            st.plotly_chart(fig_vendor, use_container_width=True)
    
    # Time-based analysis
    st.subheader("📊 Expense Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_daily = df.groupby(df['date'].dt.date)['amount'].sum().mean()
        st.metric("Average Daily Spending", f"${avg_daily:.2f}")
    
    with col2:
        max_expense = df['amount'].max()
        st.metric("Largest Single Expense", f"${max_expense:.2f}")
    
    with col3:
        most_frequent_category = df['category'].value_counts().index[0]
        st.metric("Most Frequent Category", most_frequent_category)

if __name__ == "__main__":
    main()