import streamlit as st
import requests
from speechtotext import speechtotext
from texttospeech import speak

BACKEND_URL = "http://localhost:8000/detect"

st.set_page_config(page_title="Voice‑Activated YOLO Detection", layout="centered")
st.title("🎤 Voice‑Activated YOLO Object Detection")

# -----------------------------
# UI: Image Upload
# -----------------------------
uploaded_file = st.file_uploader("Upload an image for object detection", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

# -----------------------------
# UI: Voice Interaction
# -----------------------------
st.subheader("🎤 Voice Command")
st.write("Say things like: **'detect objects'**, **'start detection'**, **'run YOLO'**")

if st.button("Start Voice Command"):
    command = speechtotext()

    if command and ("detect" in command or "start" in command or "yolo" in command):
        if not uploaded_file:
            st.warning("Please upload an image first.")
            speak("Please upload an image first.")
        else:
            st.info("Running YOLO detection...")
            files = {"file": uploaded_file.getvalue()}
            st.write("This is a placeholder for backend processing.")
            speak("This is a placeholder for backend processing.")
            # response = requests.post(BACKEND_URL, files={"file": uploaded_file})

            # if response.status_code == 200:
            #     detections = response.json()["detections"]

            #     if len(detections) == 0:
            #         st.warning("No objects detected.")
            #         speak("No objects detected.")
            #     else:
            #         st.success("Objects detected:")
            #         result_text = ""

            #         for det in detections:
            #             label = det["label"]
            #             conf = round(det["confidence"], 2)
            #             st.write(f"- **{label}** ({conf})")
            #             result_text += f"{label} with confidence {conf}. "

            #         speak(result_text)
            # else:
            #     st.error("Backend error. Could not process the image.")
            #     speak("Backend error. Could not process the image.")
    else:
        st.warning("Voice command not recognized.")
        speak("Voice command not recognized.")
