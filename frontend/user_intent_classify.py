import requests
import streamlit as st # type: ignore

BACKEND_CLASSIFY_URL = "http://localhost:8000/classify-intent"

def get_user_intent(user_text: str) -> str:
    """Call backend to classify user intent"""
    response = requests.post(
        f"{BACKEND_CLASSIFY_URL}",
        params={"text": user_text}
    )
    
    if response.status_code == 200:
        return response.json()["intent"]
    else:
        st.error(f"Failed to classify intent {response.status_code}")
        return "object_detection"  # fallback