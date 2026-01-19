import streamlit as st
import requests
from speechtotext import speechtotext
from texttospeech import speak
from locate_image import locate_by_image
from locate_video import locate_by_video
import os

st.set_page_config(page_title="LocateMe Voice-Assisted AI", layout="centered")

# Custom CSS for background color
st.markdown("""
    <style>
    .stApp {
        background-color: #D3D3D3 !important;
    }
    /* Style for tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #404040 !important;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1A1A1A !important;
    }
    .st-c1 {
            background-color: #D3D3D3 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------
# UI: Page Header and Logo
# -----------------------------

# Display logo if available (assets folder is in project root)
logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
if os.path.exists(logo_path):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(logo_path, width=200)

st.title("🎤 Voice-Assisted Object Locater")
st.caption("Upload an image/video and use voice commands to detect objects.")

# -----------------------------
# UI: Menu Tabs
# -----------------------------
locateInImage, locateInVideo = st.tabs(["📷 Locate By Image", "🎥 Locate By Video"])

with locateInImage:
    locate_by_image()

with locateInVideo:
    locate_by_video()
