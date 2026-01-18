"""Check error codes in production database for uniqueness"""
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
    
    print("="*70)
    print("PRODUCTION DATABASE: Error Code Verification")
    print("="*70)
    
    # Get all error codes
    cursor.execute("""
        SELECT error_code, error_type, error_description 
        FROM error_handling 
        ORDER BY error_code
    """)
    errors = cursor.fetchall()
    
    print(f"\n✅ Total Errors in Database: {len(errors)}")
    
    # Check for duplicates
    error_codes = [err[0] for err in errors]
    unique_codes = set(error_codes)
    
    print(f"✅ Unique Error Codes: {len(unique_codes)}")
    
    if len(error_codes) == len(unique_codes):
        print("✅ ALL ERROR CODES ARE UNIQUE ✓")
    else:
        print("❌ WARNING: Duplicate error codes found!")
        duplicates = [code for code in error_codes if error_codes.count(code) > 1]
        print(f"   Duplicate codes: {set(duplicates)}")
    
    print("\n" + "="*70)
    print("All Error Codes:")
    print("="*70)
    
    for err in errors:
        code, error_type, description = err
        print(f"Code {code:4d}: [{error_type:25s}] {description[:40]}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*70)
    print("✅ Verification Complete")
    print("="*70)
    
except Exception as e:
    print(f"❌ Error: {e}")
