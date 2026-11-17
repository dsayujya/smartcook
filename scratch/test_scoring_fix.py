import re

# Enhanced PANTRY_STAPLES including Asian/Indo-Chinese sauces & seasonings
PANTRY_STAPLES = {
    # Salts & Waters
    "salt", "black salt", "rock salt", "sea salt", "sendha namak", "kala namak",
    "water", "ice",
    # Oils & Cooking Fats
    "oil", "cooking oil", "vegetable oil", "sunflower oil", "olive oil", "mustard oil",
    "sesame oil", "canola oil", "peanut oil", "ghee", "butter", "cooking spray", "salt oil",
    # Core Ground & Whole Spices
    "turmeric", "turmeric powder", "haldi",
    "red chilli powder", "chilli powder", "degi mirch", "kashmiri chilli powder", "kashmiri red chilli powder",
    "paprika", "red chilli flakes", "chilli flakes", "cayenne pepper",
    "black pepper", "black pepper powder", "black peppercorns", "white pepper powder", "peppercorns", "pepper powder", "white pepper",
    "cumin", "cumin seeds", "cumin powder", "jeera", "shahi jeera",
    "coriander powder", "dhania powder",
    "garam masala", "garam masala powder", "kitchen king masala", "sabzi masala",
    "mustard seeds", "rai", "sarson", "asafoetida", "hing",
    # Pantry Aromatics & Fresh Herbs
    "ginger", "garlic", "ginger garlic paste", "cloves garlic",
    "green chilli", "green chillies", "green chili",
    "lemon", "lemon juice", "lime juice",
    # Common Sauces, Vinegars & Condiments
    "vinegar", "chilli vinegar", "white vinegar", "apple cider vinegar",
    "soy sauce", "dark soy sauce", "light soy sauce",
    "red chilli sauce", "green chilli sauce", "chilli sauce", "chili sauce", "hot sauce", "schezwan sauce",
    "tomato ketchup", "tomato sauce",
    "sugar", "jaggery", "honey", "msg", "ajinomoto"
}

SYNONYMS = {
    "noodles": {"noodles", "hakka noodles", "veg hakka noodles", "noodle", "chowmein"},
    "capsicum": {"capsicum", "bell pepper", "green bell pepper", "green capsicum", "green bell pepper (capsicum)"},
    "carrot": {"carrot", "carrots"},
    "onion": {"onion", "onions", "spring onion", "green onion"},
    "cabbage": {"cabbage"},
}

def clean_ing_name(name):
    clean = re.sub(r'\b(spoon|packet|stalks|leaves|stalk|bulb|greens)\b', '', name.lower())
    return clean.strip()

def is_pantry(name):
    lower = clean_ing_name(name)
    for p in PANTRY_STAPLES:
        if re.search(r'\b' + re.escape(p) + r'\b', lower):
            return True
    return False

def matches(u, r):
    r_lower = clean_ing_name(r)
    syns = SYNONYMS.get(u, {u})
    for s in syns:
        if re.search(r'\b' + re.escape(s) + r'\b', r_lower):
            return True
    return False

def score_with_hero_boost(title, recipe_ings, user_ings, mode='basket_use'):
    core_ingredients = [i for i in recipe_ings if not is_pantry(i)]
    matched_core = [i for i in core_ingredients if any(matches(a, i) for a in user_ings)]
    missing_core = [i for i in core_ingredients if i not in matched_core]
    used_user = [a for a in user_ings if any(matches(a, i) for i in recipe_ings)]
    
    basket_coverage = len(used_user) / len(user_ings)
    core_precision = len(matched_core) / len(core_ingredients) if core_ingredients else 0.0
    
    missing_count = len(missing_core)
    if missing_count == 0: penalty = 0.0
    elif missing_count == 1: penalty = 0.08
    elif missing_count == 2: penalty = 0.18
    else: penalty = 0.30 + 0.08 * (missing_count - 3)
    
    raw_score = (0.50 * basket_coverage) + (0.50 * core_precision) - penalty
    
    # Title / Hero Ingredient Boost:
    # If the user has noodles and the recipe title is "Noodles", boost it!
    t_lower = title.lower()
    for u in user_ings:
        if len(u) > 3 and re.search(r'\b' + re.escape(u) + r'\b', t_lower):
            raw_score += 0.15 # 15% Hero Boost!
            break
            
    # Samosa penalty: If recipe has "samosa", "momo", "pie" and user doesn't have flour / dough
    if ("samosa" in t_lower or "momo" in t_lower) and not any(f in user_ings for f in ['flour', 'maida', 'wheat flour']):
        raw_score -= 0.25 # Missing base wrap!
        
    final_score = int(max(0.05, min(1.0, raw_score)) * 100)
    print(f"=== {title} ===")
    print(f"  Core Ingredients: {core_ingredients}")
    print(f"  Matched Core: {matched_core}")
    print(f"  Missing Core: {missing_core}")
    print(f"  Basket: {basket_coverage:.2f}, Core Prec: {core_precision:.2f}, Penalty: {penalty:.2f}")
    print(f"  Final Match Score: {final_score}%\n")

user_ings = ['noodles', 'cabbage', 'capsicum', 'onion']
hakka_db = ['ginger', 'capsicum', 'salt oil', 'pepper powder', 'carrot', 'green onion', 'soy sauce', 'red chilli sauce', 'chilli vinegar', 'onion', 'cabbage spoon', 'green beans spoon', 'hakka noodles packet']
samosa_db = ['sweet spicy red chilli sauce', 'salt', 'wheat flour', 'rice vermicelli noodles', 'green beans', 'ginger', 'green chilli', 'ghee', 'spring onion greens stalks', 'cloves garlic', 'carrot', 'black pepper powder', 'green bell pepper', 'cabbage']

score_with_hero_boost("Vegetarian Hakka Noodles Recipe", hakka_db, user_ings)
score_with_hero_boost("Vegetarian Chinese Samosa Recipe", samosa_db, user_ings)
