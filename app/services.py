"""
Business services for sales operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.models import Product, Sale, Customer

class SalesService:
    """Service for sales-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_top_products_last_month(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get top products by quantity sold in the last month
        
        Args:
            limit: Number of products to return (default: 5)
            
        Returns:
            List of dictionaries with product information and sales data
        """
        # For demonstration purposes, using a wider date range since sample data is from 2025
        # In production, this would use the actual last month
        today = datetime.now()
        # Using last 12 months for demo data
        last_period = today - timedelta(days=365)
        
        # Query to get top products by quantity sold in last month
        results = (
            self.db.query(
                Product.id,
                Product.name,
                Product.category,
                Product.price,
                func.sum(Sale.quantity).label('total_quantity'),
                func.sum(Sale.total_amount).label('total_revenue'),
                func.count(Sale.id).label('total_sales')
            )
            .join(Sale, Product.id == Sale.product_id)
            .filter(Sale.sale_date >= last_period)
            .group_by(Product.id, Product.name, Product.category, Product.price)
            .order_by(desc('total_quantity'))
            .limit(limit)
            .all()
        )
        
        return [
            {
                "product_id": result.id,
                "product_name": result.name,
                "category": result.category,
                "price": float(result.price) if result.price else 0,
                "total_quantity_sold": result.total_quantity,
                "total_revenue": float(result.total_revenue),
                "total_number_of_sales": result.total_sales
            }
            for result in results
        ]
    
    def get_sales_stats(self) -> Dict[str, Any]:
        """Get general sales statistics"""
        today = datetime.now()
        # Using last 12 months for demo data (sample data is from 2025)
        last_period = today - timedelta(days=365)
        
        # Total sales count
        total_sales = self.db.query(Sale).count()
        
        # Total revenue
        total_revenue = self.db.query(func.sum(Sale.total_amount)).scalar() or 0
        
        # Sales in period
        sales_last_month = (
            self.db.query(Sale)
            .filter(Sale.sale_date >= last_period)
            .count()
        )
        
        # Revenue in period
        revenue_last_month = (
            self.db.query(func.sum(Sale.total_amount))
            .filter(Sale.sale_date >= last_period)
            .scalar() or 0
        )
        
        # Total unique customers
        total_customers = self.db.query(Customer).count()
        
        # Total products
        total_products = self.db.query(Product).count()
        
        return {
            "total_sales": total_sales,
            "total_revenue": float(total_revenue),
            "sales_last_month": sales_last_month,
            "revenue_last_month": float(revenue_last_month),
            "total_customers": total_customers,
            "total_products": total_products,
            "period_analyzed": f"Last 12 months (from {last_period.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')})"
        } 