"""Add the 'meal_type' column to the recipes table if it doesn't exist."""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine

def migrate():
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE recipes ADD COLUMN IF NOT EXISTS meal_type VARCHAR DEFAULT 'savoury'"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_recipes_meal_type ON recipes (meal_type)"))
        conn.commit()
    print("Migration complete: 'meal_type' column added to recipes table.")

if __name__ == "__main__":
    migrate()
