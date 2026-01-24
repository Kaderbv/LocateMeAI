import streamlit as st
import requests
from speechtotext import speechtotext
from texttospeech import speak
from user_intent_classify import get_user_intent
from utils.video_utils import download_video, video_uploader_section
from general_inquiry import ask_general_query

BACKEND_VIDEO_DETECT_URL = "http://localhost:8000/detect-video"

def locate_by_video():
    """Handle video detection functionality"""
    
    video_file = video_uploader_section()

    st.subheader("🎤 Voice Command")
    st.write("Say things like: **'detect objects'**, **'start detection'**")

    if st.button("Start Voice Command for Video"):
        video_command_placeholder = st.empty()
        video_command_placeholder.info("Listening for your command...")
        voiceCommand = speechtotext()
        video_command_placeholder.info(f"Recognized command: {voiceCommand}")

        classified_intent = get_user_intent(voiceCommand)
        st.write(f"Classified Intent: **{classified_intent}**")

        if classified_intent == "object_detection":
            if not video_file:
                st.warning("Please upload a video first.")
                speak("Please upload a video first.")
            else:
                # st.video(video_file)
                
                # call backend for video detection 
                files = {"file": video_file.getvalue()}
                
                with st.spinner("Processing video..."):
                   video_detection_response = requests.post(BACKEND_VIDEO_DETECT_URL, files={"file": video_file})
                   
                if video_detection_response.status_code == 200:
                    result = video_detection_response.json()
                    st.success("Video processed successfully!")
                    st.info(f"Total frames processed: {result['total_frames']}")
                    
                    # Show detection statistics
                    video_detections = result.get('detections', [])
                    if video_detections:
                        video_command_placeholder.empty()  
                        st.subheader("📊 Detection Summary")
                        
                        # Count unique objects
                        object_counts = {}
                        for det in video_detections:
                            label = det['label']
                            object_counts[label] = object_counts.get(label, 0) + 1
                        
                        # Display counts
                        for obj, count in object_counts.items():
                            st.write(f"- **{obj}**: detected {count} times")
                        
                        # Fetch and display the processed video
                        output_file = result['output_file']                     
                        
                        # Call the download_video function to fetch and display the video
                        download_video(output_file)
                    else:
                        st.warning("No objects detected in the video.")
                        speak("No objects detected in the video.")                           
                
                else:
                    st.error("Backend error. Could not process the video.")
                    speak("Backend error. Could not process the video.")
                    video_command_placeholder.empty()
        else:
            st.warning("General inquiry detected.")
            speak("General inquiry detected.")
            response = ask_general_query(video_file.getvalue(), voiceCommand, isImage=False)
            st.write(response)
            video_command_placeholder.empty()
