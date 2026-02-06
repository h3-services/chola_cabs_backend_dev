
import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Add the current directory to sys.path so we can import from app
sys.path.append(os.getcwd())

from app.database import DATABASE_URL

def update_schema():
    print(f"Connecting to database...")
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    table_name = "trips"
    
    # List of new columns to add
    # format: (column_name, column_type_sql)
    new_columns = [
        ("waiting_charges", "DECIMAL(10, 2) DEFAULT 0.00"),
        ("inter_state_permit_charges", "DECIMAL(10, 2) DEFAULT 0.00"),
        ("driver_allowance", "DECIMAL(10, 2) DEFAULT 0.00"),
        ("luggage_cost", "DECIMAL(10, 2) DEFAULT 0.00"),
        ("pet_cost", "DECIMAL(10, 2) DEFAULT 0.00"),
        ("toll_charges", "DECIMAL(10, 2) DEFAULT 0.00"),
        ("night_allowance", "DECIMAL(10, 2) DEFAULT 0.00"),
        ("total_amount", "DECIMAL(10, 2) DEFAULT 0.00")
    ]
    
    with engine.connect() as connection:
        # Get existing columns
        existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
        print(f"Existing columns in '{table_name}': {existing_columns}")
        
        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                print(f"Adding missing column: {col_name}...")
                try:
                    alter_query = text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                    connection.execute(alter_query)
                    print(f"✅ Added {col_name}")
                except Exception as e:
                    print(f"❌ Failed to add {col_name}: {e}")
            else:
                print(f"Column {col_name} already exists.")
        
        # Verify changes
        # Re-inspect to make sure columns are there
        # Note: inspector might cache, strict verification might require re-creating engine or just trusting the ALTER success
        print("\nSchema update process completed.")

if __name__ == "__main__":
    update_schema()
