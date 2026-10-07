from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.gemini_service import GeminiService
from app.services.ingredient_service import IngredientService
from app.schemas.schemas import IngredientDetectionResponse

router = APIRouter(prefix="/ingredients", tags=["ingredients"])
gemini_service = GeminiService()

@router.post("/detect", response_model=IngredientDetectionResponse)
async def detect_ingredients(image: UploadFile = File(...)):
    """
    Takes an uploaded image, sends it to Gemini Flash to detect ingredients.
    """
    is_image_content = image.content_type and image.content_type.startswith("image/")
    is_image_ext = image.filename and image.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
    
    if not is_image_content and not is_image_ext:
        raise HTTPException(status_code=400, detail="File must be an image")
        
    mime_type = image.content_type if (image.content_type and image.content_type.startswith("image/")) else "image/jpeg"

    try:
        contents = await image.read()
        result = gemini_service.identify_ingredients_from_image(contents, mime_type=mime_type)
        return result
    except HTTPException:
        raise
    except Exception as e:
        if not gemini_service.has_key:
            return gemini_service._mock_identify_ingredients()
        raise HTTPException(
            status_code=503, 
            detail=f"Ingredient detection service is temporarily unavailable: {str(e)}"
        )


@router.post("/normalize")
def normalize_ingredients(raw_ingredients: list[str], db: Session = Depends(get_db)):
    """
    Takes a list of raw ingredient strings and normalizes them.
    """
    normalized = IngredientService.process_detected_ingredients(db, raw_ingredients)
    return {"normalized_ingredients": normalized}
