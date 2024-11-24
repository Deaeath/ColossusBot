# File: ColossusBot/config.py

"""
Config: Centralized Bot Configuration
--------------------------------------
Handles loading configuration from environment variables, with support for local overrides.
"""

from dotenv import load_dotenv
import os
import logging
from typing import Optional, Dict

# Load environment variables from .env and optionally .env.local for local development
load_dotenv()  # Load .env file
if os.path.exists(".env.local"):
    load_dotenv(".env.local")  # Override with .env.local values for local development

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("colossusbot.log"),
        logging.StreamHandler()
    ]
)

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
