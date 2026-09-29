import csv
import sys
import os
import re

# Add the project root to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.domain import Recipe, Ingredient, RecipeIngredient


def normalize_ingredient_name(raw: str) -> str:
    """
    Strips quantities, units, and common adjectives from a raw ingredient string
    to produce a clean canonical ingredient name.
    """
    raw = raw.lower().strip()
    # Remove parenthetical synonyms like "(besan)" or "(Jeera)"
    raw = re.sub(r'\(.*?\)', '', raw).strip()
    # Remove leading quantity patterns like "1 tablespoon", "2 teaspoons", "1/2 cup"
    raw = re.sub(r'^[\d/.\s]+(tablespoon|teaspoon|cup|lb|kg|g|ml|oz|piece|pieces|inch|small|medium|large|whole)s?\s+', '', raw, flags=re.IGNORECASE).strip()
    # Remove common adjectives/preparation words
    adjectives = [
        "fresh", "chopped", "diced", "sliced", "minced", "grated",
        "ground", "crushed", "dried", "finely", "roughly", "thinly",
        "powdered", "raw", "ripe", "tender", "boneless", "skinless",
        "to taste", "as required", "as needed", "for garnishing",
        "for frying", "for greasing", "optional",
    ]
    for adj in adjectives:
        raw = raw.replace(adj, "")
    # Collapse whitespace and strip leading/trailing dashes and hyphens
    raw = re.sub(r'\s+', ' ', raw).strip(' -,')
    return raw


def import_csv(file_path, limit=500):
    db = SessionLocal()
    print(f"Importing up to {limit} recipes from {file_path}")
    
    existing_ingredients = {ing.name: ing for ing in db.query(Ingredient).all()}
    
    recipes_added = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if recipes_added >= limit:
                break
                
            name = row.get('TranslatedRecipeName', '').strip()
            if not name: continue
            
            if db.query(Recipe).filter(Recipe.name == name).first():
                continue
                
            ingredients_str = row.get('Cleaned-Ingredients', '')
            instructions = row.get('TranslatedInstructions', '')
            image_url = row.get('image-url', '').strip()
            cuisine = row.get('Cuisine', 'Indian')
            
            time_str = row.get('TotalTimeInMins', '0')
            try:
                cook_time = int(time_str)
            except:
                cook_time = 30

            # Treat empty/whitespace-only image URLs as None
            if not image_url:
                image_url = None
                
            recipe = Recipe(
                name=name,
                description=f"A delicious {cuisine} recipe: {name}.",
                instructions=instructions,
                image_url=image_url,
                cuisine=cuisine,
                difficulty="Medium",
                prep_time=15,
                cook_time=cook_time,
                servings=4,
                diet_type="Vegetarian" if "veg" in cuisine.lower() else "Non-Vegetarian",
                rating=3.5,         # Lower default rating than curated recipes
                popularity=50,      # Lower default popularity than curated recipes
                source="csv_import" # Mark as imported so we can filter/de-prioritize
            )
            db.add(recipe)
            db.flush()
            
            # Parse and normalize ingredient names properly
            ings = [i.strip() for i in ingredients_str.split(',')]
            for raw_ing in ings:
                if not raw_ing: continue
                ing_name = normalize_ingredient_name(raw_ing)
                if not ing_name or len(ing_name) < 2:
                    continue  # Skip empty or too-short names
                    
                if ing_name not in existing_ingredients:
                    new_ing = Ingredient(name=ing_name)
                    db.add(new_ing)
                    db.flush()
                    existing_ingredients[ing_name] = new_ing
                
                db.add(RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=existing_ingredients[ing_name].id,
                    quantity=1,
                    unit="unit"
                ))
                
            recipes_added += 1
            if recipes_added % 100 == 0:
                print(f"Added {recipes_added} recipes...")
                db.commit()
                
    db.commit()
    print(f"Done! Imported {recipes_added} new recipes.")
    db.close()

if __name__ == '__main__':
    # File is in d:\smartcook
    import_csv('../Cleaned_Indian_Food_Dataset.csv', limit=7000)
