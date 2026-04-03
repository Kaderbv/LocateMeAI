import streamlit as st
import requests
from speechtotext import speechtotext
from texttospeech import speak
from locate_image import locate_by_image
from locate_video import locate_by_video
from locate_stream import locate_by_stream
from fine_tuning import fine_tune_model
from styles import get_custom_css
from config import FRONTEND_AUTH_CONFIG_ERROR, FRONTEND_AUTH_ENABLED, FRONTEND_AUTH_USERS
import hmac
import os

st.set_page_config(page_title="LocateMe Voice-Assisted AI", layout="wide")


def initialize_auth_state():
    """Initialize session state values used by the optional login flow."""
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "auth_error" not in st.session_state:
        st.session_state.auth_error = None
    if "auth_enabled" not in st.session_state:
        st.session_state.auth_enabled = FRONTEND_AUTH_ENABLED
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = not FRONTEND_AUTH_ENABLED

    # Keep session auth state aligned with the current config.
    if st.session_state.auth_enabled != FRONTEND_AUTH_ENABLED:
        st.session_state.auth_enabled = FRONTEND_AUTH_ENABLED
        st.session_state.authenticated = not FRONTEND_AUTH_ENABLED
        st.session_state.current_user = None
        st.session_state.auth_error = None

    if FRONTEND_AUTH_ENABLED and not st.session_state.current_user:
        st.session_state.authenticated = False


def verify_credentials(username: str, password: str) -> bool:
    """Validate credentials against the configured frontend user list."""
    stored_password = FRONTEND_AUTH_USERS.get(username.strip())
    if stored_password is None:
        return False
    return hmac.compare_digest(stored_password, password)


def render_login_gate():
    """Render a simple login form and stop the app until the user signs in."""
    initialize_auth_state()

    if not FRONTEND_AUTH_ENABLED or st.session_state.authenticated:
        return

    st.title("LocateMeAI Login")
    st.caption("Sign in to access the frontend application.")

    if FRONTEND_AUTH_CONFIG_ERROR:
        st.error(FRONTEND_AUTH_CONFIG_ERROR)
        st.info("Update FRONTEND_AUTH_USERS in frontend/.env or frontend/.env.local and restart Streamlit.")
        st.stop()

    if not FRONTEND_AUTH_USERS:
        st.error("Frontend authentication is enabled, but no users are configured.")
        st.info("Add FRONTEND_AUTH_USERS=username:password pairs in frontend/.env or frontend/.env.local.")
        st.stop()

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", use_container_width=True)

    if submitted:
        if verify_credentials(username, password):
            st.session_state.authenticated = True
            st.session_state.current_user = username.strip()
            st.session_state.auth_error = None
            st.rerun()

        st.session_state.auth_error = "Invalid username or password."

    if st.session_state.auth_error:
        st.error(st.session_state.auth_error)

    st.stop()


def render_auth_sidebar():
    """Show the signed-in user and a logout control when auth is enabled."""
    if not FRONTEND_AUTH_ENABLED:
        return

    with st.sidebar:
        st.success(f"Signed in as {st.session_state.current_user}")
        if st.button("Log out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.auth_error = None
            st.rerun()

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

render_login_gate()
render_auth_sidebar()

# -----------------------------
# UI: Page Header and Logo
# -----------------------------

# Display logo on the left with title and caption on the right
logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
if os.path.exists(logo_path):
    col1, col2, col3, col4 = st.columns([1.5, 6,0.8, 1.5])
    with col1:
        st.image(logo_path, width=150)
    with col2:
        st.title("Voice-Assisted Object Locater")
        st.caption("Upload an image/video and use voice commands to detect objects.")
else:
    st.title("🎤 Voice-Assisted Object Locater")
    st.caption("Upload an image/video and use voice commands to detect objects.")

# -----------------------------
# UI: Menu Tabs
# -----------------------------
locateInImage, locateInVideo, locateInStream, fineTuning = st.tabs(["📷 Locate By Image", "🎥 Locate By Video", "🌐 Live Stream", "🎯 Fine-tune Model"])

with locateInImage:
    locate_by_image()

with locateInVideo:
    locate_by_video()

with locateInStream:
    locate_by_stream()

with fineTuning:
    fine_tune_model()
