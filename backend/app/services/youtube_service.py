import logging
from typing import List, Dict, Any
from app.config import settings
try:
    from googleapiclient.discovery import build
except ImportError:
    build = None

class YouTubeService:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        if self.api_key and build:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        else:
            self.youtube = None
            logging.warning("YouTube API key not provided or google-api-python-client not installed. Using mock mode.")

    def search_tutorials(self, recipe_name: str, ingredients: List[str] = None) -> List[Dict[str, Any]]:
        """
        Searches YouTube for cooking tutorials based on the recipe name and ingredients.
        """
        if not self.youtube:
            return self._mock_search_tutorials(recipe_name)
            
        try:
            ingredients_str = " ".join(ingredients) if ingredients else ""
            query = f"{recipe_name} recipe tutorial cooking {ingredients_str}".strip()
            
            # Call the search.list method to retrieve results
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=5,
                type='video'
            ).execute()
            
            videos = []
            for search_result in search_response.get('items', []):
                title = search_result['snippet']['title']
                desc = search_result['snippet'].get('description', '')
                
                score = 0
                if ingredients:
                    text_to_search = f"{title} {desc}".lower()
                    for ing in ingredients:
                        if ing.lower() in text_to_search:
                            score += 1

                videos.append({
                    'video_id': search_result['id']['videoId'],
                    'title': title,
                    'channel': search_result['snippet']['channelTitle'],
                    'thumbnail': search_result['snippet']['thumbnails']['high']['url'],
                    'published_at': search_result['snippet']['publishedAt'],
                    'score': score
                })
                
            if ingredients:
                videos.sort(key=lambda x: x.get('score', 0), reverse=True)
                
            return videos
            
        except Exception as e:
            logging.error(f"Error calling YouTube API: {e}")
            return []

    def _mock_search_tutorials(self, recipe_name: str) -> List[Dict[str, Any]]:
        """
        Returns mock data when the API key is not available.
        """
        return [
            {
                'video_id': 'dQw4w9WgXcQ',
                'title': f'How to make perfect {recipe_name} at home!',
                'channel': 'Chef Master',
                'thumbnail': 'https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg',
                'published_at': '2023-10-01T12:00:00Z'
            },
            {
                'video_id': 'jNQXAC9IVRw',
                'title': f'Quick & Easy {recipe_name} in 15 Minutes',
                'channel': 'Speedy Kitchen',
                'thumbnail': 'https://img.youtube.com/vi/jNQXAC9IVRw/hqdefault.jpg',
                'published_at': '2023-10-05T15:30:00Z'
            }
        ]
