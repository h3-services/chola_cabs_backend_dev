"""Check production data in payments and wallet_transactions"""
import mysql.connector

config = {
    'host': '72.62.196.30',
    'port': 3306,
    'user': 'myuser',
    'password': 'Hope3Services@2026',
    'database': 'cab_app'
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    print("="*60)
    print("Payment Transactions Data")
    print("="*60)
    cursor.execute("SELECT * FROM payment_transactions LIMIT 5")
    columns = [desc[0] for desc in cursor.description]
    print(f"Columns: {columns}")
    for row in cursor.fetchall():
        print(row)
    
    print("\n" + "="*60)
    print("Wallet Transactions Data")
    print("="*60)
    cursor.execute("SELECT * FROM wallet_transactions LIMIT 5")
    columns = [desc[0] for desc in cursor.description]
    print(f"Columns: {columns}")
    for row in cursor.fetchall():
        print(row)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
