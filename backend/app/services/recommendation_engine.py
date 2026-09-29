import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, select
from app.models.domain import Recipe, RecipeIngredient, Ingredient
from app.schemas.schemas import RecipeRecommendation, Recipe as RecipeSchema, RecipeIngredientDetail, Ingredient as IngredientSchema

try:
    from sentence_transformers import SentenceTransformer, util
    _model = None  # Lazy-loaded to avoid cold-start penalty on import

    def _get_model():
        global _model
        if _model is None:
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        return _model
except ImportError:
    logging.warning("SentenceTransformers not installed. Similarity matching will be disabled.")
    _get_model = lambda: None
except Exception as e:
    logging.error(f"Error setting up SentenceTransformer: {e}")
    _get_model = lambda: None


class RecommendationEngine:
    def __init__(self, db: Session):
        self.db = db

    def _fetch_candidate_recipes(self, available_ingredients: List[str], filters: Dict[str, Any] = None) -> List[Recipe]:
        """
        SQL-level pre-filter: only fetch recipes that share at least one
        ingredient with the user's available list. Applies optional filters
        for cuisine, meal_type, and max_cook_time at the SQL level.
        Uses eager-loading to avoid N+1 queries.
        """
        lower_ingredients = [i.lower() for i in available_ingredients]

        # Subquery: find recipe IDs that have at least one matching ingredient
        matching_recipe_ids = (
            select(RecipeIngredient.recipe_id)
            .join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id)
            .where(Ingredient.name.in_(lower_ingredients))
            .distinct()
            .scalar_subquery()
        )

        # Build query with optional filters
        query = (
            self.db.query(Recipe)
            .filter(Recipe.id.in_(matching_recipe_ids))
        )

        if filters:
            if filters.get('cuisine'):
                # Fuzzy match: "Indian" matches "North Indian Recipes", etc.
                query = query.filter(Recipe.cuisine.ilike(f"%{filters['cuisine']}%"))
            if filters.get('meal_type'):
                query = query.filter(Recipe.meal_type == filters['meal_type'])
            if filters.get('max_cook_time'):
                query = query.filter(Recipe.cook_time <= filters['max_cook_time'])

        recipes = (
            query
            .options(
                joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient)
            )
            .all()
        )

        return recipes

    def _is_ingredient_match(self, available_ing: str, recipe_ing: str) -> bool:
        """Check if an available ingredient matches a recipe ingredient using substring matching."""
        return available_ing in recipe_ing or recipe_ing in available_ing

    def calculate_ingredient_match(self, available_ingredients: List[str], recipe_ingredients: List[str]) -> Dict[str, float]:
        """
        Returns a dict with precision, recall, f_score, and overlap_count.
        
        Precision = matched / total_recipe_ingredients  (how much of the recipe you can make)
        Recall    = matched / total_available_ingredients (how many of your ingredients are used)
        F-score   = F_beta with beta=0.5 (favours precision but penalises low recall)
        
        This prevents recipes with very few ingredients from being over-ranked:
        e.g. coffee (3 ingredients, 2 match) = 66% precision but low recall,
        vs. paneer butter masala (12 ingredients, 7 match) = 58% precision but high recall.
        """
        if not recipe_ingredients or not available_ingredients:
            return {"precision": 0.0, "recall": 0.0, "f_score": 0.0, "overlap_count": 0}
        
        available_list = [i.lower() for i in available_ingredients]
        recipe_list = [i.lower() for i in recipe_ingredients]
        
        # Count how many recipe ingredients are matched
        overlap_count = 0
        for r_ing in recipe_list:
            if any(self._is_ingredient_match(a_ing, r_ing) for a_ing in available_list):
                overlap_count += 1
        
        # Count how many available ingredients are used by this recipe
        used_count = 0
        for a_ing in available_list:
            if any(self._is_ingredient_match(a_ing, r_ing) for r_ing in recipe_list):
                used_count += 1
        
        precision = overlap_count / len(recipe_list)
        recall = used_count / len(available_list)
        
        # F-beta score with beta=0.5 (weighs precision 4x more than recall,
        # but still penalises recipes that use almost none of the user's ingredients)
        beta = 0.5
        if precision + recall > 0:
            f_score = (1 + beta**2) * (precision * recall) / ((beta**2 * precision) + recall)
        else:
            f_score = 0.0
        
        return {
            "precision": precision,
            "recall": recall,
            "f_score": f_score,
            "overlap_count": overlap_count
        }

    def get_missing_ingredients(self, available_ingredients: List[str], recipe_ingredients: List[str]) -> List[str]:
        available_list = [i.lower() for i in available_ingredients]
        recipe_list = [i.lower() for i in recipe_ingredients]
        
        missing = []
        for r_ing in recipe_list:
            if not any(self._is_ingredient_match(a_ing, r_ing) for a_ing in available_list):
                missing.append(r_ing)
        return missing

    def _batch_similarity(self, query_text: str, recipe_texts: List[str]) -> List[float]:
        """
        Compute cosine similarity between the query and ALL candidate recipe
        ingredient texts in a single batched encode call, instead of one-by-one.
        """
        model = _get_model()
        if not model or not recipe_texts:
            return [0.0] * len(recipe_texts)

        try:
            query_embedding = model.encode(query_text, convert_to_tensor=True)
            recipe_embeddings = model.encode(recipe_texts, convert_to_tensor=True, batch_size=64)
            scores = util.cos_sim(query_embedding, recipe_embeddings)[0]
            return [s.item() for s in scores]
        except Exception as e:
            logging.error(f"Error in batch similarity: {e}")
            return [0.0] * len(recipe_texts)

    def rank_recipes(self, available_ingredients: List[str], user_preferences: Dict[str, Any] = None, filters: Dict[str, Any] = None) -> List[RecipeRecommendation]:
        # Stage 1: SQL pre-filter — only fetch recipes sharing at least one ingredient + category filters
        candidate_db_recipes = self._fetch_candidate_recipes(available_ingredients, filters)

        if not candidate_db_recipes:
            return []

        # Stage 2: Fast keyword matching + collect candidates
        candidates = []
        for recipe in candidate_db_recipes:
            recipe_ingredient_names = [ri.ingredient.name for ri in recipe.ingredients]
            match_info = self.calculate_ingredient_match(available_ingredients, recipe_ingredient_names)
            
            if match_info["overlap_count"] <= 0:
                continue
                
            missing = self.get_missing_ingredients(available_ingredients, recipe_ingredient_names)
            candidates.append({
                "recipe": recipe,
                "names": recipe_ingredient_names,
                "match_info": match_info,
                "missing": missing
            })

        # Sort by f_score (balanced metric) and take top 50 for semantic re-ranking
        candidates.sort(key=lambda x: x["match_info"]["f_score"], reverse=True)
        top_candidates = candidates[:50]

        if not top_candidates:
            return []

        # Stage 3: Batched AI semantic re-ranking (single encode call for all candidates)
        query_text = " ".join(available_ingredients)
        recipe_texts = [" ".join(c["names"]) for c in top_candidates]
        similarities = self._batch_similarity(query_text, recipe_texts)

        # Stage 4: Scoring
        recommendations = []
        for i, cand in enumerate(top_candidates):
            recipe = cand["recipe"]
            match_info = cand["match_info"]
            missing = cand["missing"]
            similarity = similarities[i]
            
            # Use F-score as the primary ingredient match metric
            ingredient_score = match_info["f_score"]
            precision = match_info["precision"]
            
            # Weights — ingredient match dominates the ranking
            w_match = 0.75
            w_similarity = 0.10
            w_popularity = 0.05
            w_time = 0.10
            
            # Normalize popularity (curated recipes have higher default popularity)
            normalized_popularity = min(recipe.popularity / 1000.0, 1.0)
            
            time_score = 1.0
            if user_preferences and user_preferences.get('max_cooking_time') and recipe.cook_time:
                if recipe.cook_time > user_preferences['max_cooking_time']:
                    time_score = 0.5  # Penalty
                else:
                    time_score = 1.0
            
            final_score = (
                (w_match * ingredient_score) +
                (w_similarity * similarity) +
                (w_popularity * normalized_popularity) +
                (w_time * time_score)
            )
            
            # Display the final score as the match percentage so users see
            # the actual ranking metric, not just raw ingredient precision.
            display_match = final_score
            
            # Convert to Pydantic schemas for the response
            schema_ingredients = [
                RecipeIngredientDetail(
                    ingredient=IngredientSchema(id=ri.ingredient.id, name=ri.ingredient.name),
                    quantity=ri.quantity,
                    unit=ri.unit
                ) for ri in recipe.ingredients
            ]
            
            recipe_schema = RecipeSchema(
                id=recipe.id,
                name=recipe.name,
                description=recipe.description,
                instructions=recipe.instructions,
                image_url=recipe.image_url,
                cuisine=recipe.cuisine,
                difficulty=recipe.difficulty,
                prep_time=recipe.prep_time,
                cook_time=recipe.cook_time,
                servings=recipe.servings,
                diet_type=recipe.diet_type,
                rating=recipe.rating,
                popularity=recipe.popularity,
                source=recipe.source,
                meal_type=recipe.meal_type,
                ingredients=schema_ingredients
            )
            
            recommendations.append(RecipeRecommendation(
                recipe=recipe_schema,
                match_percentage=display_match,
                missing_ingredients=missing,
                score=final_score
            ))
                
        # Sort by final score descending
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:10]  # Top 10
