"""
Classify existing recipes as 'sweet' or 'savoury' using keyword heuristics
on recipe name and ingredient names.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.domain import Recipe, RecipeIngredient, Ingredient

# Keywords that strongly indicate a sweet/dessert recipe
SWEET_NAME_KEYWORDS = [
    "cake", "halwa", "kheer", "gulab jamun", "dessert", "sweet", "pudding",
    "ice cream", "mithai", "ladoo", "laddu", "barfi", "burfi", "jalebi",
    "rasgulla", "rasmalai", "sandesh", "payasam", "basundi", "rabri",
    "shrikhand", "modak", "peda", "kulfi", "falooda", "brownie", "cookie",
    "cupcake", "muffin", "pie", "tart", "pastry", "fudge", "truffle",
    "mousse", "parfait", "cheesecake", "tiramisu", "panna cotta",
    "milkshake", "smoothie", "lassi", "shake", "sherbet", "sorbet",
    "caramel", "praline", "meringue", "souffle", "waffle", "pancake",
    "crepe", "donut", "doughnut", "churro", "biscuit", "scone",
    "halva", "mysore pak", "coconut burfi", "phirni", "seviyan",
    "malpua", "imarti", "kalakand", "cham cham", "rasgula",
    "fruit salad", "compote", "jam", "marmalade", "preserve",
    "candy", "lollipop", "toffee", "chocolate",
]

SWEET_INGREDIENT_KEYWORDS = [
    "sugar", "jaggery", "honey", "chocolate", "cocoa", "condensed milk",
    "whipped cream", "vanilla extract", "vanilla essence", "maple syrup",
    "molasses", "caramel", "icing", "frosting", "sprinkles",
    "brown sugar", "powdered sugar", "caster sugar", "corn syrup",
]


def classify_recipes():
    db = SessionLocal()

    all_recipes = db.query(Recipe).all()
    sweet_count = 0
    savoury_count = 0

    for recipe in all_recipes:
        name_lower = (recipe.name or "").lower()

        # Check recipe name against sweet keywords
        is_sweet = any(kw in name_lower for kw in SWEET_NAME_KEYWORDS)

        # If not matched by name, check ingredients
        if not is_sweet:
            ingredient_names = []
            for ri in recipe.ingredients:
                if ri.ingredient:
                    ingredient_names.append(ri.ingredient.name.lower())
            all_ingredients_text = " ".join(ingredient_names)

            # A recipe is sweet if it contains multiple sweet-indicator ingredients
            sweet_ingredient_hits = sum(
                1 for kw in SWEET_INGREDIENT_KEYWORDS if kw in all_ingredients_text
            )
            # Require at least 2 sweet ingredient matches to classify as sweet
            # (since "sugar" alone appears in many savoury recipes)
            if sweet_ingredient_hits >= 2:
                is_sweet = True

        recipe.meal_type = "sweet" if is_sweet else "savoury"
        if is_sweet:
            sweet_count += 1
        else:
            savoury_count += 1

    db.commit()
    print(f"Classification complete: {sweet_count} sweet, {savoury_count} savoury (total: {len(all_recipes)})")
    db.close()


if __name__ == "__main__":
    classify_recipes()
