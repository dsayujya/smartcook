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
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
            self.has_key = True
        else:
            self.has_key = False
            logging.warning("Gemini API key not provided or genai not installed. Using mock mode.")

    def identify_ingredients_from_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        """
        Takes image bytes and returns a structured JSON-like dict of ingredients and confidences.
        Iterates over active Gemini models to bypass per-model quota limits (e.g. 429 20 RPD limits).
        Falls back to mock data ONLY if no Gemini API key is configured (offline dev mode).
        """
        if not self.has_key:
            return self._mock_identify_ingredients()

        candidate_models = [
            'gemini-flash-lite-latest',
            'gemini-3.5-flash-lite',
            'gemini-3.1-flash-lite',
            'gemini-flash-latest',
            'gemini-3.8-flash',
            'gemini-3.5-flash',
        ]

        prompt = """
        Analyze this image and identify the visible food ingredients, vegetables, fruits, grains, or groceries.
        Return a JSON object with a single key 'ingredients'. The value should be a list of objects, 
        where each object has 'name' (canonical ingredient name, string) and 'confidence' (float between 0 and 1).
        If no food ingredients are clearly visible, return {"ingredients": []}.
        Only output valid JSON.
        """

        image_part = {
            "mime_type": mime_type,
            "data": image_bytes
        }

        last_error = None
        for model_name in candidate_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content([prompt, image_part], request_options={"timeout": 30})
                
                text_response = response.text.strip()
                if "```json" in text_response:
                    text_response = text_response.split("```json")[1].split("```")[0].strip()
                elif "```" in text_response:
                    text_response = text_response.split("```")[1].split("```")[0].strip()
                    
                # Extract innermost JSON braces if needed
                json_start = text_response.find('{')
                json_end = text_response.rfind('}')
                if json_start != -1 and json_end != -1 and json_end >= json_start:
                    text_response = text_response[json_start:json_end+1]

                parsed = json.loads(text_response)
                if "ingredients" in parsed and isinstance(parsed["ingredients"], list):
                    cleaned_ingredients = []
                    for item in parsed["ingredients"]:
                        if isinstance(item, dict) and "name" in item:
                            name = str(item["name"]).strip().lower()
                            if name:
                                conf = float(item.get("confidence", 0.9))
                                cleaned_ingredients.append({"name": name, "confidence": conf})
                    logging.info(f"Successfully identified {len(cleaned_ingredients)} ingredients using model {model_name}")
                    return {"ingredients": cleaned_ingredients}
            except Exception as e:
                last_error = e
                logging.warning(f"Model {model_name} failed or rate limited: {e}. Trying next model...")

        logging.error(f"All Gemini models failed or exceeded quota limits. Last error: {last_error}")
        raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

    def _mock_identify_ingredients(self) -> Dict[str, Any]:
        """
        Returns mock data when the API key is not configured (offline development mode only).
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


