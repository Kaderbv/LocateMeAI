import streamlit as st # type: ignore
import io
import requests

BACKEND_VIDEO_DOWNLOAD_URL = "http://localhost:8000/download-video"

def download_video(output_file: str) -> bytes:
    """Downloads video from the given URL and returns its content as bytes."""
    download_url = f"{BACKEND_VIDEO_DOWNLOAD_URL}/{output_file}"
                      
    st.subheader("🎥 Processed Video with Detections")

    try:
        # Fetch the video file from backend
        video_response = requests.get(download_url, timeout=30)
        
        if video_response.status_code == 200:
            video_content = video_response.content
            
            # Verify we actually got video content
            if len(video_content) > 0:
                # Display the processed video with detections
                st.video(video_content)
                
                # Also provide download button
                st.download_button(
                    label="📥 Download Processed Video",
                    data=video_content,
                    file_name=f"detected_{output_file}",
                    mime="video/mp4"
                )
            else:
                st.error("Received empty video file.")
        else:
            st.error(f"Could not load processed video. Status: {video_response.status_code}")
            if video_response.status_code == 404:
                st.error("Video file not found on server.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching video: {str(e)}")