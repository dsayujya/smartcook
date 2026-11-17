import re

PANTRY_STAPLES = {
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
    # Pantry Aromatics & Fresh Herbs
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

SYNONYMS = {
    "noodles": {"noodles", "hakka noodles", "veg hakka noodles", "noodle"},
    "capsicum": {"capsicum", "bell pepper", "green bell pepper", "green capsicum", "green bell pepper (capsicum)"},
    "carrot": {"carrot", "carrots"},
    "onion": {"onion", "onions", "spring onion", "green onion"},
    "cabbage": {"cabbage"},
}

def is_pantry(name):
    lower = name.lower().strip()
    for p in PANTRY_STAPLES:
        if re.search(r'\b' + re.escape(p) + r'\b', lower):
            return True
    return False

def matches(u, r):
    r_lower = r.lower().strip()
    syns = SYNONYMS.get(u, {u})
    for s in syns:
        if re.search(r'\b' + re.escape(s) + r'\b', r_lower):
            return True
    return False

hakka_db = ['ginger', 'capsicum', 'salt oil', 'pepper powder', 'carrot', 'green onion', 'soy sauce', 'red chilli sauce', 'chilli vinegar', 'onion', 'cabbage spoon', 'green beans spoon', 'hakka noodles packet']
samosa_db = ['sweet spicy red chilli sauce', 'salt', 'wheat flour', 'rice vermicelli noodles', 'green beans', 'ginger', 'green chilli', 'ghee', 'spring onion greens stalks', 'cloves garlic', 'carrot', 'black pepper powder', 'green bell pepper', 'cabbage']

test_inputs = [
    ['noodles', 'cabbage', 'carrot', 'capsicum'],
    ['noodles', 'cabbage', 'capsicum', 'onion'],
    ['noodles', 'cabbage', 'carrot', 'onion'],
    ['noodles', 'cabbage', 'carrot', 'capsicum', 'onion'],
    ['noodles', 'cabbage', 'capsicum'],
]

def eval_recipe(recipe_ings, user_ings, mode='basket_use'):
    core_ingredients = [i for i in recipe_ings if not is_pantry(i)]
    matched_core = [i for i in core_ingredients if any(matches(a, i) for a in user_ings)]
    missing_core = [i for i in core_ingredients if i not in matched_core]
    used_user = [a for a in user_ings if any(matches(a, i) for i in recipe_ings)]
    
    basket_coverage = len(used_user) / len(user_ings)
    core_precision = len(matched_core) / len(core_ingredients) if core_ingredients else 0.0
    
    missing_count = len(missing_core)
    if missing_count == 0: penalty = 0.0
    elif missing_count == 1: penalty = 0.08
    elif missing_count == 2: penalty = 0.20
    else: penalty = 0.35 + 0.08 * (missing_count - 3)
    
    if mode == 'basket_use':
        raw_score = (0.55 * basket_coverage) + (0.45 * core_precision) - penalty
    else:
        raw_score = (0.30 * basket_coverage) + (0.70 * core_precision) - (penalty * 1.5)
        
    return int(max(0.05, min(1.0, raw_score)) * 100), len(missing_core), len(used_user)

for u_ing in test_inputs:
    h_score, h_miss, h_used = eval_recipe(hakka_db, u_ing, 'basket_use')
    s_score, s_miss, s_used = eval_recipe(samosa_db, u_ing, 'basket_use')
    print(f"Inputs: {u_ing}")
    print(f"  Hakka Noodles: {h_score}% (missing core: {h_miss}, used: {h_used})")
    print(f"  Chinese Samosa: {s_score}% (missing core: {s_miss}, used: {s_used})")
    print()
