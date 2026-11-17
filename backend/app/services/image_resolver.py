import re
from typing import Optional

# ==============================================================================
# Curated High-Resolution, Mobile-Optimized CDN Food Images (Unsplash CDN)
# Free to use, globally cached, and never blocked by mobile clients or hotlink rules.
# ==============================================================================

DISH_KEYWORD_IMAGES = [
    # Noodles & Pastas
    (r"\b(noodle|noodles|chowmein|chow mein|schezwan noodle|hakka noodle|maggi|ramen)\b", 
     "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800&auto=format&fit=crop&q=80"),
    (r"\b(pasta|spaghetti|macaroni|penne|lasagna|ravioli|fusilli)\b", 
     "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=800&auto=format&fit=crop&q=80"),
    (r"\b(pizza)\b", 
     "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&auto=format&fit=crop&q=80"),
    (r"\b(burger|sandwich|toast|panini|wrap|roll|frankie)\b", 
     "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&auto=format&fit=crop&q=80"),

    # Rice Dishes & Biryanis
    (r"\b(biryani|dum biryani|pulao|pulav|fried rice|jeera rice)\b", 
     "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&auto=format&fit=crop&q=80"),
    (r"\b(rice|khichdi|pongal|curd rice|lemon rice|tomato rice)\b", 
     "https://images.unsplash.com/photo-1516714435131-44d6b64dc6a2?w=800&auto=format&fit=crop&q=80"),

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

    # South Indian Breakfast & Breads (checked before general curries)
    (r"\b(dosa|masala dosa|idli|vada|medu vada|uttapam|appam|pesarattu)\b", 
     "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=800&auto=format&fit=crop&q=80"),
    (r"\b(paratha|roti|chapati|naan|puri|poori|kulcha|flatbread|thepla)\b", 
     "https://images.unsplash.com/photo-1626074353765-517a681e40be?w=800&auto=format&fit=crop&q=80"),

    # Dals, Legumes & Curries
    (r"\b(chole|chana|rajma|chickpea|chickpeas)\b", 
     "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&auto=format&fit=crop&q=80"),
    (r"\b(dal|daal|sambar|rasam|tadka|makhani|moong dal|toor dal|kootu)\b", 
     "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&auto=format&fit=crop&q=80"),
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
    "chinese": "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?w=800&auto=format&fit=crop&q=80",
    "indo chinese": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800&auto=format&fit=crop&q=80",
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

# Domains known to block mobile hotlinking or serve dead links
BLOCKED_DOMAINS = [
    "archanaskitchen.com",
    "localhost",
    "127.0.0.1",
]


def is_problematic_image_url(url: Optional[str]) -> bool:
    """Check if an image URL is empty, invalid, or hosted on a domain that blocks mobile clients."""
    if not url or not isinstance(url, str):
        return True
    url_stripped = url.strip().lower()
    if not url_stripped or not url_stripped.startswith("http"):
        return True
    return any(domain in url_stripped for domain in BLOCKED_DOMAINS)


def get_reliable_image_url(
    recipe_name: str,
    cuisine: Optional[str] = None,
    meal_type: Optional[str] = None,
    raw_image_url: Optional[str] = None
) -> str:
    """
    Returns a guaranteed, fast, mobile-friendly image URL for a given recipe.
    If raw_image_url is already valid and not from a hotlink-protected host, returns it.
    Otherwise, intelligently matches dish keywords or cuisine types to high-res Unsplash CDN images.
    """
    if not is_problematic_image_url(raw_image_url):
        return raw_image_url.strip()

    name_lower = recipe_name.lower().strip() if recipe_name else ""

    # 1. Match specific dish keyword patterns in recipe name
    for pattern, img_url in DISH_KEYWORD_IMAGES:
        if re.search(pattern, name_lower, re.IGNORECASE):
            return img_url

    # 2. Match cuisine if available
    if cuisine:
        cuisine_clean = cuisine.lower().replace("recipes", "").strip()
        for c_key, c_img in CUISINE_FALLBACK_IMAGES.items():
            if c_key in cuisine_clean:
                return c_img

    # 3. Match meal type (sweet vs savoury)
    if meal_type == "sweet":
        return DEFAULT_SWEET_IMAGE

    # 4. Ultimate fallback: appetizing culinary plate
    return DEFAULT_FOOD_IMAGE
