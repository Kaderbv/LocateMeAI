import streamlit as st
import requests
import os
from speechtotext import speechtotext
from texttospeech import speak

BACKEND_VIDEO_DETECT_URL = "http://localhost:8000/detect-video"
BACKEND_VIDEO_DOWNLOAD_URL = "http://localhost:8000/download-video"

def locate_by_video():
    """Handle video detection functionality"""
    
    st.subheader("🎥 Upload Video")
    video_file = st.file_uploader("Upload a video for object detection", type=["mp4", "avi", "mov"], key="video_uploader")

    st.subheader("🎤 Voice Command")
    st.write("Say things like: **'detect objects'**, **'start detection'**, **'run YOLO'**")

    if st.button("Start Voice Command for Video"):
        video_command_placeholder = st.empty()
        video_command_placeholder.info("Listening for your command...")
        voiceCommand = speechtotext()
        video_command_placeholder.info(f"Recognized command: {voiceCommand}")

        if voiceCommand and ("detect" in voiceCommand or "start" in voiceCommand or "yolo" in voiceCommand):
            if not video_file:
                st.warning("Please upload a video first.")
                speak("Please upload a video first.")
            else:
                st.video(video_file)
                st.success("Video uploaded successfully! Object detection will be implemented soon.")

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
                      download_url = f"{BACKEND_VIDEO_DOWNLOAD_URL}/{output_file}"
                      
                      st.subheader("🎥 Processed Video with Detections")
                      
                      # Fetch the video file from backend
                      video_response = requests.get(download_url)
                      if video_response.status_code == 200:
                          # Display the processed video with detections
                          st.video(video_response.content)
                          
                          # Also provide download button
                          st.download_button(
                              label="📥 Download Processed Video",
                              data=video_response.content,
                              file_name=f"detected_{output_file}",
                              mime="video/mp4"
                          )
                      else:
                          st.error("Could not load processed video.")
                  
                  video_command_placeholder.empty()
                else:
                    st.error("Backend error. Could not process the video.")
                    speak("Backend error. Could not process the video.")
                    video_command_placeholder.empty()
        else:
            st.warning("Voice command not recognized.")
            speak("Voice command not recognized.")
            video_command_placeholder.empty()
