"""Configuration management for LocateMeAI frontend."""
import os
from dotenv import load_dotenv

# Load environment variables
# Priority: .env.local (local development) > .env (Docker) > defaults
load_dotenv('.env.local')  # Load local development config first
load_dotenv()  # Then load .env if exists (won't override existing vars)

# Backend URL configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def _parse_bool(value: str | None, default: bool = False) -> bool:
	"""Parse a boolean environment variable value."""
	if value is None:
		return default
	return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_auth_users(raw_users: str | None) -> tuple[dict[str, str], str | None]:
	"""Parse comma-separated username:password pairs from environment."""
	if not raw_users:
		return {}, None

	users: dict[str, str] = {}
	for entry in raw_users.split(","):
		item = entry.strip()
		if not item:
			continue

		if ":" not in item:
			return {}, "FRONTEND_AUTH_USERS must use the format username:password,username2:password2"

		username, password = item.split(":", 1)
		username = username.strip()
		password = password.strip()

		if not username or not password:
			return {}, "FRONTEND_AUTH_USERS contains an empty username or password"

		users[username] = password

	return users, None


FRONTEND_AUTH_ENABLED = _parse_bool(os.getenv("FRONTEND_AUTH_ENABLED"), default=False)
FRONTEND_AUTH_USERS, FRONTEND_AUTH_CONFIG_ERROR = _parse_auth_users(
	os.getenv("FRONTEND_AUTH_USERS")
)

# API Endpoints
BACKEND_IMAGE_DETECT_URL = f"{BACKEND_URL}/detect"
BACKEND_VIDEO_DETECT_URL = f"{BACKEND_URL}/detect-video"
BACKEND_DOWNLOAD_VIDEO_URL = f"{BACKEND_URL}/download-video"
BACKEND_CLASSIFY_INTENT_URL = f"{BACKEND_URL}/classify-intent"
BACKEND_EXTRACT_CLASSES_URL = f"{BACKEND_URL}/extract-classes"
BACKEND_ASK_GENERAL_QUERY_URL = f"{BACKEND_URL}/ask-general-query"
