# SmartCook 🍳
### Multimodal AI-Powered Ingredient Recognition & Dual-Engine Culinary Recommendation Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.103+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flutter](https://img.shields.io/badge/Flutter-3.47+-02569B.svg?style=flat&logo=flutter&logoColor=white)](https://flutter.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Google Gemini](https://img.shields.io/badge/AI_Vision-Gemini_Flash-8E75C2.svg?style=flat&logo=google&logoColor=white)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

SmartCook is an end-to-end, production-grade mobile and cloud system designed to combat household food waste and daily meal-decision fatigue. Users simply capture or upload a photo of raw groceries and pantry items; SmartCook detects ingredients using multimodal computer vision, reconciles regional and multilingual synonyms, applies pantry staple assumptions, and evaluates **5,900+ recipes in 1.15 seconds** using a dual-mode SQL pre-filter and scoring engine. Each recommendation is paired with step-by-step instructions and verified YouTube video tutorials sanitized to exclude clickbait.

---

## 🌟 Key Highlights & Engineering Benchmarks

| Metric / Dimension | Baseline / Naive Approach | SmartCook Optimized | Improvement / Impact |
| :--- | :--- | :--- | :--- |
| **Vision Inference Latency** | 63.60 s (slow/failing models) | **4.24 s** | **15.0x Faster** (Cascading Flash models + 10s failover) |
| **Recipe Ranking Latency** | 82.70 s (Python ORM join over 5.9k rows) | **1.15 s** | **71.9x Faster** (SQL `match_count` candidate pre-filtering) |
| **YouTube Tutorial Precision** | 40% (polluted with medical/diet clickbait) | **100%** | Cleaned recipe titles + negative keyword sanitization |
| **Pantry Staple Handling** | Strict 100% matching fails on spices/oil | Dynamic staple isolation | **70+ classified essentials** bypass false missing penalties |
| **Candidate Search Space** | Full dataset scan | Top 150 candidate pre-filter | **97.5% memory & serialization reduction** |
| **Mobile App Footprint** | Standard debug runtime | **51.6 MB** release APK | Zero UI RenderFlex overflow, responsive bounded drawers |

---

## 🏗️ System Architecture

```mermaid
graph TD
    subgraph Presentation Tier [Frontend - Flutter 3.x Mobile App]
        UI[Camera / Gallery Input] --> Scale[Image Resizer & Compression]
        Scale --> ClientState[Provider State Management]
        ClientState --> ConfScreen[Ingredient Confirmation & Filter Drawer]
        ConfScreen --> RecipeUI[Ranked Recipe Cards & Video Player]
    end

    subgraph Application Tier [Backend - FastAPI Microservice]
        API_GW[FastAPI REST API /api]
        API_GW --> AuthMod[JWT Auth & BCrypt Service]
        API_GW --> VisionMod[Gemini Vision Cascade Service]
        API_GW --> SynMod[Synonym Clustering & Normalizer]
        API_GW --> RankMod[Dual-Mode SQL Scoring Engine]
        API_GW --> VideoMod[YouTube Sanitizer Service]
    end

    subgraph Data & Cloud Tier [Data & External Services]
        VisionMod -->|Multipart Image| GeminiAPI[Google Gemini Flash API]
        RankMod -->|Top 150 Match Pre-Filter| Postgres[(PostgreSQL 16 DB - 5,900+ Recipes)]
        VideoMod -->|Sanitized Query| YouTubeAPI[Google YouTube Data API v3]
    end

    ClientState <==>|JSON / REST| API_GW
```

---

## 🚀 Core Features

### 1. 📷 Multimodal AI Vision Ingredient Detection
- Zero-shot extraction of food produce, dairy, proteins, and pantry items directly from raw camera captures or gallery uploads.
- **Fail-Fast Cascading Fallback**: Automatically cascades across prioritized models (`gemini-3.1-flash-lite` -> `gemini-3.6-flash` -> `gemini-3-flash-preview` -> `gemini-3.5-flash` -> `gemini-3.8-flash`) with a strict 10-second timeout per model to circumvent single-model 429 quota exhaustion.

### 2. 🔤 Semantic Synonym Clustering & Canonical Normalization
- Resolves discrepancies across botanical, colloquial, and regional dialects (e.g., `capsicum` = `bell pepper` = `shimla mirch`; `potato` = `aloo` = `batata`; `paneer` = `cottage cheese`).
- Cleaned string canonicalization strips units, adjectives, and prep terminology (e.g., *"finely chopped organic red onions"* -> *"onion"*).

### 3. ⚡ High-Performance Dual-Mode SQL Candidate Ranking Engine
- **SQL Pre-Filtering**: Subqueries execute indexed `COUNT(ingredient_id)` aggregations in PostgreSQL to extract the top 150 candidate recipes in <0.2s, completely avoiding ORM serialization bottlenecks.
- **Dual Optimization Strategies**:
  - **Basket Maximization Mode**: Prioritizes using up available groceries to eliminate food waste:
    $$\text{Score} = 0.55 \times \text{BasketCoverage} + 0.45 \times \text{CorePrecision} - \text{MissingCorePenalty}$$
  - **Ready-to-Cook Mode**: Prioritizes recipes executable immediately with minimal missing ingredients:
    $$\text{Score} = 0.30 \times \text{BasketCoverage} + 0.70 \times \text{CorePrecision} - (1.5 \times \text{MissingCorePenalty})$$
- **Pantry Staple Knowledge Base**: Classifies 70+ spices, oils, salts, and kitchen basics so missing salt or cooking oil never penalizes a recipe match.

### 4. 🎥 Sanitized Culinary Video Tutorial Pipeline
- Strips redundant tokens from recipe titles to construct focused search queries (`"{name} recipe tutorial"`).
- Automatically filters out health, diagnosis, and medical clickbait (e.g., *thyroid*, *diabetes*, *treatment*, *weight loss*) to maintain 100% true culinary tutorial precision.

### 5. 📱 Cross-Platform Mobile Experience
- Built with Flutter 3.x for Android and iOS.
- **Material 3 Dark Emerald Aesthetics**: Designed for high contrast in kitchen environments (`#121816` charcoal background with sage `#4EAA85` accents).
- Bounded, scrollable multi-choice filter drawers (cuisine, meal type, prep time, difficulty) with zero UI clipping.

---

## 📊 Comparative Analysis

| Feature / Metric | SuperCook | MyFridgeFood | SmartCook (This Project) |
| :--- | :--- | :--- | :--- |
| **AI Camera Ingredient Scan** | ❌ (Manual checkboxes) | ❌ (Manual checkboxes) | ✅ **Gemini Multimodal Vision (4.2s)** |
| **Vernacular / Synonym Support** | ⚠️ Limited English only | ❌ None | ✅ **Extensive Regional & Global Synonyms** |
| **Dual Optimization Modes** | ❌ Single static match | ❌ Single static match | ✅ **Basket Use vs. Ready to Cook** |
| **Automated Pantry Staple Isolation** | ⚠️ Basic | ❌ None | ✅ **70+ Classified Kitchen Staples** |
| **Integrated Video Tutorials** | ❌ External links only | ❌ None | ✅ **YouTube API with Clickbait Sanitizer** |
| **5,900+ Recipe Query Latency** | ~2.50 s | ~3.00 s | ✅ **1.15 s (72x SQL Optimization)** |

---

## 🗂️ Project Directory Structure

```plaintext
smartcook/
├── Cleaned_Indian_Food_Dataset.csv   # Master recipe dataset (~5,900+ recipes)
├── backend/                          # FastAPI microservice
│   ├── app/
│   │   ├── api/                      # REST endpoints (auth, ingredients, recipes, youtube)
│   │   ├── models/                   # SQLAlchemy ORM models (User, Recipe, Ingredient)
│   │   ├── schemas/                  # Pydantic v2 validation models
│   │   ├── services/                 # GeminiService, RecommendationEngine, YouTubeService
│   │   ├── config.py                 # Pydantic settings & env loader
│   │   ├── database.py               # SessionLocal & DB engine
│   │   └── main.py                   # FastAPI initialization & CORS config
│   ├── Dockerfile                    # Container specification
│   ├── requirements.txt              # Python dependencies
│   ├── import_dataset.py             # CSV importer & normalizer
│   ├── seed_db.py                    # Database seeder
│   └── start.py                      # Production startup script
├── frontend/flutter_app/             # Cross-platform mobile client
│   ├── lib/
│   │   ├── screens/                  # Camera, Confirmation, Recommendations, Details, Auth
│   │   ├── services/                 # API client, Auth state, YouTube launcher
│   │   ├── theme/                    # Material 3 Dark Emerald theme
│   │   ├── widgets/                  # Recipe cards, Ingredient chips, Bounded filter sheet
│   │   └── main.dart                 # App entry point & Provider tree
│   └── pubspec.yaml                  # Flutter dependencies
├── report_assets/                    # Architectural diagrams, DFDs, benchmarks & screenshots
└── README.md                         # Project documentation
```

---

## 🛠️ Tech Stack & Tools

- **Frontend**: Flutter SDK (v3.47+), Dart, Provider (State Management), Google Fonts, ImagePicker, UrlLauncher.
- **Backend**: Python 3.12, FastAPI, Uvicorn ASGI Server, Pydantic v2, SQLAlchemy 2.0 ORM, PyJWT, Passlib (BCrypt).
- **Database**: PostgreSQL 16 (Relational tables indexed for ILIKE and aggregation performance).
- **AI & Cloud Services**: Google Gemini Multimodal Vision API, Google YouTube Data API v3, Docker, Render Cloud.

---

## ⚙️ Local Development & Setup Guide

### Prerequisites
- [Python 3.11+](https://www.python.org/downloads/)
- [PostgreSQL 15+](https://www.postgresql.org/download/)
- [Flutter SDK 3.x](https://docs.flutter.dev/get-started/install)
- [Git](https://git-scm.com/)
- API Keys: [Google AI Studio (Gemini)](https://aistudio.google.com/) and [Google Cloud Console (YouTube Data API v3)](https://console.cloud.google.com/)

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/dsayujya/smartcook.git
cd smartcook
```

---

### Step 2: Backend Configuration & Startup

1. Navigate to the backend directory and create a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Copy `.env.example` to `.env` and populate your credentials:
   ```ini
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/smartcook
   GEMINI_API_KEY=AIzaSy...your_gemini_api_key
   YOUTUBE_API_KEY=AIzaSy...your_youtube_api_key
   SECRET_KEY=supersecretjwtsecretkey
   DEBUG=True
   ```

4. Initialize the PostgreSQL database and import the recipe dataset:
   ```bash
   # Run table creation & migration
   python migrate_db.py

   # Import Cleaned Indian Food Dataset (~5,900 recipes)
   python import_dataset.py
   ```

5. Launch the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   *Interactive Swagger API Docs will be live at `http://localhost:8000/docs`.*

---

### Step 3: Frontend Setup (Flutter Mobile App)

1. Open a new terminal and navigate to the Flutter project:
   ```bash
   cd frontend/flutter_app
   ```

2. Fetch Flutter packages:
   ```bash
   flutter pub get
   ```

3. Configure the backend URL:
   Ensure `lib/services/api_service.dart` points to your backend instance:
   - Android Emulator: `http://10.0.2.2:8000/api`
   - Physical Android Device: `http://<YOUR_LOCAL_MACHINE_IP>:8000/api`
   - Cloud Production: `https://<YOUR_RENDER_SERVICE_URL>/api`

4. Launch the application:
   ```bash
   flutter run
   ```

---

## 📡 API Reference Overview

| Method | Endpoint | Description | Key Parameters / Body |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/ingredients/detect` | Upload image to detect ingredients via Gemini Vision | `image: UploadFile` (Multipart) |
| `POST` | `/api/ingredients/normalize` | Canonicalize vernacular strings to DB standard tokens | `raw_ingredients: List[str]` |
| `POST` | `/api/recipes/recommend` | Rank recipes based on detected/confirmed ingredients | `ingredients: List[str]`, `ranking_mode: "basket_use"\|"ready_to_cook"`, `cuisine`, `max_cooking_time` |
| `GET` | `/api/recipes/{recipe_id}` | Fetch detailed recipe information and instructions | `recipe_id: int` |
| `GET` | `/api/youtube/search` | Fetch sanitized YouTube cooking tutorials | `recipe_name: str`, `ingredients: List[str]` |
| `POST` | `/api/auth/register` | Register new user account with hashed password | `email`, `password`, `full_name` |
| `POST` | `/api/auth/login` | Authenticate user and issue JWT bearer token | `username (email)`, `password` |

---

## 🧪 Testing & Validation

```bash
# Run backend test suite
cd backend
pytest

# Test the recommendation engine ranking standalone
python test_engine.py

# Verify Flutter client analysis & linting
cd ../frontend/flutter_app
flutter analyze
```

---

## 🗺️ Roadmap & Future Enhancements

- [ ] **On-Device Edge Vision**: Deploy quantized TensorFlow Lite / ONNX models for offline zero-latency edge ingredient recognition.
- [ ] **Macronutrient Profiling**: Automated nutritional calculation (calories, macros, dietary suitability) per recipe serving.
- [ ] **Voice-Guided Hands-Free Cooking**: Interactive speech-to-text and text-to-speech navigation for kitchen workflows.
- [ ] **Pantry Expiry Forecasting**: Proactive notifications and barcode scanning to warn users of expiring ingredients.

---

## 👥 Contributors & Acknowledgements

- **Sayujya Nitin Deshpande** - Backend Architecture, Vision Pipelines & Algorithm Optimization
- **Atharva Kakde** - Flutter Mobile Development & UI/UX Design
- **Rohan Raut** - Database Engineering, ETL Normalization & Testing

*Developed as part of the Multi-Disciplinary Minor (MDM) in Artificial Intelligence & Machine Learning at the Institute of Information and Communication Technology (IICT), MGM University.*
