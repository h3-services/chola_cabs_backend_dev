"""
Check if admins table exists and show its structure
"""
from app.database import engine
from sqlalchemy import inspect, text

def check_admins_table():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("=" * 60)
    print("ALL TABLES IN DATABASE:")
    print("=" * 60)
    for table in sorted(tables):
        print(f"  ✓ {table}")
    
    print("\n" + "=" * 60)
    if 'admins' in tables:
        print("✅ ADMINS TABLE FOUND!")
        print("=" * 60)
        
        # Get columns
        columns = inspector.get_columns('admins')
        print("\nColumns in 'admins' table:")
        print("-" * 60)
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f" DEFAULT {col['default']}" if col['default'] else ""
            print(f"  • {col['name']:<20} {col['type']!s:<15} {nullable}{default}")
        
        # Get primary keys
        pk = inspector.get_pk_constraint('admins')
        if pk['constrained_columns']:
            print(f"\nPrimary Key: {', '.join(pk['constrained_columns'])}")
        
        # Count records
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM admins"))
            count = result.scalar()
            print(f"\nTotal Records: {count}")
            
            if count > 0:
                print("\nSample Records:")
                print("-" * 60)
                result = conn.execute(text("SELECT * FROM admins LIMIT 5"))
                rows = result.fetchall()
                for row in rows:
                    print(f"  {dict(row._mapping)}")
    else:
        print("❌ ADMINS TABLE NOT FOUND")
        print("=" * 60)
        print("\nSearching for similar table names...")
        admin_like = [t for t in tables if 'admin' in t.lower()]
        if admin_like:
            print(f"Found similar tables: {', '.join(admin_like)}")
        else:
            print("No tables with 'admin' in the name found.")

if __name__ == "__main__":
    check_admins_table()
