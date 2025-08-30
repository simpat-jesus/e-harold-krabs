import os
import logging
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from config import engine
from db.models import Base
from api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Finance Assistant API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(router)

# Create database tables only if not in test environment
if os.getenv("TESTING") != "true":
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Could not create database tables: {e}")
        logger.info("Database might not be ready yet - tables will be created on first request")

from contextlib import asynccontextmanager
from fastapi import FastAPI

# ... existing code ...

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events"""
    # Startup
    if os.getenv("TESTING") != "true":
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables verified/created on startup")
        except Exception as e:
            logger.warning(f"Could not create tables on startup: {e}")
    
    yield
    
    # Shutdown (if needed)
    pass

app = FastAPI(title="Finance Assistant API", lifespan=lifespan)

@app.get("/")
def root():
    logger.info("Health check request received")
    return {"message": "Finance Assistant API is running 🚀"}

@app.get("/health")
def health_check():
    """Health check endpoint that verifies database connectivity"""
    try:
        # Test database connection
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        return {
            "status": "healthy",
            "database": "connected",
            "tables": tables,
            "message": "All systems operational"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
