import logging
from typing import List, Dict, Any
from app.config import settings
try:
    from googleapiclient.discovery import build
except ImportError:
    build = None

import re

EXCLUDED_TERMS = {
    'thyroid', 'diabetes', 'disease', 'symptoms', 'treatment', 'doctor',
    'clinic', 'cure', 'blood pressure', 'supplement', 'weight loss',
    'dr.', 'medicine', 'health benefits', 'cancer', 'remedy', 'remedies',
    'deficiency', 'side effect', 'side effects', 'diagnosis'
}

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
        Searches YouTube for cooking tutorials specifically for the recipe name.
        Cleans the recipe title and filters out unrelated medical/health videos.
        """
        if not self.youtube:
            return self._mock_search_tutorials(recipe_name)
            
        try:
            # Strip redundant words like 'Recipe' from the end of recipe_name
            clean_name = re.sub(r'(?i)\b(recipe|recipes)\b', '', recipe_name).strip()
            clean_name = re.sub(r'\s+', ' ', clean_name)
            query = f"{clean_name} recipe tutorial"
            
            # Retrieve candidate results
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=10,
                type='video'
            ).execute()
            
            name_keywords = [w.lower() for w in re.findall(r'\b\w+\b', clean_name) if len(w) > 2]
            
            candidates = []
            for search_result in search_response.get('items', []):
                title = search_result['snippet']['title']
                desc = search_result['snippet'].get('description', '')
                t_low = title.lower()
                d_low = desc.lower()
                
                # Exclude health / medical / treatment videos
                if any(term in t_low for term in EXCLUDED_TERMS):
                    continue
                
                # Scoring: prioritize title keyword matches and culinary terms
                score = sum(5 for kw in name_keywords if kw in t_low) + sum(1 for kw in name_keywords if kw in d_low)
                if any(w in t_low for w in ['recipe', 'how to make', 'cooking', 'masala', 'curry', 'dish', 'tutorial', 'step by step']):
                    score += 3
                    
                # Bonus if any core ingredient is mentioned
                if ingredients:
                    for ing in ingredients[:3]:
                        if len(ing) > 3 and ing.lower() in t_low:
                            score += 1

                candidates.append({
                    'video': {
                        'video_id': search_result['id']['videoId'],
                        'title': title,
                        'channel': search_result['snippet']['channelTitle'],
                        'thumbnail': search_result['snippet']['thumbnails']['high']['url'],
                        'published_at': search_result['snippet']['publishedAt'],
                    },
                    'score': score
                })
                
            candidates.sort(key=lambda x: x['score'], reverse=True)
            return [c['video'] for c in candidates[:5]]
            
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
