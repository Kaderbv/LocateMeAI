import streamlit as st
import requests
from speechtotext import speechtotext
from texttospeech import speak
from locate_image import locate_by_image
from locate_video import locate_by_video
from locate_stream import locate_by_stream
from fine_tuning import fine_tune_model
from styles import get_custom_css
import os

st.set_page_config(page_title="LocateMe Voice-Assisted AI", layout="wide")

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

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
