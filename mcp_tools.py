"""
MCP Tools for Sales Database Access

This module contains all MCP tools for querying sales data.
Each function decorated with @mcp.tool() becomes available to the LLM.
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass
import logging

from fastmcp import FastMCP
from app.constants import DATABASE_FILE

logger = logging.getLogger(__name__)

@dataclass
class DatabaseQuery:
    """Helper class for database queries"""
    query: str
    params: tuple = ()

class SalesMCPTools:
    """Tools for accessing sales database via MCP"""
    
    def __init__(self, db_path: str = DATABASE_FILE):
        self.db_path = db_path
    
    def _execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a database query and return results as list of dictionaries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # This enables column access by name
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                # Fetch all results and convert to list of dictionaries
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise Exception(f"Database query failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in query: {e}")
            raise Exception(f"Query execution failed: {str(e)}")

# Initialize tools instance
sales_tools = SalesMCPTools()

def register_tools(mcp: FastMCP):
    """Register all MCP tools with the FastMCP instance"""
    
    @mcp.tool()
    def query_sales_data(query: str) -> str:
        """
        Execute a SQL SELECT query on the sales database.
        
        IMPORTANT: Only SELECT queries are allowed for security.
        
        Args:
            query: SQL SELECT query to execute
            
        Returns:
            JSON string with query results
            
        Example queries:
            - "SELECT * FROM products LIMIT 5"
            - "SELECT SUM(total_amount) as total_revenue FROM sales"
            - "SELECT p.name, SUM(s.quantity) as units_sold FROM sales s JOIN products p ON s.product_id = p.id GROUP BY p.id ORDER BY units_sold DESC LIMIT 5"
        """
        # Validate query - only allow SELECT statements
        query_stripped = query.strip().upper()
        if not query_stripped.startswith('SELECT'):
            return f"Error: Only SELECT queries are allowed. Query must start with SELECT."
        
        # Prevent potentially dangerous operations
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        if any(keyword in query_stripped for keyword in dangerous_keywords):
            return f"Error: Query contains dangerous keywords: {dangerous_keywords}"
        
        try:
            results = sales_tools._execute_query(query)
            
            if not results:
                return "Query executed successfully but returned no results."
            
            # Format results for better readability
            formatted_results = json.dumps(results, indent=2, default=str)
            
            return f"Query results ({len(results)} rows):\n{formatted_results}"
            
        except Exception as e:
            error_msg = f"Error executing query: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @mcp.tool()
    def get_database_schema() -> str:
        """
        Get the database schema information (table structure).
        
        Returns:
            Database schema information including table names, columns, and types
        """
        try:
            # Get table names
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            tables = sales_tools._execute_query(tables_query)
            
            schema_info = "Database Schema:\n\n"
            
            for table in tables:
                table_name = table['name']
                schema_info += f"Table: {table_name}\n"
                
                # Get column information
                columns_query = f"PRAGMA table_info({table_name})"
                columns = sales_tools._execute_query(columns_query)
                
                for col in columns:
                    schema_info += f"  - {col['name']}: {col['type']}"
                    if col['pk']:
                        schema_info += " (PRIMARY KEY)"
                    if col['notnull']:
                        schema_info += " NOT NULL"
                    if col['dflt_value']:
                        schema_info += f" DEFAULT {col['dflt_value']}"
                    schema_info += "\n"
                
                schema_info += "\n"
            
            # Get table row counts
            schema_info += "Table row counts:\n"
            for table in tables:
                table_name = table['name']
                count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                count_result = sales_tools._execute_query(count_query)
                row_count = count_result[0]['count'] if count_result else 0
                schema_info += f"  - {table_name}: {row_count} rows\n"
            
            # Add important notes about date queries
            schema_info += """
⚠️ IMPORTANTE - CONSULTAS DE DATA:
- A coluna 'sale_date' contém TIMESTAMPS completos (YYYY-MM-DD HH:MM:SS)
- Para consultas por período, use funções de data do SQLite:
  * strftime('%Y-%m', sale_date) para filtrar por mês
  * date(sale_date) para filtrar por dia
  * EVITE usar BETWEEN com strings de data!

EXEMPLOS SEGUROS:
✅ SELECT * FROM sales WHERE strftime('%Y-%m', sale_date) = '2025-02'
✅ SELECT * FROM sales WHERE date(sale_date) = '2025-02-28'
❌ SELECT * FROM sales WHERE sale_date BETWEEN '2025-02-01' AND '2025-02-28'
"""
            
            return schema_info
            
        except Exception as e:
            error_msg = f"Error getting database schema: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @mcp.tool()
    def get_sales_statistics() -> str:
        """
        Get general sales statistics from the database.
        
        Returns:
            Formatted string with key sales metrics
        """
        try:
            stats = {}
            
            # Total sales count
            total_query = "SELECT COUNT(*) as total FROM sales"
            total_result = sales_tools._execute_query(total_query)
            stats['total_orders'] = total_result[0]['total'] if total_result else 0
            
            # Total revenue
            revenue_query = "SELECT SUM(total_amount) as revenue FROM sales"
            revenue_result = sales_tools._execute_query(revenue_query)
            stats['total_revenue'] = revenue_result[0]['revenue'] if revenue_result else 0
            
            # Average order value
            if stats['total_orders'] > 0:
                stats['average_order_value'] = stats['total_revenue'] / stats['total_orders']
            else:
                stats['average_order_value'] = 0
            
            # Product count
            product_query = "SELECT COUNT(*) as count FROM products"
            product_result = sales_tools._execute_query(product_query)
            stats['total_products'] = product_result[0]['count'] if product_result else 0
            
            # Customer count
            customer_query = "SELECT COUNT(*) as count FROM customers"
            customer_result = sales_tools._execute_query(customer_query)
            stats['total_customers'] = customer_result[0]['count'] if customer_result else 0
            
            # Date range
            date_query = "SELECT MIN(sale_date) as min_date, MAX(sale_date) as max_date FROM sales"
            date_result = sales_tools._execute_query(date_query)
            if date_result and date_result[0]['min_date']:
                stats['date_range'] = f"{date_result[0]['min_date']} to {date_result[0]['max_date']}"
            else:
                stats['date_range'] = "No sales data"
            
            # Format statistics
            stats_text = "Sales Database Statistics:\n\n"
            stats_text += f"📊 Total Orders: {stats['total_orders']:,}\n"
            stats_text += f"💰 Total Revenue: ${stats['total_revenue']:,.2f}\n"
            stats_text += f"📈 Average Order Value: ${stats['average_order_value']:,.2f}\n"
            stats_text += f"📦 Total Products: {stats['total_products']}\n"
            stats_text += f"👥 Total Customers: {stats['total_customers']}\n"
            stats_text += f"📅 Date Range: {stats['date_range']}\n"
            
            return stats_text
            
        except Exception as e:
            error_msg = f"Error getting sales statistics: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @mcp.tool()
    def analyze_sales_trends() -> str:
        """
        Analyze sales trends over time.
        
        Returns:
            Formatted analysis of sales trends
        """
        try:
            # Get sales by month
            monthly_query = """
            SELECT 
                strftime('%Y-%m', sale_date) as month,
                COUNT(*) as orders,
                SUM(total_amount) as revenue,
                AVG(total_amount) as avg_order_value
            FROM sales 
            GROUP BY strftime('%Y-%m', sale_date)
            ORDER BY month
            """
            
            monthly_results = sales_tools._execute_query(monthly_query)
            
            if not monthly_results:
                return "No sales data available for trend analysis."
            
            trend_text = "Sales Trends Analysis:\n\n"
            trend_text += "Monthly Performance:\n"
            
            for month_data in monthly_results:
                month = month_data['month']
                orders = month_data['orders']
                revenue = month_data['revenue'] or 0
                avg_value = month_data['avg_order_value'] or 0
                
                trend_text += f"  {month}: {orders} orders, ${revenue:,.2f} revenue, ${avg_value:.2f} avg\n"
            
            # Calculate growth trends
            if len(monthly_results) >= 2:
                latest_month = monthly_results[-1]
                previous_month = monthly_results[-2]
                
                order_growth = ((latest_month['orders'] - previous_month['orders']) / previous_month['orders'] * 100) if previous_month['orders'] > 0 else 0
                revenue_growth = ((latest_month['revenue'] - previous_month['revenue']) / previous_month['revenue'] * 100) if previous_month['revenue'] > 0 else 0
                
                trend_text += f"\nMonth-over-Month Growth:\n"
                trend_text += f"  Orders: {order_growth:+.1f}%\n"
                trend_text += f"  Revenue: {revenue_growth:+.1f}%\n"
            
            return trend_text
            
        except Exception as e:
            error_msg = f"Error analyzing sales trends: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @mcp.tool()
    def get_sales_by_period(period_type: str, period_value: str) -> str:
        """
        Get sales data for specific periods with timestamp-safe queries.
        
        This tool solves the common issue of BETWEEN queries with timestamps
        by using proper SQLite date functions internally.
        
        Args:
            period_type: Type of period - 'month', 'day', 'year', 'week'
            period_value: Period value:
                - For month: '2025-02' 
                - For day: '2025-02-28'
                - For year: '2025'
                - For week: '2025-02-24' (any day in the week)
        
        Returns:
            Formatted sales summary for the specified period
            
        Examples:
            - get_sales_by_period('month', '2025-02') -> February 2025 sales
            - get_sales_by_period('day', '2025-02-28') -> Feb 28th sales
            - get_sales_by_period('year', '2025') -> All 2025 sales
        """
        try:
            if period_type == 'month':
                # Format: '2025-02'
                query = """
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(quantity) as total_items,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_order_value,
                    MIN(sale_date) as first_sale,
                    MAX(sale_date) as last_sale
                FROM sales 
                WHERE strftime('%Y-%m', sale_date) = ?
                """
                params = (period_value,)
                period_display = f"mês {period_value}"
                
            elif period_type == 'day':
                # Format: '2025-02-28'
                query = """
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(quantity) as total_items,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_order_value,
                    MIN(sale_date) as first_sale,
                    MAX(sale_date) as last_sale
                FROM sales 
                WHERE date(sale_date) = ?
                """
                params = (period_value,)
                period_display = f"dia {period_value}"
                
            elif period_type == 'year':
                # Format: '2025'
                query = """
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(quantity) as total_items,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_order_value,
                    MIN(sale_date) as first_sale,
                    MAX(sale_date) as last_sale
                FROM sales 
                WHERE strftime('%Y', sale_date) = ?
                """
                params = (period_value,)
                period_display = f"ano {period_value}"
                
            elif period_type == 'week':
                # Format: '2025-02-24' (any day in the week)
                # Get the Monday of the week containing this date
                query = """
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(quantity) as total_items,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_order_value,
                    MIN(sale_date) as first_sale,
                    MAX(sale_date) as last_sale
                FROM sales 
                WHERE date(sale_date) >= date(?, 'weekday 0', '-6 days')
                AND date(sale_date) <= date(?, 'weekday 0')
                """
                params = (period_value, period_value)
                period_display = f"semana que contém {period_value}"
                
            else:
                return f"Erro: Tipo de período '{period_type}' não suportado. Use 'month', 'day', 'year' ou 'week'."
            
            results = sales_tools._execute_query(query, params)
            
            if not results or not results[0]['total_sales']:
                return f"❌ Nenhuma venda encontrada para o {period_display}."
            
            result = results[0]
            
            # Format the response in Portuguese
            response = f"""📊 Resumo de Vendas - {period_display.title()}:

🛒 Total de Vendas: {result['total_sales']}
📦 Itens Vendidos: {result['total_items'] or 0}
💰 Faturamento Total: R$ {result['total_revenue']:,.2f}
📈 Ticket Médio: R$ {result['avg_order_value']:,.2f}"""

            # Add date range if available
            if result['first_sale'] and result['last_sale']:
                first_date = result['first_sale'][:10]  # Get just the date part
                last_date = result['last_sale'][:10]
                if first_date == last_date:
                    response += f"\n📅 Data: {first_date}"
                else:
                    response += f"\n📅 Período: {first_date} a {last_date}"
            
            return response
            
        except Exception as e:
            error_msg = f"Erro ao buscar vendas por período: {str(e)}"
            logger.error(error_msg)
            return error_msg 