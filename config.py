"""
Config: Centralized Bot Configuration
--------------------------------------
Handles loading configuration from environment variables, with support for local overrides.
"""

from dotenv import load_dotenv
import os
import logging
from typing import Optional, Dict
import sys

# Load environment variables from .env and optionally .env.local for local development
load_dotenv()  # Load .env file
if os.path.exists(".env.local"):
    load_dotenv(".env.local")  # Override with .env.local values for local development

# Logging Configuration (without writing to a file)
log_handlers = [logging.StreamHandler(sys.stdout)]  # Only log to stdout

# Set up logging with error handling for the handlers
try:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=log_handlers
    )
except OSError as e:
    # If logging setup fails, ignore errors (don't crash the bot)
    logging.error(f"Error setting up logging: {e}")

# Bot Configuration
BOT_PREFIX: str = os.getenv("BOT_PREFIX", "!")  # Default prefix is "!" if not set
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "your-discord-bot-token")
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)

# Database Configuration
DATABASE_CONFIG: Dict[str, Optional[str]] = {
    "engine": os.getenv("DB_ENGINE", "sqlite"),  # Supported values: 'sqlite' or 'mysql'
    "database": os.getenv("DB_NAME", "colossusbot.db"),
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# Google Cloud Configuration
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "your-google-cloud-api-key")
CX_ID: str = os.getenv("GOOGLE_CX_ID", "your-google-custom-search-api-key")

# OCR Configuration
OCR_SPACE_API_KEY: str = os.getenv("OCR_SPACE_API_KEY", "your-ocr-space-api-key")

# SERP Configuration
SERPAPI_KEY: str = os.getenv('SERPAPI_KEY', "your-serp-api-key")

# X-RapidAPI Configuration
RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "your-rapidapi-key")
