"""Check existing error codes in production database"""
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
    print("Existing Error Codes in Database")
    print("="*60)
    
    cursor.execute("SELECT error_code, error_type, error_description FROM error_handling ORDER BY error_code")
    errors = cursor.fetchall()
    
    if errors:
        print(f"\nFound {len(errors)} predefined errors:\n")
        for error in errors:
            print(f"Code {error[0]:3d}: [{error[1]}] {error[2]}")
    else:
        print("\nNo predefined errors found in database!")
        print("You need to populate the error_handling table.")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
