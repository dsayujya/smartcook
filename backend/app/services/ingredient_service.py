from typing import List
from sqlalchemy.orm import Session
from app.models.domain import Ingredient, IngredientSynonym

class IngredientService:
    @staticmethod
    def normalize_ingredient_name(name: str) -> str:
        """
        Lowercases, strips, and removes common unnecessary words.
        In a full implementation, this could use NLTK for lemmatization.
        """
        name = name.lower().strip()
        # Basic removal of common adjectives for simplicity
        words_to_remove = ["fresh", "chopped", "diced", "sliced", "green", "red", "yellow"]
        for word in words_to_remove:
            if name.startswith(word + " "):
                name = name.replace(word + " ", "", 1)
        return name.strip()

    @staticmethod
    def get_canonical_name(db: Session, raw_name: str) -> str:
        """
        Normalizes the name and checks the database for synonyms.
        """
        normalized = IngredientService.normalize_ingredient_name(raw_name)
        
        # Check if it's a known synonym in the database
        synonym = db.query(IngredientSynonym).filter(IngredientSynonym.synonym_name == normalized).first()
        if synonym:
            canonical_ingredient = db.query(Ingredient).filter(Ingredient.id == synonym.canonical_id).first()
            if canonical_ingredient:
                return canonical_ingredient.name
        
        # Hardcoded fallbacks for MVP if database is empty
        fallbacks = {
            "bell pepper": "capsicum",
            "tomatoes": "tomato",
            "potatoes": "potato",
            "onions": "onion"
        }
        return fallbacks.get(normalized, normalized)

    @staticmethod
    def process_detected_ingredients(db: Session, raw_ingredients: List[str]) -> List[str]:
        """
        Takes a list of raw detected strings and returns canonical names.
        """
        canonical_list = set()
        for raw in raw_ingredients:
            canonical = IngredientService.get_canonical_name(db, raw)
            canonical_list.add(canonical)
        return list(canonical_list)
