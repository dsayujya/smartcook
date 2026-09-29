from fastapi import APIRouter, Query
from app.services.youtube_service import YouTubeService
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/youtube", tags=["youtube"])
youtube_service = YouTubeService()

@router.get("/search")
def search_tutorials(recipe_name: str, ingredients: Optional[List[str]] = Query(None)) -> List[Dict[str, Any]]:
    """
    Search YouTube for cooking tutorials for a specific recipe name.
    """
    videos = youtube_service.search_tutorials(recipe_name, ingredients)
    return videos
