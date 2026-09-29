"""
Purge all CSV-imported recipes from the database, leaving only curated seed recipes.
Also cleans up orphaned ingredients that are no longer referenced by any recipe.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.domain import Recipe, RecipeIngredient, Ingredient

def reset_imported():
    db = SessionLocal()
    
    # Step 1: Find all CSV-imported recipes
    imported_recipes = db.query(Recipe).filter(Recipe.source == "csv_import").all()
    count = len(imported_recipes)
    
    if count == 0:
        # Fallback: if source column doesn't exist yet or isn't populated,
        # delete all recipes that are NOT from the seed (i.e., have generic descriptions)
        imported_recipes = db.query(Recipe).filter(
            Recipe.description.like("A delicious % recipe.")
        ).all()
        count = len(imported_recipes)
    
    if count == 0:
        print("No imported recipes found. Database is clean.")
        db.close()
        return

    print(f"Found {count} imported recipes to purge.")
    
    # Step 2: Delete associated recipe_ingredients
    imported_ids = [r.id for r in imported_recipes]
    deleted_ri = db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id.in_(imported_ids)
    ).delete(synchronize_session=False)
    print(f"Deleted {deleted_ri} recipe-ingredient associations.")
    
    # Step 3: Delete the recipes themselves
    deleted_r = db.query(Recipe).filter(
        Recipe.id.in_(imported_ids)
    ).delete(synchronize_session=False)
    print(f"Deleted {deleted_r} imported recipes.")
    
    # Step 4: Clean up orphaned ingredients (not referenced by any remaining recipe)
    orphaned = db.query(Ingredient).filter(
        ~Ingredient.id.in_(
            db.query(RecipeIngredient.ingredient_id).distinct()
        )
    ).all()
    
    if orphaned:
        orphaned_ids = [i.id for i in orphaned]
        db.query(Ingredient).filter(Ingredient.id.in_(orphaned_ids)).delete(synchronize_session=False)
        print(f"Cleaned up {len(orphaned_ids)} orphaned ingredients.")
    
    db.commit()
    print("Database purge complete. Only curated seed recipes remain.")
    db.close()

if __name__ == "__main__":
    reset_imported()
