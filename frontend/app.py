import streamlit as st
import requests
from speechtotext import speechtotext
from texttospeech import speak
from image_utils import draw_bounding_boxes, image_uploader_section
import os

st.set_page_config(page_title="LocateMe Voice-Assisted AI", layout="centered")

# Custom CSS for background color
st.markdown("""
    <style>
    .stApp {
        background-color: #F5F5DC !important;
    }
    </style>
    """, unsafe_allow_html=True)

BACKEND_URL = "http://localhost:8000/detect"

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
st.caption("Upload an image and use voice commands to detect objects.")

# -----------------------------
# UI: Image Uploader
# -----------------------------
uploaded_file = image_uploader_section()

# -----------------------------
# UI: Voice Interaction
# -----------------------------
st.subheader("🎤 Voice Command")
st.write("Say things like: **'detect objects'**, **'start detection'**, **'run YOLO'**")

if st.button("Start Voice Command"):
    command_placeholder = st.empty()
    command_placeholder.info("Listening for your command...")
    command = speechtotext()
    command_placeholder.info(f"Recognized command: {command}")
    if command and ("detect" in command or "start" in command or "yolo" in command):
        if not uploaded_file:
            st.warning("Please upload an image first.")
            speak("Please upload an image first.")
        else:
            # Create placeholder for temporary info message
            info_placeholder = st.empty()
            info_placeholder.info("Running YOLO detection...")
            files = {"file": uploaded_file.getvalue()}
            # show a loading spinner while waiting for response
            with st.spinner("Processing..."):
                response = requests.post(BACKEND_URL, files={"file": uploaded_file})
            
            # Clear the info message after detection
            info_placeholder.empty()

            if response.status_code == 200:
                detections = response.json()["detections"]

                if len(detections) == 0:
                    st.warning("No objects detected.")
                    speak("No objects detected.")
                else:
                    st.success("Objects detected:")
                    result_text = ""

                    for det in detections:
                        label = det["label"]
                        conf = round(det["confidence"], 2)
                        st.write(f"- **{label}** ({conf})")
                        result_text += f"{label} with confidence {conf}. "

                    # speak(result_text)
                    
                    # Draw bounding boxes on the image and display it
                    draw_bounding_boxes(uploaded_file, detections)
                    command_placeholder.empty()
                    
            else:
                st.error("Backend error. Could not process the image.")
                speak("Backend error. Could not process the image.")
                command_placeholder.empty()         
    else:
        st.warning("Voice command not recognized.")
        speak("Voice command not recognized.")
        command_placeholder.empty()
            
