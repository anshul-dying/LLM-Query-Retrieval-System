import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API Configuration (optional for deployment)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
OPENROUTER_REFERER = os.getenv("OPENROUTER_REFERER", "https://example.com")

# Local LLM Configuration (disabled by default on remote hosts)
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "llama3.2:3b")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# File Processing Configuration
TEMP_DIR = os.getenv("TEMP_DIR", "temp")
TEMP_FILE_CLEANUP_RETRIES = int(os.getenv("TEMP_FILE_CLEANUP_RETRIES", "3"))
TEMP_FILE_CLEANUP_DELAY = float(os.getenv("TEMP_FILE_CLEANUP_DELAY", "1.0"))
DOWNLOAD_TIMEOUT = int(os.getenv("DOWNLOAD_TIMEOUT", "30"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))  # 100MB default limit