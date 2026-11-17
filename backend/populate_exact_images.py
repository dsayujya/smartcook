"""
Utility script to populate exact recipe-wise images into recipe_image_cache.json.
Uses the configured YouTube Data API v3 or Next.js recipe page resolvers to link
recipes directly to authentic dish photos from verified chefs.
"""
import os
import sys
import json
import re
from dotenv import load_dotenv

# Load backend/.env explicitly
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.youtube_service import YouTubeService
from app.services.image_resolver import CACHE_FILE, load_cache, EXACT_IMAGE_CACHE

def fetch_and_cache_recipe_image(recipe_name: str, yt_service: YouTubeService = None) -> str:
    """Fetch the top verified YouTube tutorial thumbnail for a recipe and cache it."""
    clean_name = recipe_name.lower().strip()
    if clean_name in EXACT_IMAGE_CACHE:
        return EXACT_IMAGE_CACHE[clean_name]

    if yt_service is None:
        yt_service = YouTubeService()

    try:
        results = yt_service.search_tutorials(recipe_name)
        if results and 'thumbnail' in results[0]:
            thumbnail_url = results[0]['thumbnail']
            EXACT_IMAGE_CACHE[clean_name] = thumbnail_url
            # Persist to disk
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(EXACT_IMAGE_CACHE, f, indent=2)
            print(f"Cached exact image for '{recipe_name}': {thumbnail_url}")
            return thumbnail_url
    except Exception as e:
        print(f"Failed to fetch for '{recipe_name}': {e}")
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        dish_name = " ".join(sys.argv[1:])
        print(f"Fetching exact image for '{dish_name}'...")
        yt = YouTubeService()
        img = fetch_and_cache_recipe_image(dish_name, yt)
        print("Result:", img)
    else:
        print("Usage: python populate_exact_images.py <Recipe Name>")
        print("Example: python populate_exact_images.py 'Paneer Butter Masala'")
