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
            self.model = genai.GenerativeModel('gemini-3.5-flash')
        else:
            self.model = None
            logging.warning("Gemini API key not provided or genai not installed. Using mock mode.")

    def identify_ingredients_from_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Takes image bytes and returns a structured JSON-like dict of ingredients and confidences.
        """
        if not self.model:
            return self._mock_identify_ingredients()
            
        try:
            prompt = """
            Analyze this image and identify the visible food ingredients.
            Return a JSON object with a single key 'ingredients'. The value should be a list of objects, 
            where each object has 'name' (string) and 'confidence' (float between 0 and 1).
            Only output the valid JSON.
            """
            
            # Note: The actual implementation for image upload in genai requires 
            # either uploading the file or passing the appropriate Part object.
            # This is a simplified wrapper for demonstration.
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
            
            response = self.model.generate_content([prompt, image_part])
            
            # Attempt to parse JSON from response
            text_response = response.text
            # Clean up potential markdown formatting around the JSON
            if "```json" in text_response:
                text_response = text_response.split("```json")[1].split("```")[0].strip()
            elif "```" in text_response:
                text_response = text_response.split("```")[1].split("```")[0].strip()
                
            return json.loads(text_response)
        except Exception as e:
            logging.error(f"Error calling Gemini API: {e}")
            return {"error": "Failed to identify ingredients", "details": str(e)}

    def _mock_identify_ingredients(self) -> Dict[str, Any]:
        """
        Returns mock data when the API key is not available.
        """
        return {
            "ingredients": [
                {"name": "tomato", "confidence": 0.96},
                {"name": "potato", "confidence": 0.93},
                {"name": "onion", "confidence": 0.91},
                {"name": "capsicum", "confidence": 0.88}
            ]
        }
