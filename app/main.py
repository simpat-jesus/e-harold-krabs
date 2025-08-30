from fastapi import FastAPI
from config import Base, engine
from api.routes import router

app = FastAPI(title="Finance Assistant API")

app.include_router(router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Finance Assistant API is running 🚀"}
