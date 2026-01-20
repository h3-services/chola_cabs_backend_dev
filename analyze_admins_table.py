"""
Comprehensive Admins Table Report
"""
from app.database import engine
from sqlalchemy import text
import json

print("=" * 80)
print("ADMINS TABLE REPORT")
print("=" * 80)

with engine.connect() as conn:
    # Check if table exists
    result = conn.execute(text("SHOW TABLES LIKE 'admins'"))
    exists = result.fetchone()
    
    if exists:
        print("\n✅ TABLE EXISTS: admins\n")
        
        # Show structure
        print("TABLE STRUCTURE:")
        print("-" * 80)
        print(f"{'Field':<25} {'Type':<30} {'Null':<8} {'Key':<8} {'Default':<15}")
        print("-" * 80)
        
        result = conn.execute(text("DESCRIBE admins"))
        columns = []
        for row in result:
            field, type_, null, key, default, extra = row
            columns.append({
                'field': field,
                'type': type_,
                'null': null,
                'key': key,
                'default': default,
                'extra': extra
            })
            default_str = str(default) if default else ''
            print(f"{field:<25} {type_:<30} {null:<8} {key:<8} {default_str:<15}")
        
        # Count records
        result = conn.execute(text("SELECT COUNT(*) FROM admins"))
        count = result.scalar()
        print(f"\n{'Total Records:':<25} {count}")
        
        # Show indexes
        print("\n\nINDEXES:")
        print("-" * 80)
        result = conn.execute(text("SHOW INDEXES FROM admins"))
        for row in result:
            print(f"  • {row[2]} on column: {row[4]}")
        
        # Show sample data if exists
        if count > 0:
            print("\n\nSAMPLE DATA:")
            print("-" * 80)
            result = conn.execute(text("SELECT * FROM admins LIMIT 5"))
            rows = result.fetchall()
            for i, row in enumerate(rows, 1):
                print(f"\nRecord {i}:")
                for j, col in enumerate(columns):
                    print(f"  {col['field']:<20}: {row[j]}")
        else:
            print("\n\n⚠️  No records found in admins table")
        
        # Generate SQLAlchemy model
        print("\n\n" + "=" * 80)
        print("SUGGESTED SQLALCHEMY MODEL:")
        print("=" * 80)
        print("""
class Admin(Base):
    __tablename__ = "admins"
    """)
        
        for col in columns:
            field_name = col['field']
            type_str = col['type']
            
            # Map MySQL types to SQLAlchemy types
            if 'varchar' in type_str:
                length = type_str.split('(')[1].split(')')[0]
                sa_type = f"String({length})"
            elif 'enum' in type_str:
                sa_type = "String(50)"  # or create Enum
            elif 'datetime' in type_str:
                sa_type = "DateTime"
            elif 'text' in type_str:
                sa_type = "Text"
            elif 'int' in type_str:
                sa_type = "Integer"
            else:
                sa_type = "String(255)"
            
            nullable = col['null'] == 'YES'
            primary_key = col['key'] == 'PRI'
            
            args = []
            if primary_key:
                args.append("primary_key=True")
            if not nullable and not primary_key:
                args.append("nullable=False")
            if col['default']:
                if col['default'] == 'CURRENT_TIMESTAMP':
                    args.append("default=func.now()")
                else:
                    args.append(f"default='{col['default']}'")
            
            args_str = ", ".join(args) if args else ""
            print(f"    {field_name} = Column({sa_type}, {args_str})")
        
    else:
        print("\n❌ ADMINS TABLE DOES NOT EXIST")
        
        # Show all tables
        result = conn.execute(text("SHOW TABLES"))
        print("\nAvailable tables:")
        for row in result:
            print(f"  - {row[0]}")

print("\n" + "=" * 80)
