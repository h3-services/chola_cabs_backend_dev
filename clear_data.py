"""Clear problematic data from database"""
import sqlite3

conn = sqlite3.connect('cab_app.db')
cursor = conn.cursor()

# Check and clear wallet_transactions
cursor.execute("SELECT COUNT(*) FROM wallet_transactions")
wallet_count = cursor.fetchone()[0]
print(f"Wallet transactions count: {wallet_count}")

if wallet_count > 0:
    cursor.execute("DELETE FROM wallet_transactions")
    print("Cleared wallet_transactions table")

# Check and clear payment_transactions
cursor.execute("SELECT COUNT(*) FROM payment_transactions")
payment_count = cursor.fetchone()[0]
print(f"Payment transactions count: {payment_count}")

if payment_count > 0:
    cursor.execute("DELETE FROM payment_transactions")
    print("Cleared payment_transactions table")

# Check and clear vehicle_tariff_config
cursor.execute("SELECT COUNT(*) FROM vehicle_tariff_config")
tariff_count = cursor.fetchone()[0]
print(f"Tariff configs count: {tariff_count}")

if tariff_count > 0:
    cursor.execute("DELETE FROM vehicle_tariff_config")
    print("Cleared vehicle_tariff_config table")

conn.commit()
conn.close()
print("\nDatabase cleaned successfully!")
