"""Check database schema"""
import sqlite3

conn = sqlite3.connect('cab_app.db')
cursor = conn.cursor()

# Get wallet_transactions schema
cursor.execute("PRAGMA table_info(wallet_transactions)")
print("wallet_transactions schema:")
for row in cursor.fetchall():
    print(f"  {row[1]}: {row[2]}")

# Get sample data
cursor.execute("SELECT * FROM wallet_transactions LIMIT 1")
print("\nSample wallet_transaction:")
for row in cursor.fetchall():
    print(f"  {row}")

# Get payment_transactions schema
cursor.execute("PRAGMA table_info(payment_transactions)")
print("\npayment_transactions schema:")
for row in cursor.fetchall():
    print(f"  {row[1]}: {row[2]}")

# Get tariff config schema
cursor.execute("PRAGMA table_info(vehicle_tariff_config)")
print("\nvehicle_tariff_config schema:")
for row in cursor.fetchall():
    print(f"  {row[1]}: {row[2]}")

conn.close()
