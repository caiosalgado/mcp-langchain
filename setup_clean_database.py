"""
Script para configurar o banco de dados com apenas os dados do script_dump_banco.txt
"""
import sqlite3
import os
from datetime import datetime

def create_clean_database():
    """Cria o banco de dados limpo com apenas os dados do script original"""
    
    # Remove o banco existente se existir
    if os.path.exists('sales.db'):
        os.remove('sales.db')
        print("✓ Banco de dados anterior removido")
    
    # Conecta ao banco (cria se não existir)
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    
    print("📝 Criando estrutura do banco de dados...")
    
    # Cria as tabelas exatamente como no script original
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            price NUMERIC(10, 2)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER REFERENCES products(id),
            customer_id INTEGER REFERENCES customers(id),
            quantity INTEGER NOT NULL,
            total_amount NUMERIC(10, 2) NOT NULL,
            sale_date TIMESTAMP NOT NULL
        )
    """)
    
    print("✓ Tabelas criadas")
    
    # Insere dados dos produtos (exatamente como no script)
    products_data = [
        ('SKU001', 'Product A', 'Category 1', 10.99),
        ('SKU002', 'Product B', 'Category 1', 20.50),
        ('SKU003', 'Product C', 'Category 2', 15.75),
        ('SKU004', 'Product D', 'Category 3', 30.00),
        ('SKU005', 'Product E', 'Category 4', 25.00)
    ]
    
    cursor.executemany(
        "INSERT INTO products (sku, name, category, price) VALUES (?, ?, ?, ?)",
        products_data
    )
    print("✓ Produtos inseridos: 5 registros")
    
    # Insere dados dos clientes (exatamente como no script)
    customers_data = [
        ('John Doe', 'john@example.com'),
        ('Jane Smith', 'jane@example.com'),
        ('Bob Johnson', 'bob@example.com'),
        ('Alice Brown', 'alice@example.com'),
        ('Charlie Davis', 'charlie@example.com')
    ]
    
    cursor.executemany(
        "INSERT INTO customers (name, email) VALUES (?, ?)",
        customers_data
    )
    print("✓ Clientes inseridos: 5 registros")
    
    # Insere dados de vendas (exatamente como no script)
    sales_data = [
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
        (5, 2, 9, 225.00, '2025-03-02 10:00:00')
    ]
    
    cursor.executemany(
        "INSERT INTO sales (product_id, customer_id, quantity, total_amount, sale_date) VALUES (?, ?, ?, ?, ?)",
        sales_data
    )
    print("✓ Vendas inseridas: 33 registros")
    
    # Commit e fechar
    conn.commit()
    conn.close()
    
    print("\n🎉 Banco de dados criado com sucesso!")
    print(f"📊 Resumo:")
    print(f"   • 5 produtos")
    print(f"   • 5 clientes") 
    print(f"   • 33 vendas")
    print(f"   • Período: 2025-01-05 a 2025-03-02")
    print(f"   • Arquivo: sales.db")

def verify_database():
    """Verifica se o banco foi criado corretamente"""
    try:
        conn = sqlite3.connect('sales.db')
        cursor = conn.cursor()
        
        # Verifica contagem de registros
        cursor.execute("SELECT COUNT(*) FROM products")
        products_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM customers")
        customers_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sales")
        sales_count = cursor.fetchone()[0]
        
        # Verifica uma venda específica
        cursor.execute("""
            SELECT p.name, c.name, s.quantity, s.total_amount, s.sale_date
            FROM sales s
            JOIN products p ON s.product_id = p.id
            JOIN customers c ON s.customer_id = c.id
            LIMIT 1
        """)
        sample_sale = cursor.fetchone()
        
        conn.close()
        
        print(f"\n✅ Verificação do banco:")
        print(f"   • Produtos: {products_count}")
        print(f"   • Clientes: {customers_count}")
        print(f"   • Vendas: {sales_count}")
        print(f"   • Exemplo de venda: {sample_sale[0]} vendido para {sample_sale[1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Configurando banco de dados limpo...")
    create_clean_database()
    verify_database()
    print("\n✨ Pronto! Agora você pode executar a API.") 