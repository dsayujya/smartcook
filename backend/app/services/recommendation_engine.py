import logging
import re
from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, select, or_
from app.models.domain import Recipe, RecipeIngredient, Ingredient
from app.schemas.schemas import RecipeRecommendation, Recipe as RecipeSchema, RecipeIngredientDetail, Ingredient as IngredientSchema

try:
    from sentence_transformers import SentenceTransformer, util
    _model = None  # Lazy-loaded

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


# ==============================================================================
# Domain Knowledge: Common Kitchen Pantry Staples & Spices
# ==============================================================================
PANTRY_STAPLES: Set[str] = {
    # Salts & Waters
    "salt", "black salt", "rock salt", "sea salt", "sendha namak", "kala namak",
    "water", "ice",
    
    # Oils & Cooking Fats
    "oil", "cooking oil", "vegetable oil", "sunflower oil", "olive oil", "mustard oil",
    "sesame oil", "canola oil", "peanut oil", "ghee", "butter", "cooking spray",
    
    # Core Ground & Whole Spices
    "turmeric", "turmeric powder", "haldi",
    "red chilli powder", "chilli powder", "degi mirch", "kashmiri chilli powder", "kashmiri red chilli powder",
    "paprika", "red chilli flakes", "chilli flakes", "cayenne pepper",
    "black pepper", "black pepper powder", "black peppercorns", "white pepper powder", "peppercorns",
    "cumin", "cumin seeds", "cumin powder", "jeera", "shahi jeera",
    "coriander powder", "dhania powder",
    "garam masala", "garam masala powder", "kitchen king masala", "sabzi masala",
    "mustard seeds", "rai", "sarson",
    "asafoetida", "hing",
    "fennel seeds", "saunf",
    "fenugreek seeds", "methi dana",
    "carom seeds", "ajwain",
    "cloves", "laung", "cinnamon", "cinnamon stick", "dalchini",
    "cardamom", "green cardamom", "black cardamom", "elaichi", "cardamom pods",
    "bay leaf", "bay leaves", "tej patta",
    "star anise", "mace", "javitri", "nutmeg", "jaiphal",
    
    # Pantry Aromatics & Fresh Herbs (usually standard in home kitchens)
    "curry leaves", "kadi patta",
    "coriander leaves", "fresh coriander", "cilantro", "dhania leaves",
    "mint leaves", "pudina",
    "ginger", "garlic", "ginger garlic paste", "cloves garlic",
    "green chilli", "green chillies", "green chili",
    "lemon", "lemon juice", "lime juice",
    
    # Seasoning Powders & Extracts
    "kasuri methi", "dry fenugreek leaves",
    "amchur", "dry mango powder", "amchur powder",
    "chaat masala", "chaat masala powder",
    "oregano", "mixed herbs", "italian seasoning", "rosemary", "thyme", "basil",
    "sugar", "jaggery", "honey",
    "baking soda", "baking powder", "yeast",
    "vanilla extract", "vinegar", "soy sauce"
}

# ==============================================================================
# Synonym Groups (Canonical & Vernacular Mapping)
# ==============================================================================
SYNONYM_GROUPS = [
    # Produce & Alliums
    {"capsicum", "bell pepper", "green bell pepper", "red bell pepper", "yellow bell pepper", "green capsicum", "shimla mirch", "capsicums"},
    {"potato", "potatoes", "baby potatoes", "baby potato", "aloo", "batata"},
    {"sweet potato", "sweet potatoes", "shakarkandi"},
    {"tomato", "tomatoes", "tamatar", "cherry tomato", "cherry tomatoes"},
    {"onion", "onions", "pyaz", "shallot", "shallots", "red onion", "white onion"},
    {"spring onion", "spring onions", "scallion", "scallions", "green onion", "green onions"},
    {"garlic", "garlic cloves", "cloves garlic", "lahsun"},
    {"ginger", "adrak", "ginger root"},
    {"ginger garlic paste", "ginger garlic"},
    {"eggplant", "brinjal", "aubergine", "baingan"},
    
    # Herbs & Chillies
    {"chilli", "chillies", "chili", "chilies", "green chilli", "green chillies", "green chili", "mirch", "hari mirch"},
    {"red chilli", "red chillies", "dry red chillies", "lal mirch"},
    {"coriander", "coriander leaves", "cilantro", "dhania", "dhania leaves", "fresh coriander"},
    {"mint", "mint leaves", "pudina"},
    {"curry leaves", "kadi patta", "curry leaf"},
    {"fenugreek leaves", "methi", "methi leaves", "kasuri methi"},
    
    # Dairy, Poultry & Proteins
    {"egg", "eggs", "anda"},
    {"paneer", "cottage cheese", "chenna"},
    {"curd", "yogurt", "yoghurt", "dahi"},
    {"milk", "doodh"},
    {"cheese", "cheddar cheese", "mozzarella cheese", "processed cheese"},
    {"butter", "makhan"},
    {"ghee", "clarified butter"},
    {"chicken", "murgh"},
    {"mutton", "lamb", "goat meat"},
    {"fish", "machhli"},
    {"prawns", "shrimp"},
    {"tofu", "bean curd"},
    
    # Grains, Flours & Bases
    {"rice", "basmati rice", "chawal", "cooked rice", "brown rice"},
    {"wheat flour", "atta", "whole wheat flour", "gehun ka atta"},
    {"maida", "all purpose flour", "plain flour"},
    {"besan", "gram flour", "chickpea flour"},
    {"suji", "sooji", "semolina", "rava"},
    {"pasta", "macaroni", "spaghetti", "penne"},
    {"noodles", "hakka noodles"},
    {"bread", "bread slices", "white bread", "brown bread", "pav"},
    {"idli batter", "dosa batter", "idli dosa batter"},
    {"oats", "rolled oats"},
    {"poha", "flattened rice"},
    
    # Legumes & Pulses
    {"chickpeas", "chana", "kabuli chana", "white chickpeas", "garbanzo beans"},
    {"kala chana", "black chickpeas", "brown chickpeas"},
    {"rajma", "kidney beans"},
    {"dal", "daal", "lentils"},
    {"toor dal", "arhar dal", "pigeon pea"},
    {"moong dal", "yellow moong dal", "green moong dal", "mung beans"},
    {"urad dal", "black gram"},
    {"chana dal", "bengal gram"},
    {"masoor dal", "red lentils"},
    
    # Other Common Vegetables
    {"cauliflower", "gobi", "gobhi", "phool gobi"},
    {"cabbage", "patta gobi", "bandh gobi"},
    {"peas", "green peas", "matar", "mutter"},
    {"carrot", "carrots", "gajar"},
    {"spinach", "palak"},
    {"mushroom", "mushrooms", "khumb"},
    {"lady finger", "okra", "bhindi"},
    {"corn", "sweet corn", "corn kernels", "makka"},
    {"cucumber", "kheera"},
    {"beetroot", "chukandar"},
    {"bottle gourd", "lauki", "doodhi"},
    {"bitter gourd", "karela"},
    {"beans", "french beans", "green beans"},
    {"lemon", "lime", "nimbu", "lemon juice", "lime juice"},
    {"coconut", "grated coconut", "nariyal"},
]

SYNONYM_LOOKUP: Dict[str, Set[str]] = {}
for group in SYNONYM_GROUPS:
    for item in group:
        SYNONYM_LOOKUP[item.lower()] = group


def get_synonyms(term: str) -> Set[str]:
    term_lower = term.lower().strip()
    return SYNONYM_LOOKUP.get(term_lower, {term_lower})


def is_pantry_ingredient(name: str) -> bool:
    """Check if an ingredient name is classified as a pantry staple/seasoning."""
    lower = name.lower().strip()
    for p in PANTRY_STAPLES:
        if re.search(r'\b' + re.escape(p) + r'\b', lower):
            return True
    return False


def matches_ingredient(avail_ing: str, recipe_ing: str) -> bool:
    """
    Robust word-boundary & synonym ingredient matcher.
    Prevents false substrings (e.g. 'oil' in 'boiled', 'corn' in 'peppercorns').
    """
    avail_terms = get_synonyms(avail_ing)
    rec_lower = recipe_ing.lower().strip()
    
    for term in avail_terms:
        # Whole word match
        if re.search(r'\b' + re.escape(term) + r'\b', rec_lower):
            return True
        # Basic morphological plural/singular check
        if term.endswith('s') and len(term) > 3:
            stem = term[:-1]
            if re.search(r'\b' + re.escape(stem) + r'\b', rec_lower):
                return True
        elif not term.endswith('s'):
            plural = term + 's'
            if re.search(r'\b' + re.escape(plural) + r'\b', rec_lower):
                return True
                
    return False


class RecommendationEngine:
    def __init__(self, db: Session):
        self.db = db

    def _fetch_candidate_recipes(self, available_ingredients: List[str], filters: Dict[str, Any] = None) -> List[Recipe]:
        """
        SQL-level pre-filter with expanded synonym roots:
        Orders candidate recipes by the number of matching ingredients and limits to the top 150
        candidates to avoid transferring thousands of records across the network, dropping response
        time from 80+ seconds to < 1.5 seconds.
        """
        lower_ingredients = [i.lower().strip() for i in available_ingredients if i.strip()]
        if not lower_ingredients:
            return []

        # Expand search terms with all synonyms
        expanded_terms = set(lower_ingredients)
        for ing in lower_ingredients:
            expanded_terms.update(get_synonyms(ing))

        # Build base subquery to rank recipes by number of shared ingredients
        base_subquery = (
            select(
                RecipeIngredient.recipe_id,
                func.count(RecipeIngredient.ingredient_id).label("match_count")
            )
            .join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id)
            .where(
                or_(
                    Ingredient.name.in_(list(expanded_terms)),
                    *(Ingredient.name.ilike(f"%{ing}%") for ing in lower_ingredients)
                )
            )
        )

        if filters:
            base_subquery = base_subquery.join(Recipe, RecipeIngredient.recipe_id == Recipe.id)
            if filters.get('cuisine'):
                base_subquery = base_subquery.where(Recipe.cuisine.ilike(f"%{filters['cuisine']}%"))
            if filters.get('meal_type'):
                base_subquery = base_subquery.where(Recipe.meal_type == filters['meal_type'])
            if filters.get('max_cook_time'):
                base_subquery = base_subquery.where(Recipe.cook_time <= filters['max_cook_time'])

        candidate_ids = (
            base_subquery
            .group_by(RecipeIngredient.recipe_id)
            .order_by(func.count(RecipeIngredient.ingredient_id).desc())
            .limit(150)
            .subquery()
        )

        recipes = (
            self.db.query(Recipe)
            .filter(Recipe.id.in_(select(candidate_ids.c.recipe_id)))
            .options(
                joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient)
            )
            .all()
        )

        return recipes

    def _batch_similarity(self, query_text: str, recipe_texts: List[str]) -> List[float]:
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

    def rank_recipes(
        self,
        available_ingredients: List[str],
        user_preferences: Dict[str, Any] = None,
        filters: Dict[str, Any] = None,
        assume_pantry_staples: bool = True,
        ranking_mode: str = "basket_use",
        limit: int = 20
    ) -> List[RecipeRecommendation]:
        """
        Rank candidate recipes based on user ingredients, pantry assumptions, and ranking mode.
        
        ranking_mode:
          - "basket_use": Prioritize recipes utilizing the highest proportion of user ingredients.
          - "ready_to_cook": Prioritize recipes with fewest missing core ingredients.
        """
        cleaned_available = [i.strip() for i in available_ingredients if i.strip()]
        if not cleaned_available:
            return []

        # Stage 1: Fetch candidate recipes from database
        candidates_db = self._fetch_candidate_recipes(cleaned_available, filters)
        if not candidates_db:
            return []

        # Stage 2: Detailed recipe ingredient analysis
        scored_candidates = []
        for recipe in candidates_db:
            recipe_ing_names = [ri.ingredient.name for ri in recipe.ingredients]
            if not recipe_ing_names:
                continue

            # Classify recipe ingredients into core and pantry
            if assume_pantry_staples:
                core_ingredients = [i for i in recipe_ing_names if not is_pantry_ingredient(i)]
                if not core_ingredients:
                    core_ingredients = recipe_ing_names  # fallback
                pantry_ingredients = [i for i in recipe_ing_names if is_pantry_ingredient(i)]
            else:
                core_ingredients = recipe_ing_names
                pantry_ingredients = []

            # Check matches against available user ingredients
            matched_core = [
                i for i in core_ingredients 
                if any(matches_ingredient(a, i) for a in cleaned_available)
            ]
            missing_core = [i for i in core_ingredients if i not in matched_core]

            used_user_ingredients = [
                a for a in cleaned_available 
                if any(matches_ingredient(a, i) for i in recipe_ing_names)
            ]

            matched_pantry = [
                i for i in pantry_ingredients 
                if any(matches_ingredient(a, i) for a in cleaned_available)
            ]
            missing_pantry = [i for i in pantry_ingredients if i not in matched_pantry]

            if not used_user_ingredients:
                continue

            # Metrics
            basket_coverage = len(used_user_ingredients) / len(cleaned_available)
            core_precision = len(matched_core) / len(core_ingredients) if core_ingredients else 0.0

            # Missing core penalty
            missing_count = len(missing_core)
            if missing_count == 0:
                penalty = 0.0
            elif missing_count == 1:
                penalty = 0.08
            elif missing_count == 2:
                penalty = 0.20
            else:
                penalty = 0.35 + 0.08 * (missing_count - 3)

            # Weighting by mode
            if ranking_mode == "basket_use":
                # Heavily reward using user's basket items
                raw_score = (0.55 * basket_coverage) + (0.45 * core_precision) - penalty
            else:  # ready_to_cook
                # Heavily reward recipes you can make right now
                raw_score = (0.30 * basket_coverage) + (0.70 * core_precision) - (penalty * 1.5)

            # Small adjustments for popularity & rating
            popularity_boost = min(recipe.popularity / 2000.0, 0.03)
            rating_boost = min(recipe.rating / 50.0, 0.03)
            raw_score += (popularity_boost + rating_boost)

            # Cooking time preference penalty if exceeded
            if user_preferences and user_preferences.get('max_cooking_time') and recipe.cook_time:
                if recipe.cook_time > user_preferences['max_cooking_time']:
                    raw_score -= 0.15

            display_match = max(0.05, min(1.0, raw_score))

            scored_candidates.append({
                "recipe": recipe,
                "display_match": display_match,
                "score": raw_score,
                "used_ingredients": used_user_ingredients,
                "missing_core": missing_core,
                "missing_pantry": missing_pantry,
                "all_missing": missing_core if assume_pantry_staples else (missing_core + missing_pantry),
                "matched_core": matched_core,
            })

        if not scored_candidates:
            return []

        # Stage 3: Sort candidates based on ranking mode
        if ranking_mode == "basket_use":
            # Prioritize recipes utilizing the most user ingredients, then least missing core, then score
            scored_candidates.sort(
                key=lambda x: (
                    -len(x["used_ingredients"]),
                    len(x["missing_core"]),
                    -x["score"]
                )
            )
        else:  # ready_to_cook
            # Prioritize recipes with 0-1 missing items, then basket utilization, then score
            scored_candidates.sort(
                key=lambda x: (
                    len(x["missing_core"]),
                    -len(x["used_ingredients"]),
                    -x["score"]
                )
            )

        top_candidates = scored_candidates[:limit]

        # Stage 4: Build Pydantic response models
        recommendations = []
        for cand in top_candidates:
            recipe = cand["recipe"]

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
                match_percentage=cand["display_match"],
                missing_ingredients=cand["all_missing"],
                score=cand["score"],
                used_ingredients=cand["used_ingredients"],
                missing_core_ingredients=cand["missing_core"],
                missing_pantry_ingredients=cand["missing_pantry"]
            ))

        return recommendations
