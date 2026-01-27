import streamlit as st
import requests
from speechtotext import speechtotext
from texttospeech import speak
from user_intent_classify import get_user_intent
from utils.video_utils import download_video, video_uploader_section
from general_inquiry import ask_general_query

BACKEND_EXTRACT_CLASSES_URL = "http://localhost:8000/extract-classes"
BACKEND_VIDEO_DETECT_URL = "http://localhost:8000/detect-video"

def locate_by_video():
    """Handle video detection functionality"""
    
    video_file = video_uploader_section()

    st.subheader("🎤 Voice Command")
    st.write("Say things like: **'detect cycle'**, **'find person and cat in this video'**")

    if st.button("Start Voice Command for Video"):
        video_command_placeholder = st.empty()
        video_command_placeholder.info("Listening for your command...")
        voiceCommand = speechtotext()
        video_command_placeholder.info(f"Recognized command: {voiceCommand}")

        classified_intent = get_user_intent(voiceCommand)
        st.write(f"Classified Intent: **{classified_intent}**")

        if classified_intent == "object_detection":
            speak("Initiated object detection mode.")
            if not video_file:
                st.warning("Please upload a video first.")
                speak("Please upload a video first.")
            else:
                info_placeholder = st.empty()
                info_placeholder.info("Understanding your command...")
                
                try:
                    classes_response = requests.post(
                        BACKEND_EXTRACT_CLASSES_URL,
                        data={"command": voiceCommand},
                        timeout=15
                    )
                    response_data = classes_response.json()
                    classes = response_data.get("class_ids", "")
                    object_names = response_data.get("object_names", "")
                    
                    if classes and object_names:
                        st.info(f"🎯 Detecting: {object_names} with (class IDs: {classes})")
                    else:
                        st.info("🎯 Detecting all objects")
                except Exception as e:
                    st.warning(f"Could not extract classes, detecting all objects. Error: {e}")
                    classes = ""

                info_placeholder.info("Running detection...")

                # call backend for video detection 
                files = {"file": video_file.getvalue()}
                data = {"classes": classes} if classes else {}
                
                with st.spinner("Processing video..."):
                   video_detection_response = requests.post(BACKEND_VIDEO_DETECT_URL,
                                                            files={"file": video_file},
                                                            data=data)
                # Clear the info message after detection
                info_placeholder.empty()

                if video_detection_response.status_code == 200:
                    result = video_detection_response.json()
                    st.success("Video processed successfully!")
                    st.info(f"Total frames processed: {result['total_frames']}")
                    
                    # Show detection statistics
                    video_detections = result.get('detections', [])
                    if video_detections:
                        video_command_placeholder.empty()  
                        st.subheader("📊 Detection Summary")
                        
                        # Group detections by object
                        object_detections = {}
                        for det in video_detections:
                            label = det['label']
                            frame_id = det.get('frame', 'N/A')
                            if label not in object_detections:
                                object_detections[label] = []
                            object_detections[label].append(frame_id)
                        
                        # Display counts and frame IDs
                        for obj, frames in object_detections.items():
                            st.write(f"- **{obj}**: detected {len(frames)} times (Frames: {', '.join(map(str, frames))})")
                            speak(f"{obj} detected {len(frames)} times in the video.")
                        
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
            speak("General inquiry mode.")
            
            with st.spinner("Processing..."):
                response = ask_general_query(video_file.getvalue(), voiceCommand, isImage=False)
            
            speak(response)
            st.write(response)
            video_command_placeholder.empty()
