"""Configuration management for LocateMeAI frontend."""
import os
from dotenv import load_dotenv

# Load environment variables
# Priority: .env.local (local development) > .env (Docker) > defaults
load_dotenv('.env.local')  # Load local development config first
load_dotenv()  # Then load .env if exists (won't override existing vars)

# Backend URL configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# API Endpoints
BACKEND_IMAGE_DETECT_URL = f"{BACKEND_URL}/detect"
BACKEND_VIDEO_DETECT_URL = f"{BACKEND_URL}/detect-video"
BACKEND_DOWNLOAD_VIDEO_URL = f"{BACKEND_URL}/download-video"
BACKEND_CLASSIFY_INTENT_URL = f"{BACKEND_URL}/classify-intent"
BACKEND_EXTRACT_CLASSES_URL = f"{BACKEND_URL}/extract-classes"
BACKEND_ASK_GENERAL_QUERY_URL = f"{BACKEND_URL}/ask-general-query"
