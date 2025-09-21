import os
from pathlib import Path

def _db_url():
    raw = os.getenv("DATABASE_URL", "sqlite:///options_chain.db")
    if raw.startswith("postgres://"):
        raw = raw.replace("postgres://", "postgresql://", 1)
    return raw


class Config:
    SECRET_KEY = 'your-secret-key-here'  # Change this in production
    SQLALCHEMY_DATABASE_URI = _db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True  # Set to False in production
    ALLOWED_EXTENSIONS = {'csv', 'json'}  # Allowed file types for uploads
    ML_MODEL_PATH = Path(__file__).resolve().parent / 'ml/models'  # Path to ML models
    AI_PROMPTS_PATH = Path(__file__).resolve().parent / 'ai/prompts'  # Path to AI prompts
    CACHE_TYPE = 'simple'  # Use simple caching
    CACHE_DEFAULT_TIMEOUT = 300  # Cache timeout in seconds
    RATE_LIMIT = '100/hour'  # Rate limit for API calls
    LOGGING_LEVEL = 'INFO'  # Logging level for the application

    # Add any additional configuration settings as needed