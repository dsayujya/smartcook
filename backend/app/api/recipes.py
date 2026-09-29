from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.recommendation_engine import RecommendationEngine
from app.schemas.schemas import RecipeRecommendation, Recipe as RecipeSchema
from app.models.domain import Recipe

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.post("/recommend", response_model=List[RecipeRecommendation])
def recommend_recipes(
    ingredients: List[str],
    cuisine: Optional[str] = Query(None, description="Filter by cuisine (e.g. 'Indian', 'Italian')"),
    meal_type: Optional[str] = Query(None, description="Filter by meal type: 'sweet' or 'savoury'"),
    max_cooking_time: Optional[int] = Query(None, description="Max cooking time in minutes"),
    db: Session = Depends(get_db)
):
    """
    Takes a confirmed list of ingredients and recommends recipes.
    Supports optional filters for cuisine, meal type, and max cooking time.
    """
    engine = RecommendationEngine(db)
    
    preferences = {}
    if max_cooking_time:
        preferences['max_cooking_time'] = max_cooking_time

    # Build filters dict from query params
    filters = {}
    if cuisine:
        filters['cuisine'] = cuisine
    if meal_type:
        filters['meal_type'] = meal_type
    if max_cooking_time:
        filters['max_cook_time'] = max_cooking_time
        
    recommendations = engine.rank_recipes(ingredients, preferences, filters if filters else None)
    return recommendations

@router.get("/{recipe_id}", response_model=RecipeSchema)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe
