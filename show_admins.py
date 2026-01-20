"""
Simple Admins Table Check
"""
import sys
from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        # Get table structure
        result = conn.execute(text("DESCRIBE admins"))
        
        print("ADMINS TABLE STRUCTURE:")
        print("=" * 100)
        print(f"{'Field':<25} {'Type':<35} {'Null':<8} {'Key':<8} {'Default':<15} {'Extra'}")
        print("=" * 100)
        
        for row in result:
            field, type_, null, key, default, extra = row
            default_str = str(default) if default else ''
            extra_str = str(extra) if extra else ''
            print(f"{field:<25} {type_:<35} {null:<8} {key:<8} {default_str:<15} {extra_str}")
        
        # Count records
        result = conn.execute(text("SELECT COUNT(*) FROM admins"))
        count = result.scalar()
        print(f"\nTotal Records: {count}")
        
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
