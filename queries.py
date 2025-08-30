#!/usr/bin/env python3
"""
Orders Analytics - Query Engine
This script runs analytics queries on the orders database and generates reports.
"""

import sqlite3
import csv
import os
from datetime import datetime

def ensure_reports_directory():
    """Ensure the reports directory exists."""
    if not os.path.exists('reports'):
        os.makedirs('reports')
        print("✓ Created reports directory")

def connect_to_database():
    """Connect to the orders database."""
    if not os.path.exists('orders.db'):
        print("❌ Error: orders.db not found! Please run 'python load_db.py' first.")
        return None
    
    try:
        conn = sqlite3.connect('orders.db')
        print("✓ Connected to orders.db")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def generate_daily_revenue_report(conn):
    """Generate daily revenue report."""
    print("📊 Generating daily revenue report...")
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            order_date,
            COUNT(*) as order_count,
            SUM(unit_price * quantity) as total_revenue,
            AVG(unit_price * quantity) as avg_order_value
        FROM orders 
        GROUP BY order_date 
        ORDER BY order_date
    ''')
    
    results = cursor.fetchall()
    
    # Write to CSV
    with open('reports/daily_revenue.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Order Count', 'Total Revenue', 'Average Order Value'])
        
        for row in results:
            writer.writerow([
                row[0],
                row[1],
                f"{row[2]:.2f}",
                f"{row[3]:.2f}"
            ])
    
    print("✓ Daily revenue report saved to reports/daily_revenue.csv")
    return results

def generate_revenue_by_category_report(conn):
    """Generate revenue by category report."""
    print("📊 Generating revenue by category report...")
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            category,
            COUNT(*) as order_count,
            SUM(unit_price * quantity) as total_revenue,
            AVG(unit_price * quantity) as avg_order_value,
            SUM(quantity) as total_units_sold
        FROM orders 
        GROUP BY category 
        ORDER BY total_revenue DESC
    ''')
    
    results = cursor.fetchall()
    
    # Write to CSV
    with open('reports/revenue_by_category.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Category', 'Order Count', 'Total Revenue', 'Average Order Value', 'Units Sold'])
        
        for row in results:
            writer.writerow([
                row[0],
                row[1],
                f"{row[2]:.2f}",
                f"{row[3]:.2f}",
                row[4]
            ])
    
    print("✓ Revenue by category report saved to reports/revenue_by_category.csv")
    return results

def generate_top_products_report(conn):
    """Generate top products report."""
    print("📊 Generating top products report...")
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            product,
            category,
            COUNT(*) as times_ordered,
            SUM(quantity) as total_units_sold,
            SUM(unit_price * quantity) as total_revenue,
            AVG(unit_price) as avg_unit_price
        FROM orders 
        GROUP BY product, category
        ORDER BY total_revenue DESC
        LIMIT 20
    ''')
    
    results = cursor.fetchall()
    
    # Write to CSV
    with open('reports/top_products.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Product', 'Category', 'Times Ordered', 'Units Sold', 'Total Revenue', 'Avg Unit Price'])
        
        for row in results:
            writer.writerow([
                row[0],
                row[1],
                row[2],
                row[3],
                f"{row[4]:.2f}",
                f"{row[5]:.2f}"
            ])
    
    print("✓ Top products report saved to reports/top_products.csv")
    return results

def generate_repeat_customers_report(conn):
    """Generate repeat customers report."""
    print("📊 Generating repeat customers report...")
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            customer_id,
            COUNT(*) as order_count,
            SUM(unit_price * quantity) as total_spent,
            AVG(unit_price * quantity) as avg_order_value,
            MIN(order_date) as first_order_date,
            MAX(order_date) as last_order_date,
            COUNT(DISTINCT category) as categories_purchased
        FROM orders 
        GROUP BY customer_id 
        HAVING COUNT(*) > 1
        ORDER BY total_spent DESC
    ''')
    
    results = cursor.fetchall()
    
    # Write to CSV
    with open('reports/repeat_customers.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Customer ID', 'Order Count', 'Total Spent', 'Avg Order Value', 
                        'First Order', 'Last Order', 'Categories Purchased'])
        
        for row in results:
            writer.writerow([
                row[0],
                row[1],
                f"{row[2]:.2f}",
                f"{row[3]:.2f}",
                row[4],
                row[5],
                row[6]
            ])
    
    print("✓ Repeat customers report saved to reports/repeat_customers.csv")
    return results

def generate_summary_report(conn, daily_revenue, category_revenue, top_products, repeat_customers):
    """Generate summary markdown report."""
    print("📊 Generating summary report...")
    
    cursor = conn.cursor()
    
    # Get overall statistics
    cursor.execute('SELECT COUNT(*) FROM orders')
    total_orders = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT customer_id) FROM orders')
    total_customers = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(unit_price * quantity) FROM orders')
    total_revenue = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(unit_price * quantity) FROM orders')
    avg_order_value = cursor.fetchone()[0]
    
    cursor.execute('SELECT MIN(order_date), MAX(order_date) FROM orders')
    date_range = cursor.fetchone()
    
    # Calculate repeat customer rate
    repeat_customer_count = len(repeat_customers)
    repeat_rate = (repeat_customer_count / total_customers) * 100 if total_customers > 0 else 0
    
    # Generate markdown content
    summary_content = f"""# Orders Analytics Summary Report

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

- **Total Orders**: {total_orders:,}
- **Total Customers**: {total_customers:,}
- **Total Revenue**: ${total_revenue:,.2f}
- **Average Order Value**: ${avg_order_value:.2f}
- **Date Range**: {date_range[0]} to {date_range[1]}
- **Repeat Customers**: {repeat_customer_count:,} ({repeat_rate:.1f}% of all customers)

## Top Performing Categories

| Category | Orders | Revenue | Avg Order Value |
|----------|--------|---------|-----------------|
"""
    
    for category_data in category_revenue[:5]:
        summary_content += f"| {category_data[0]} | {category_data[1]:,} | ${category_data[2]:,.2f} | ${category_data[3]:.2f} |\n"
    
    summary_content += f"""
## Top 5 Products by Revenue

| Product | Category | Revenue | Units Sold |
|---------|----------|---------|------------|
"""
    
    for product_data in top_products[:5]:
        summary_content += f"| {product_data[0]} | {product_data[1]} | ${product_data[4]:,.2f} | {product_data[3]:,} |\n"
    
    summary_content += f"""
## Key Insights

### Revenue Trends
- Highest single-day revenue: ${max(day[2] for day in daily_revenue):,.2f}
- Lowest single-day revenue: ${min(day[2] for day in daily_revenue):,.2f}
- Average daily revenue: ${sum(day[2] for day in daily_revenue) / len(daily_revenue):,.2f}

### Customer Behavior
- {repeat_customer_count:,} customers made multiple purchases
- Top repeat customer spent: ${repeat_customers[0][2]:,.2f} across {repeat_customers[0][1]} orders
- Average repeat customer value: ${sum(customer[2] for customer in repeat_customers) / len(repeat_customers):,.2f}

### Product Performance
- Most popular category: {category_revenue[0][0]} ({category_revenue[0][1]:,} orders)
- Best-selling product: {top_products[0][0]} (${top_products[0][4]:,.2f} revenue)

## Files Generated

- `daily_revenue.csv` - Daily revenue breakdown
- `revenue_by_category.csv` - Category performance analysis
- `top_products.csv` - Top 20 products by revenue
- `repeat_customers.csv` - Repeat customer analysis
- `summary.md` - This summary report

---
*Generated by Orders Analytics System*
"""
    
    # Write summary to file
    with open('reports/summary.md', 'w', encoding='utf-8') as file:
        file.write(summary_content)
    
    print("✓ Summary report saved to reports/summary.md")

def main():
    """Main function to run all analytics queries."""
    print("🚀 Orders Analytics - Query Engine")
    print("=" * 40)
    
    # Ensure reports directory exists
    ensure_reports_directory()
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Generate all reports
        daily_revenue = generate_daily_revenue_report(conn)
        category_revenue = generate_revenue_by_category_report(conn)
        top_products = generate_top_products_report(conn)
        repeat_customers = generate_repeat_customers_report(conn)
        
        # Generate summary report
        generate_summary_report(conn, daily_revenue, category_revenue, top_products, repeat_customers)
        
        print("\n✅ All reports generated successfully!")
        print("\n📁 Generated files:")
        print("   - reports/daily_revenue.csv")
        print("   - reports/revenue_by_category.csv")
        print("   - reports/top_products.csv")
        print("   - reports/repeat_customers.csv")
        print("   - reports/summary.md")
        
    except Exception as e:
        print(f"\n❌ Error generating reports: {e}")
    finally:
        conn.close()
        print("\n🔒 Database connection closed")

if __name__ == "__main__":
    main()
