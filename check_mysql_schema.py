"""Check production MySQL database schema and save to file"""
import mysql.connector

# MySQL connection details (without database)
config = {
    'host': '72.62.196.30',
    'port': 3306,
    'user': 'myuser',
    'password': 'Hope3Services@2026'
}

output = []

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    output.append("="*60)
    output.append("Connected to MySQL Server!")
    output.append("="*60)
    
    # Get all databases
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    output.append("\nAvailable databases:")
    for db in databases:
        output.append(f"  - {db[0]}")
    
    # Try to use cab_app database (lowercase)
    try:
        cursor.execute("USE cab_app")
        output.append(f"\n{'='*60}")
        output.append("Using database: cab_app")
        output.append('='*60)
    except:
        cursor.execute("USE CAB_APP")
        output.append(f"\n{'='*60}")
        output.append("Using database: CAB_APP")
        output.append('='*60)
    
    # Get all tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    output.append("\nTables in database:")
    for t in tables:
        output.append(f"  - {t[0]}")
    
    # Check each important table schema
    important_tables = ['drivers', 'vehicles', 'trips', 'payment_transactions', 
                       'wallet_transactions', 'vehicle_tariff_config']
    
    for table in important_tables:
        try:
            output.append(f"\n{'='*60}")
            output.append(f"Table: {table}")
            output.append('='*60)
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            for col in columns:
                output.append(f"  {col[0]:<25} {col[1]:<30} NULL:{col[2]:<5} KEY:{col[3]:<5}")
        except Exception as e:
            output.append(f"  Error: {e}")
    
    # Check sample data counts
    output.append(f"\n{'='*60}")
    output.append("Data Counts")
    output.append('='*60)
    for table in important_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            output.append(f"  {table:<30} {count} records")
        except:
            pass
    
    cursor.close()
    conn.close()
    output.append("\n" + "="*60)
    output.append("Schema check complete!")
    output.append("="*60)
    
except mysql.connector.Error as err:
    output.append(f"MySQL Error: {err}")
except Exception as e:
    output.append(f"Unexpected error: {e}")

# Write to file
with open('mysql_schema_report.txt', 'w') as f:
    f.write('\n'.join(output))

# Also print
print('\n'.join(output))
