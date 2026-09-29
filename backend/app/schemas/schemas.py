from pydantic import BaseModel
from typing import List, Optional

class UserBase(BaseModel):
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_email_verified: bool = False
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    class Config:
        from_attributes = True

class UserRegisterRequest(BaseModel):
    email: str
    password: Optional[str] = None
    full_name: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: str
    password: str

class RequestOTPRequest(BaseModel):
    target: str # Email address
    otp_type: Optional[str] = "email_verification"

class VerifyOTPRequest(BaseModel):
    target: str
    otp_code: str
    otp_type: Optional[str] = "email_verification"

class GoogleAuthRequest(BaseModel):
    id_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
    dev_otp_code: Optional[str] = None

class IngredientBase(BaseModel):
    name: str

class Ingredient(IngredientBase):
    id: int
    class Config:
        from_attributes = True

class IngredientDetectionResult(BaseModel):
    name: str
    confidence: float

class IngredientDetectionResponse(BaseModel):
    ingredients: List[IngredientDetectionResult]

class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    instructions: str
    image_url: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    servings: Optional[int] = None
    diet_type: Optional[str] = None
    rating: float = 0.0
    popularity: int = 0
    source: Optional[str] = "seed"
    meal_type: Optional[str] = "savoury"

class RecipeIngredientDetail(BaseModel):
    ingredient: Ingredient
    quantity: Optional[float] = None
    unit: Optional[str] = None
    class Config:
        from_attributes = True

class Recipe(RecipeBase):
    id: int
    ingredients: List[RecipeIngredientDetail] = []
    class Config:
        from_attributes = True

class RecipeRecommendation(BaseModel):
    recipe: Recipe
    match_percentage: float
    missing_ingredients: List[str]
    score: float

class RecipeFilterParams(BaseModel):
    cuisine: Optional[str] = None       # e.g. "Indian", "Italian", "Continental"
    meal_type: Optional[str] = None     # "sweet" or "savoury"
    max_cook_time: Optional[int] = None # in minutes

