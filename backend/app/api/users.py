from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.domain import UserPreference, Favorite, History, Recipe
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])

# Schemas specifically for these endpoints
class UserPreferenceUpdate(BaseModel):
    diet_type: str = None
    cuisine_preference: str = None
    max_cooking_time: int = None
    difficulty_preference: str = None

class FavoriteCreate(BaseModel):
    recipe_id: int

@router.put("/{user_id}/preferences")
def update_preferences(user_id: int, prefs: UserPreferenceUpdate, db: Session = Depends(get_db)):
    db_pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if not db_pref:
        db_pref = UserPreference(user_id=user_id)
        db.add(db_pref)
    
    if prefs.diet_type: db_pref.diet_type = prefs.diet_type
    if prefs.cuisine_preference: db_pref.cuisine_preference = prefs.cuisine_preference
    if prefs.max_cooking_time: db_pref.max_cooking_time = prefs.max_cooking_time
    if prefs.difficulty_preference: db_pref.difficulty_preference = prefs.difficulty_preference
    
    db.commit()
    return {"message": "Preferences updated"}

@router.post("/{user_id}/favorites")
def add_favorite(user_id: int, fav: FavoriteCreate, db: Session = Depends(get_db)):
    existing = db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.recipe_id == fav.recipe_id).first()
    if not existing:
        new_fav = Favorite(user_id=user_id, recipe_id=fav.recipe_id)
        db.add(new_fav)
        db.commit()
    return {"message": "Favorite added"}

@router.get("/{user_id}/favorites")
def get_favorites(user_id: int, db: Session = Depends(get_db)):
    favorites = db.query(Favorite).filter(Favorite.user_id == user_id).all()
    # In a full app, return serialized recipes here
    return [{"recipe_id": f.recipe_id} for f in favorites]

@router.get("/{user_id}/history")
def get_history(user_id: int, db: Session = Depends(get_db)):
    history = db.query(History).filter(History.user_id == user_id).all()
    return [{"recipe_id": h.recipe_id, "viewed_at": h.viewed_at} for h in history]
