import json
import os
import re
from typing import Optional

# ==============================================================================
# 1. Exact Recipe Image Cache (Direct real photos per recipe)
# ==============================================================================
CACHE_FILE = os.path.join(os.path.dirname(__file__), "recipe_image_cache.json")
EXACT_IMAGE_CACHE = {}

def load_cache():
    global EXACT_IMAGE_CACHE
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                EXACT_IMAGE_CACHE = json.load(f)
        except Exception:
            EXACT_IMAGE_CACHE = {}

load_cache()

# ==============================================================================
# 2. Granular Dish-Specific Food Images (Fine-tuned to authentic preparations)
# ==============================================================================
DISH_KEYWORD_IMAGES = [
    # Indo-Chinese & Stir-Fried Noodles (Spicy Schezwan, Hakka, Chowmein - Wok stir-fry, NOT soup/ramen)
    (r"\b(schezwan|schezuan|hakka|chowmein|chow mein|stir fry noodle|fried noodle|veg noodle|vegetable noodle)\b", 
     "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=800&auto=format&fit=crop&q=80"),
    (r"\b(ramen|noodle soup|thukpa)\b", 
     "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800&auto=format&fit=crop&q=80"),
    (r"\b(noodle|noodles|maggi)\b", 
     "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=800&auto=format&fit=crop&q=80"),

    # Pastas & Italian
    (r"\b(pasta|spaghetti|macaroni|penne|lasagna|ravioli|fusilli)\b", 
     "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=800&auto=format&fit=crop&q=80"),
    (r"\b(pizza)\b", 
     "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&auto=format&fit=crop&q=80"),
    (r"\b(burger|sandwich|toast|panini|wrap|roll|frankie)\b", 
     "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&auto=format&fit=crop&q=80"),

    # Biryanis, Pulao & Rice Dishes
    (r"\b(biryani|dum biryani)\b", 
     "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&auto=format&fit=crop&q=80"),
    (r"\b(pulao|pulav|fried rice|jeera rice|tava pulao)\b", 
     "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?w=800&auto=format&fit=crop&q=80"),
    (r"\b(rice|khichdi|pongal|curd rice|lemon rice|tomato rice)\b", 
     "https://images.unsplash.com/photo-1516714435131-44d6b64dc6a2?w=800&auto=format&fit=crop&q=80"),

    # South Indian Breakfast & Breads
    (r"\b(dosa|masala dosa|idli|vada|medu vada|uttapam|appam|pesarattu)\b", 
     "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=800&auto=format&fit=crop&q=80"),
    (r"\b(paratha|roti|chapati|naan|puri|poori|kulcha|flatbread|thepla)\b", 
     "https://images.unsplash.com/photo-1626074353765-517a681e40be?w=800&auto=format&fit=crop&q=80"),

    # Dairy, Paneer & Cheeses
    (r"\b(paneer|shahi paneer|palak paneer|paneer butter masala|matar paneer|cottage cheese)\b", 
     "https://images.unsplash.com/photo-1567184109411-b28f21ee097a?w=800&auto=format&fit=crop&q=80"),

    # Poultry, Meat & Seafood
    (r"\b(chicken|murgh|tikka|tandoori|wings|kebab|kabab)\b", 
     "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=800&auto=format&fit=crop&q=80"),
    (r"\b(fish|prawn|prawns|shrimp|seafood|salmon|crab)\b", 
     "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=800&auto=format&fit=crop&q=80"),
    (r"\b(mutton|lamb|goat|keema|gosht|meat)\b", 
     "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&auto=format&fit=crop&q=80"),
    (r"\b(egg|eggs|omelette|omelet|egg curry|bhurji|anda)\b", 
     "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=800&auto=format&fit=crop&q=80"),

    # Dals, Legumes & Curries
    (r"\b(chole|chana|rajma|chickpea|chickpeas)\b", 
     "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&auto=format&fit=crop&q=80"),
    (r"\b(dal|daal|sambar|rasam|tadka|makhani|moong dal|toor dal|kootu)\b", 
     "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&auto=format&fit=crop&q=80"),
    (r"\b(karela|bitter gourd)\b", 
     "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=800&auto=format&fit=crop&q=80"),
    (r"\b(curry|gravy|korma|masala|salan)\b", 
     "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=800&auto=format&fit=crop&q=80"),
    (r"\b(sabzi|subzi|bhaji|poriyal|sukhi|stir fry|aloo|gobi|bhindi|baingan)\b", 
     "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800&auto=format&fit=crop&q=80"),

    # Soups & Salads
    (r"\b(soup|broth|shorba|chowder)\b", 
     "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800&auto=format&fit=crop&q=80"),
    (r"\b(salad|raita|kachumber|slaw)\b", 
     "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&auto=format&fit=crop&q=80"),
    (r"\b(chutney|dip|pachadi|sauce)\b", 
     "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800&auto=format&fit=crop&q=80"),

    # Desserts, Sweets & Bakery
    (r"\b(cake|cupcake|muffin|pastry|brownie|pie|tart)\b", 
     "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800&auto=format&fit=crop&q=80"),
    (r"\b(halwa|kheer|payasam|ladoo|laddu|barfi|gulab jamun|rasgulla|pudding|ice cream|dessert|sweet)\b", 
     "https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=800&auto=format&fit=crop&q=80"),
    (r"\b(cookie|cookies|biscuit|biscuits)\b", 
     "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=800&auto=format&fit=crop&q=80"),

    # Beverages & Drinks
    (r"\b(tea|chai|coffee|latte|smoothie|shake|juice|drink|sharbat|lassi)\b", 
     "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=800&auto=format&fit=crop&q=80"),
]

CUISINE_FALLBACK_IMAGES = {
    "italian": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=800&auto=format&fit=crop&q=80",
    "mexican": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=800&auto=format&fit=crop&q=80",
    "south indian": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=800&auto=format&fit=crop&q=80",
    "north indian": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&auto=format&fit=crop&q=80",
    "punjabi": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&auto=format&fit=crop&q=80",
    "chinese": "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=800&auto=format&fit=crop&q=80",
    "indo chinese": "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=800&auto=format&fit=crop&q=80",
    "asian": "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?w=800&auto=format&fit=crop&q=80",
    "thai": "https://images.unsplash.com/photo-1559847844-5315695dadae?w=800&auto=format&fit=crop&q=80",
    "continental": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&auto=format&fit=crop&q=80",
    "bengali": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=800&auto=format&fit=crop&q=80",
    "kerala": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=800&auto=format&fit=crop&q=80",
    "maharashtrian": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&auto=format&fit=crop&q=80",
    "rajasthani": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&auto=format&fit=crop&q=80",
    "gujarati": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&auto=format&fit=crop&q=80",
}

DEFAULT_FOOD_IMAGE = "https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=800&auto=format&fit=crop&q=80"
DEFAULT_SWEET_IMAGE = "https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=800&auto=format&fit=crop&q=80"


def is_problematic_image_url(url: Optional[str]) -> bool:
    """Check if an image URL is empty, invalid, or hosted on the blocked www.archanaskitchen.com host."""
    if not url or not isinstance(url, str):
        return True
    url_stripped = url.strip().lower()
    if not url_stripped or not url_stripped.startswith("http"):
        return True
    # The old www.archanaskitchen.com blocks mobile clients with 403 Forbidden
    if "www.archanaskitchen.com" in url_stripped:
        return True
    if "localhost" in url_stripped or "127.0.0.1" in url_stripped:
        return True
    return False


def get_reliable_image_url(
    recipe_name: str,
    cuisine: Optional[str] = None,
    meal_type: Optional[str] = None,
    raw_image_url: Optional[str] = None
) -> str:
    """
    Returns an exact, authentic recipe image if available, or a fine-tuned dish-specific image.
    1. Checks the exact recipe cache (real recipe photographs from Google Cloud Storage / YouTube / verified sources).
    2. Checks if raw_image_url is already a valid, working image (e.g. YouTube i.ytimg.com, storage.googleapis.com, etc.).
    3. Matches fine-grained dish preparation (e.g. Schezwan wok noodles, not soup ramen; Dosa, not generic curry).
    4. Fallback to cuisine and meal type.
    """
    name_clean = recipe_name.lower().strip() if recipe_name else ""

    # 1. Exact Recipe Match from persistent cache (Highest Priority - 100% authentic dish photo)
    if name_clean in EXACT_IMAGE_CACHE:
        return EXACT_IMAGE_CACHE[name_clean]
    for key, cached_url in EXACT_IMAGE_CACHE.items():
        if key in name_clean or name_clean in key:
            return cached_url

    # 2. Existing working image URL
    if not is_problematic_image_url(raw_image_url):
        return raw_image_url.strip()

    # 3. Fine-tuned dish keyword matching (e.g. Schezwan noodles -> authentic wok stir-fry noodles)
    for pattern, img_url in DISH_KEYWORD_IMAGES:
        if re.search(pattern, name_clean, re.IGNORECASE):
            return img_url

    # 4. Match cuisine if available
    if cuisine:
        cuisine_clean = cuisine.lower().replace("recipes", "").strip()
        for c_key, c_img in CUISINE_FALLBACK_IMAGES.items():
            if c_key in cuisine_clean:
                return c_img

    # 5. Match meal type (sweet vs savoury)
    if meal_type == "sweet":
        return DEFAULT_SWEET_IMAGE

    # 6. Default appetizing culinary plate
    return DEFAULT_FOOD_IMAGE
