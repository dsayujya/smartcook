from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    phone_number = Column(String, unique=True, index=True, nullable=True)
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    google_id = Column(String, unique=True, index=True, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    favorites = relationship("Favorite", back_populates="user")
    history = relationship("History", back_populates="user")

class OTPVerification(Base):
    __tablename__ = "otp_verifications"
    id = Column(Integer, primary_key=True, index=True)
    target = Column(String, index=True) # Email or Phone string
    otp_code = Column(String)
    otp_type = Column(String, default="email_verification") # email_verification, phone_verification, login
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    diet_type = Column(String, nullable=True) # e.g. Vegetarian, Vegan
    cuisine_preference = Column(String, nullable=True)
    max_cooking_time = Column(Integer, nullable=True) # in minutes
    difficulty_preference = Column(String, nullable=True)

    user = relationship("User", back_populates="preferences")

class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # Normalized name

class IngredientSynonym(Base):
    __tablename__ = "ingredient_synonyms"
    id = Column(Integer, primary_key=True, index=True)
    synonym_name = Column(String, unique=True, index=True)
    canonical_id = Column(Integer, ForeignKey("ingredients.id"))

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    instructions = Column(Text)
    image_url = Column(String, nullable=True)
    cuisine = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    prep_time = Column(Integer, nullable=True) # in minutes
    cook_time = Column(Integer, nullable=True)
    servings = Column(Integer, nullable=True)
    diet_type = Column(String, nullable=True)
    rating = Column(Float, default=0.0)
    popularity = Column(Integer, default=0)
    source = Column(String, default="seed")  # "seed" for curated, "csv_import" for bulk imports
    meal_type = Column(String, default="savoury", index=True)  # "sweet" or "savoury"

    ingredients = relationship("RecipeIngredient", back_populates="recipe")

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"))
    quantity = Column(Float, nullable=True)
    unit = Column(String, nullable=True)

    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient")

class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(Integer, ForeignKey("recipes.id"))

    user = relationship("User", back_populates="favorites")
    recipe = relationship("Recipe")

class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    viewed_at = Column(String) # Simple timestamp

    user = relationship("User", back_populates="history")
    recipe = relationship("Recipe")
