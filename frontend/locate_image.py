import streamlit as st
import requests
from speechtotext import speechtotext
from texttospeech import speak
from utils.image_utils import draw_bounding_boxes, image_uploader_section
from user_intent_classify import get_user_intent
from general_inquiry import ask_general_query

BACKEND_IMAGE_DETECT_URL = "http://localhost:8000/detect"

def locate_by_image():
    """Handle image detection functionality"""
    # -----------------------------
    # UI: Image Uploader
    # -----------------------------
    uploaded_file = image_uploader_section()

    # -----------------------------
    # UI: Voice Interaction
    # -----------------------------
    st.subheader("🎤 Voice Command")
    st.write("Say things like: **'detect objects'**, **'start detection'**")

    if st.button("Start Voice Command for Image"):
        command_placeholder = st.empty()
        command_placeholder.info("Listening for your command...")
        command = speechtotext()
        command_placeholder.info(f"Recognized command: {command}")

        classified_intent = get_user_intent(command)
        st.write(f"Classified Intent: **{classified_intent}**")

        if classified_intent == "object_detection":
            speak("Initiated object detection mode.")
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
                    response = requests.post(BACKEND_IMAGE_DETECT_URL, files={"file": uploaded_file})
                
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
            speak("General inquiry mode.")
            response = ask_general_query(uploaded_file.getvalue(), command, isImage=True)
            speak(response)
            st.write(response)
            command_placeholder.empty()
