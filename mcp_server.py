"""
MCP Server for Sales Database Access

This server provides tools for querying sales data through MCP (Model Context Protocol).
It uses FastMCP to create a server that can be consumed by LangChain MCP adapters.
"""
import argparse
import logging

from fastmcp import FastMCP
from app.constants import MCP_SERVER_PORT
from mcp_tools import register_tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("Sales Database Server")

# Register all MCP tools
register_tools(mcp)

def main():
    """Main function to run the MCP server"""
    parser = argparse.ArgumentParser(description="Start Sales Database MCP Server")
    parser.add_argument(
        "--port", 
        type=int, 
        default=MCP_SERVER_PORT, 
        help=f"Port to run the server on (default: {MCP_SERVER_PORT})"
    )
    
    args = parser.parse_args()
    
    print(f"Starting Sales Database MCP Server on port {args.port}...")
    print("Available tools:")
    print("- query_sales_data: Execute SQL queries")
    print("- get_database_schema: Get database structure")
    print("- get_sales_statistics: Get general statistics")
    print("- analyze_sales_trends: Analyze sales trends")
    print("- get_sales_by_period: Get sales for specific periods")
    
    # Run the server
    mcp.run(transport="streamable-http", host="127.0.0.1", port=args.port)

if __name__ == "__main__":
    main() 