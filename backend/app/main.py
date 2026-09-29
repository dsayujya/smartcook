from fastapi import FastAPI
from app.config import settings
from app.database import Base, engine
from app.models import domain

# Create database tables
Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to SmartCook API"}

from app.api import auth, ingredients, recipes, users, youtube

app.include_router(auth.router, prefix="/api")
app.include_router(ingredients.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(youtube.router, prefix="/api")
