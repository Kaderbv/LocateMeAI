from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Ollama configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llava")
# Default YOLO model path
DEFAULT_YOLO_MODEL = os.getenv("DEFAULT_YOLO_MODEL", "yolov8n.pt")

# Ollama API URL
OLLAMA_API_PULL_URL = f"{OLLAMA_HOST}/api/pull"
OLLAMA_API_GENERATE_URL = f"{OLLAMA_HOST}/api/generate"
# ==========================================
