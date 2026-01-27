from dotenv import load_dotenv
import os

# Load environment variables
# Priority: .env.local (local development) > .env (Docker) > defaults
load_dotenv('.env.local')  # Load local development config first
load_dotenv()  # Then load .env if exists (won't override existing vars)

# Ollama configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llava")
# Default YOLO model path
DEFAULT_YOLO_MODEL = os.getenv("DEFAULT_YOLO_MODEL", "yolov8n.pt")

# Ollama API URL
OLLAMA_API_PULL_URL = f"{OLLAMA_HOST}/api/pull"
OLLAMA_API_GENERATE_URL = f"{OLLAMA_HOST}/api/generate"
# ==========================================
