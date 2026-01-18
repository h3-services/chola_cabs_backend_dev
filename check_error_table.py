"""Check production database error_handling table structure and data"""
import mysql.connector
import json

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
    
    print("="*70)
    print("Checking error_handling Table")
    print("="*70)
    
    # Check table structure
    cursor.execute("DESCRIBE error_handling")
    columns = cursor.fetchall()
    print("\nTable Structure:")
    for col in columns:
        print(f"  {col[0]:20s} {col[1]:30s} NULL:{col[2]:5s}")
    
    # Get sample data
    cursor.execute("SELECT * FROM error_handling LIMIT 3")
    errors = cursor.fetchall()
    
    print(f"\nSample Data ({len(errors)} records):")
    print("-"*70)
    for err in errors:
        print(f"ID: {err[0]}")
        print(f"Type: {err[1]}")
        print(f"Code: {err[2]}")
        print(f"Description: {err[3][:50]}...")
        print(f"Created: {err[4]}")
        print("-"*70)
    
    # Check data types
    cursor.execute("SELECT error_id, error_code FROM error_handling LIMIT 1")
    result = cursor.fetchone()
    if result:
        print(f"\nData Type Check:")
        print(f"  error_id type: {type(result[0])} = {result[0]}")
        print(f"  error_code type: {type(result[1])} = {result[1]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
