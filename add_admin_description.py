"""
Migration script to add admin_description column to error_handling table
"""
from app.database import engine
from sqlalchemy import text

def add_admin_description_column():
    try:
        with engine.connect() as connection:
            # Add the new column
            connection.execute(text("""
                ALTER TABLE error_handling 
                ADD COLUMN admin_description TEXT NULL
            """))
            connection.commit()
            print("Successfully added admin_description column to error_handling table")
            
    except Exception as e:
        print(f"Error adding column: {e}")

if __name__ == "__main__":
    add_admin_description_column()