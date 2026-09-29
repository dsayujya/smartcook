from sqlalchemy import text
from app.database import engine, Base
from app.models import domain

def run_migrations():
    print("Running database migrations...")
    
    # 1. Ensure all missing tables are created
    Base.metadata.create_all(bind=engine)
    
    # 2. Add missing columns to users table if they don't exist
    columns_to_add = [
        ("full_name", "VARCHAR"),
        ("phone_number", "VARCHAR"),
        ("is_email_verified", "BOOLEAN DEFAULT FALSE"),
        ("is_phone_verified", "BOOLEAN DEFAULT FALSE"),
        ("google_id", "VARCHAR"),
        ("avatar_url", "VARCHAR"),
        ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
    ]
    
    with engine.connect() as conn:
        for col_name, col_type in columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
                conn.commit()
                print(f"Verified column: users.{col_name}")
            except Exception as e:
                print(f"Error adding column {col_name}: {e}")
                
    print("Database migration completed successfully!")

if __name__ == "__main__":
    run_migrations()
