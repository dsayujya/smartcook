import logging
import json
from typing import List, Dict, Any
from app.config import settings
try:
    import google.generativeai as genai
except ImportError:
    genai = None

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = None
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
            # Try multiple model options in case one has quota restrictions
            for model_name in ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-2.0-flash']:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    break
                except Exception:
                    continue
        if not self.model:
            logging.warning("Gemini API key not provided, model unavailable, or genai not installed. Using mock mode.")

    def identify_ingredients_from_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Takes image bytes and returns a structured JSON-like dict of ingredients and confidences.
        Falls back gracefully to mock data if Gemini API fails (e.g. quota 429, network error).
        """
        if not self.model:
            return self._mock_identify_ingredients()
            
        try:
            prompt = """
            Analyze this image and identify the visible food ingredients.
            Return a JSON object with a single key 'ingredients'. The value should be a list of objects, 
            where each object has 'name' (string) and 'confidence' (float between 0 and 1).
            Only output valid JSON.
            """
            
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
            
            response = self.model.generate_content([prompt, image_part])
            
            # Attempt to parse JSON from response
            text_response = response.text
            if "```json" in text_response:
                text_response = text_response.split("```json")[1].split("```")[0].strip()
            elif "```" in text_response:
                text_response = text_response.split("```")[1].split("```")[0].strip()
                
            parsed = json.loads(text_response)
            if "ingredients" in parsed and isinstance(parsed["ingredients"], list) and len(parsed["ingredients"]) > 0:
                return parsed
            else:
                logging.warning("Gemini returned JSON without valid ingredients. Falling back to mock data.")
                return self._mock_identify_ingredients()
        except Exception as e:
            logging.error(f"Error calling Gemini API: {e}. Falling back to mock detection.")
            return self._mock_identify_ingredients()

    def _mock_identify_ingredients(self) -> Dict[str, Any]:
        """
        Returns mock data when the API key/quota is unavailable or fails.
        """
        return {
            "ingredients": [
                {"name": "tomato", "confidence": 0.96},
                {"name": "onion", "confidence": 0.93},
                {"name": "garlic", "confidence": 0.91},
                {"name": "pasta", "confidence": 0.88},
                {"name": "cheese", "confidence": 0.85},
                {"name": "olive oil", "confidence": 0.82}
            ]
        }

