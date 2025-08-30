import os
from fastapi import FastAPI
from config import Base, engine
from api.routes import router

app = FastAPI(title="Finance Assistant API")

app.include_router(router)

# Create database tables only if not in test environment
if os.getenv("TESTING") != "true":
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("This is expected in test environments or when database is not available.")

@app.get("/")
def root():
    return {"message": "Finance Assistant API is running 🚀"}
