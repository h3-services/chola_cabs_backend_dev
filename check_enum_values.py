"""Check exact production data to see ENUM values"""
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
    print("Payment Transactions - Sample Data")
    print("="*60)
    cursor.execute("SELECT payment_id, driver_id, amount, transaction_type, status FROM payment_transactions LIMIT 3")
    for row in cursor.fetchall():
        print(f"ID: {row[0]}")
        print(f"  driver_id: {row[1]}")
        print(f"  amount: {row[2]}")
        print(f"  transaction_type: {row[3]}")
        print(f"  status: {row[4]}")
        print()
    
    print("="*60)
    print("Wallet Transactions - Sample Data")
    print("="*60)
    cursor.execute("SELECT wallet_id, driver_id, amount, transaction_type FROM wallet_transactions LIMIT 3")
    for row in cursor.fetchall():
        print(f"ID: {row[0]}")
        print(f"  driver_id: {row[1]}")
        print(f"  amount: {row[2]}")
        print(f"  transaction_type: {row[3]}")
        print()
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
