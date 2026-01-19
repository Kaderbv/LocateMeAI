import streamlit as st # type: ignore
import io
import requests

BACKEND_VIDEO_DOWNLOAD_URL = "http://localhost:8000/download-video"

@st.dialog("🎥 Video Preview")
def show_video_preview(video):
    """Display uploaded video in a modal dialog"""
    st.video(video, format="video/mp4", start_time=0)


def video_uploader_section():
    """UI section for uploading video files"""
    st.subheader("🎥 Upload Video")
    video_file = st.file_uploader("Upload a video for object detection", type=["mp4", "avi", "mov"], key="video_uploader")
    if video_file:
        # add a preview of the uploaded video with a preview button
        if st.button("Preview Uploaded video"):
            # show video in popup when button is clicked
            show_video_preview(video_file)
    return video_file

def download_video(output_file: str) -> bytes:
    """Downloads video from the given URL and returns its content as bytes."""
    download_url = f"{BACKEND_VIDEO_DOWNLOAD_URL}/{output_file}"
                      
    st.subheader("🎥 Processed Video with Detections")

    # Use session state to persist video content across reruns
    cache_key = f"video_content_{output_file}"
    
    if cache_key not in st.session_state:
        try:
            # Fetch the video file from backend
            video_response = requests.get(download_url, timeout=30)
            
            if video_response.status_code == 200:
                video_content = video_response.content
                
                # Verify we actually got video content
                if len(video_content) > 0:
                    st.video(video_content)
        
                    st.download_button(
                        label="📥 Download Processed Video",
                        data=video_content,
                        file_name=f"detected_{output_file}",
                        mime="video/mp4",
                        key=f"download_{output_file}"
                    )
                else:
                    st.error("Received empty video file.")
                    return
            else:
                st.error(f"Could not load processed video. Status: {video_response.status_code}")
                if video_response.status_code == 404:
                    st.error("Video file not found on server.")
                return
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching video: {str(e)}")
            return