from app.database import SessionLocal
from app.models.domain import Recipe, Ingredient, RecipeIngredient

def seed():
    db = SessionLocal()
    
    # Predefined ingredients
    raw_ingredients = [
        "tomato", "onion", "garlic", "potato", "carrot", "beef", "chicken", "salt", 
        "pepper", "olive oil", "pasta", "cheese", "basil", "butter", "milk", "flour", 
        "sugar", "egg", "apple", "banana", "bananas", "orange slices", "orange zest", 
        "blueberries", "pineapple", "strawberries", "kiwi", "brown sugar", "orange juice", 
        "lemon juice", "lemon zest", "grapes", "extract", "honey", "lime juice", "mint", "yogurt"
    ]
    
    db_ingredients = {}
    for name in raw_ingredients:
        # Check if exists first
        ing = db.query(Ingredient).filter(Ingredient.name == name.lower()).first()
        if not ing:
            ing = Ingredient(name=name.lower())
            db.add(ing)
            db.commit()
            db.refresh(ing)
        db_ingredients[name.lower()] = ing

    def add_recipe(name, desc, inst, img, cui, diff, pt, ct, serv, diet, rat, pop, ings):
        recipe = db.query(Recipe).filter(Recipe.name == name).first()
        if not recipe:
            recipe = Recipe(name=name, description=desc, instructions=inst, image_url=img, cuisine=cui, difficulty=diff, prep_time=pt, cook_time=ct, servings=serv, diet_type=diet, rating=rat, popularity=pop, source="seed")
            db.add(recipe)
            db.commit()
            db.refresh(recipe)
            for ing_name in ings:
                if ing_name in db_ingredients:
                    ri = RecipeIngredient(recipe_id=recipe.id, ingredient_id=db_ingredients[ing_name].id, quantity=1, unit="cup")
                    db.add(ri)
            db.commit()

    add_recipe(
        "Ultimate Fresh Fruit Salad",
        "A refreshing and sweet mix of fresh fruits with a citrus glaze.",
        "1. Chop all fruits.\n2. Whisk juice and sugar.\n3. Toss and chill.",
        "https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?w=800",
        "Global", "Easy", 20, 0, 6, "Vegan", 4.9, 350,
        ["orange slices", "orange zest", "blueberries", "pineapple", "strawberries", "kiwi", "brown sugar", "orange juice", "grapes", "lemon juice", "lemon zest", "bananas", "extract"]
    )
    
    add_recipe(
        "Honey Lime Berry Citrus Splash",
        "A tangy and sweet fruit bowl drizzled with honey and fresh lime.",
        "1. Dice the fruit.\n2. Mix honey and lime juice.\n3. Pour over fruit and garnish with mint.",
        "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800",
        "Global", "Easy", 15, 0, 4, "Vegetarian", 4.7, 200,
        ["strawberries", "blueberries", "kiwi", "pineapple", "honey", "lime juice", "mint", "grapes"]
    )

    add_recipe(
        "Tropical Yogurt Fruit Bowl",
        "Creamy yogurt topped with a vibrant mix of tropical fruits.",
        "1. Scoop yogurt into bowls.\n2. Top with chopped pineapple, kiwi, bananas, and strawberries.\n3. Drizzle with honey.",
        "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800",
        "Global", "Easy", 10, 0, 2, "Vegetarian", 4.6, 180,
        ["yogurt", "pineapple", "kiwi", "bananas", "strawberries", "honey"]
    )

    add_recipe(
        "Classic Spaghetti Bolognese",
        "A rich, slow-cooked Italian meat sauce served over pasta.",
        "1. Heat olive oil and sauté onions.\n2. Brown beef.\n3. Add tomatoes and simmer.",
        "https://images.unsplash.com/photo-1626844131082-256783844137?w=800",
        "Italian", "Medium", 15, 60, 4, "Non-Vegetarian", 4.8, 500,
        ["beef", "tomato", "onion", "garlic", "pasta", "olive oil", "salt", "pepper", "cheese"]
    )

    print("Database successfully seeded with standard recipes!")
    db.close()

if __name__ == "__main__":
    seed()
