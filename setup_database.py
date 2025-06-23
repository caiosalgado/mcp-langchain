"""
Script to set up the database with initial data from script_dump_banco.txt
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.database import DATABASE_URL
from datetime import datetime

def create_and_populate_database():
    """Create database tables and populate with initial data"""
    
    print("Setting up database...")
    
    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Check if data already exists
        result = session.execute(text("SELECT COUNT(*) FROM products"))
        product_count = result.scalar()
        
        if product_count > 0:
            print(f"Database already has {product_count} products. Skipping data insertion.")
            return
        
        # Insert products
        products_sql = """
        INSERT INTO products (sku, name, category, price) VALUES 
        ('SKU001', 'Product A', 'Category 1', 10.99),
        ('SKU002', 'Product B', 'Category 1', 20.50),
        ('SKU003', 'Product C', 'Category 2', 15.75),
        ('SKU004', 'Product D', 'Category 3', 30.00),
        ('SKU005', 'Product E', 'Category 4', 25.00);
        """
        session.execute(text(products_sql))
        print("✓ Products inserted")
        
        # Insert customers
        customers_sql = """
        INSERT INTO customers (name, email) VALUES 
        ('John Doe', 'john@example.com'),
        ('Jane Smith', 'jane@example.com'),
        ('Bob Johnson', 'bob@example.com'),
        ('Alice Brown', 'alice@example.com'),
        ('Charlie Davis', 'charlie@example.com');
        """
        session.execute(text(customers_sql))
        print("✓ Customers inserted")
        
        # Insert sales
        sales_sql = """
        INSERT INTO sales (product_id, customer_id, quantity, total_amount, sale_date) VALUES 
        (4, 1, 4, 120.00, '2025-01-17 12:22:49'),
        (5, 1, 7, 175.00, '2025-01-28 04:04:17'),
        (5, 4, 4, 100.00, '2025-02-04 11:58:16'),
        (1, 2, 2, 21.98, '2025-01-05 10:30:45'),
        (2, 3, 1, 20.50, '2025-01-06 15:15:10'),
        (3, 5, 3, 47.25, '2025-01-08 09:45:22'),
        (4, 2, 1, 30.00, '2025-01-10 17:22:30'),
        (5, 4, 5, 125.00, '2025-01-12 11:00:00'),
        (1, 3, 2, 21.98, '2025-01-14 18:25:45'),
        (2, 5, 6, 123.00, '2025-01-15 13:12:22'),
        (3, 1, 2, 31.50, '2025-01-18 08:10:33'),
        (4, 4, 1, 30.00, '2025-01-20 14:05:20'),
        (5, 2, 3, 75.00, '2025-01-23 19:30:40'),
        (1, 5, 2, 21.98, '2025-01-25 10:45:10'),
        (2, 4, 4, 82.00, '2025-01-29 16:20:50'),
        (3, 2, 1, 15.75, '2025-02-01 12:00:00'),
        (4, 5, 2, 60.00, '2025-02-03 18:40:30'),
        (5, 1, 8, 200.00, '2025-02-05 11:25:00'),
        (1, 4, 3, 32.97, '2025-02-07 14:50:10'),
        (2, 3, 2, 41.00, '2025-02-08 10:20:15'),
        (3, 5, 4, 63.00, '2025-02-10 16:45:55'),
        (4, 2, 1, 30.00, '2025-02-12 20:30:00'),
        (5, 3, 2, 50.00, '2025-02-15 09:10:10'),
        (1, 1, 6, 65.94, '2025-02-16 13:35:30'),
        (2, 4, 2, 41.00, '2025-02-18 15:00:00'),
        (3, 2, 3, 47.25, '2025-02-19 11:30:45'),
        (4, 5, 2, 60.00, '2025-02-21 14:10:22'),
        (5, 4, 1, 25.00, '2025-02-22 19:45:55'),
        (1, 2, 7, 76.93, '2025-02-24 12:10:10'),
        (2, 1, 4, 82.00, '2025-02-25 17:30:50'),
        (3, 3, 5, 78.75, '2025-02-27 09:55:00'),
        (4, 5, 3, 90.00, '2025-02-28 14:25:30'),
        (5, 2, 9, 225.00, '2025-03-02 10:00:00');
        """
        session.execute(text(sales_sql))
        print("✓ Sales data inserted")
        
        # Commit the transaction
        session.commit()
        print("✓ Database setup completed successfully!")
        
        # Show statistics
        result = session.execute(text("SELECT COUNT(*) FROM products"))
        product_count = result.scalar()
        
        result = session.execute(text("SELECT COUNT(*) FROM customers"))
        customer_count = result.scalar()
        
        result = session.execute(text("SELECT COUNT(*) FROM sales"))
        sales_count = result.scalar()
        
        print(f"\nDatabase Statistics:")
        print(f"- Products: {product_count}")
        print(f"- Customers: {customer_count}")
        print(f"- Sales: {sales_count}")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    create_and_populate_database() 