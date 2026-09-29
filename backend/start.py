import os
import uvicorn
from migrate_db import run_migrations

if __name__ == "__main__":
    print("Executing automatic database migrations...")
    try:
        run_migrations()
    except Exception as e:
        print(f"Migration notice: {e}")

    port = int(os.environ.get("PORT", 8000))
    print(f"Starting SmartCook FastAPI server on host 0.0.0.0:{port}...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
