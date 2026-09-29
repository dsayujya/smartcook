from app.database import SessionLocal
from app.services.recommendation_engine import RecommendationEngine

db = SessionLocal()
engine = RecommendationEngine(db)

ings = ["tomato", "potato", "onion", "capsicum"]
print("Available ingredients:", ings)
recs = engine.rank_recipes(ings)

for r in recs:
    print(f"Recipe: {r.recipe.name}, Match: {r.match_percentage}, Score: {r.score}")
    print(f"Ingredients: {[i.ingredient.name for i in r.recipe.ingredients]}")
    print("---")
