#!/usr/bin/env python3
"""
Orders Analytics - Database Loader
This script creates an SQLite database and loads order data from CSV.
"""

import sqlite3
import csv
import os
from datetime import datetime

def create_database():
    """Create the orders database and table."""
    print("Creating orders.db database...")
    
    # Connect to database (creates file if it doesn't exist)
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            order_date DATE,
            customer_id TEXT,
            product TEXT,
            category TEXT,
            unit_price REAL,
            quantity INTEGER,
            country TEXT
        )
    ''')
    
    conn.commit()
    print("✓ Database and table created successfully")
    return conn

def load_csv_data(conn):
    """Load data from CSV file into the database."""
    csv_file = 'data/orders.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: {csv_file} not found!")
        return False
    
    print(f"Loading data from {csv_file}...")
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM orders')
    
    # Load CSV data
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        rows_inserted = 0
        
        for row in csv_reader:
            cursor.execute('''
                INSERT INTO orders (order_id, order_date, customer_id, product, 
                                  category, unit_price, quantity, country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['order_id'],
                row['order_date'],
                row['customer_id'],
                row['product'],
                row['category'],
                float(row['unit_price']),
                int(row['quantity']),
                row['country']
            ))
            rows_inserted += 1
    
    conn.commit()
    print(f"✓ Successfully loaded {rows_inserted} orders into database")
    return True

def verify_data(conn):
    """Verify the loaded data."""
    cursor = conn.cursor()
    
    # Count total records
    cursor.execute('SELECT COUNT(*) FROM orders')
    total_count = cursor.fetchone()[0]
    
    # Get date range
    cursor.execute('SELECT MIN(order_date), MAX(order_date) FROM orders')
    date_range = cursor.fetchone()
    
    # Get category breakdown
    cursor.execute('SELECT category, COUNT(*) FROM orders GROUP BY category ORDER BY COUNT(*) DESC')
    categories = cursor.fetchall()
    
    print(f"\n📊 Data Summary:")
    print(f"   Total orders: {total_count}")
    print(f"   Date range: {date_range[0]} to {date_range[1]}")
    print(f"   Categories:")
    for category, count in categories:
        print(f"     - {category}: {count} orders")

def main():
    """Main function to create database and load data."""
    print("🚀 Orders Analytics - Database Setup")
    print("=" * 40)
    
    try:
        # Create database and table
        conn = create_database()
        
        # Load CSV data
        if load_csv_data(conn):
            verify_data(conn)
            print("\n✅ Database setup completed successfully!")
            print("   Database file: orders.db")
            print("   Ready to run analytics with: python queries.py")
        else:
            print("\n❌ Database setup failed!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
