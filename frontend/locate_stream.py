import streamlit as st
import requests
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import time
import json
import base64
from speechtotext import speechtotext
from texttospeech import speak
from user_intent_classify import get_user_intent
from model_utils import display_active_model_info
from config import BACKEND_URL
import websocket
import threading

BACKEND_EXTRACT_CLASSES_URL = f"{BACKEND_URL}/extract-classes"
# Convert HTTP URL to WebSocket URL
WS_URL = BACKEND_URL.replace("http://", "ws://").replace("https://", "wss://")
BACKEND_WS_STREAM_URL = f"{WS_URL}/ws/stream-detect"

def locate_by_stream():
    """Handle live web stream detection functionality using WebSocket"""
    
    # Display active model info
    display_active_model_info()
    
    st.subheader("🌐 Live Web Stream Object Detection")
    st.write("Connect to a live stream URL (HTTP, RTSP, or RTMP) and detect objects in real-time.")
    
    # Stream URL input
    col1, col2 = st.columns([3, 1])
    with col1:
        stream_url = st.text_input(
            "Enter Stream URL",
            placeholder="http://example.com/stream or rtsp://camera-ip:554/stream",
            help="Enter the URL of your live stream (HTTP, RTSP, RTMP) or use '0' for webcam"
        )
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        use_webcam = st.checkbox("Use Webcam", help="Check this to use your webcam instead")
    
    # Frame rate control
    col1, col2 = st.columns(2)
    with col1:
        fps_limit = st.slider(
            "Detection FPS",
            min_value=1,
            max_value=30,
            value=5,
            help="Frames per second to process (lower = less CPU usage)"
        )
    with col2:
        confidence_threshold_pct = st.slider(
            "Confidence Threshold (%)",
            min_value=10,
            max_value=100,
            value=25,
            step=5,
            help="Minimum confidence for detections"
        )
        # Convert percentage to decimal for backend
        confidence_threshold = confidence_threshold_pct / 100.0
    
    st.subheader("🎤 Voice Command for Stream Detection")
    st.write("Say things like: **'detect person'**, **'find cars and trucks'**, or **'detect all objects'**")

    # Audio input widget
    audio_data_for_stream = st.audio_input("🎙️ Record your voice command", key="stream_audio_input")
    
    # Initialize session state
    if 'stream_active' not in st.session_state:
        st.session_state.stream_active = False
    if 'stream_classes' not in st.session_state:
        st.session_state.stream_classes = ""
    if 'stream_object_names' not in st.session_state:
        st.session_state.stream_object_names = "all objects"
    if 'last_stream_audio' not in st.session_state:
        st.session_state.last_stream_audio = None
    
    # Process voice command
    if audio_data_for_stream is not None:
        audio_bytes_for_stream = audio_data_for_stream.read()
        audio_hash = hash(audio_bytes_for_stream)
        
        if st.session_state.last_stream_audio != audio_hash:
            st.session_state.last_stream_audio = audio_hash
            
            stream_command_placeholder = st.empty()
            stream_command_placeholder.info("Processing your audio...")
            
            voiceCommand = speechtotext(audio_bytes_for_stream)
            
            if voiceCommand:
                stream_command_placeholder.info(f"Recognized command: {voiceCommand}")
                
                classified_intent = get_user_intent(voiceCommand)
                st.write(f"Classified Intent: **{classified_intent}**")
                
                if classified_intent == "object_detection":
                    speak("Setting up detection for live stream.")
                    
                    try:
                        classes_response = requests.post(
                            BACKEND_EXTRACT_CLASSES_URL,
                            data={"command": voiceCommand},
                            timeout=60
                        )
                        
                        response_data = classes_response.json()
                        classes = response_data.get("class_ids", "")
                        object_names = response_data.get("object_names", "")
                        
                        # Debug: Show what was extracted
                        st.write(f"DEBUG - Extracted classes: `{classes}`, objects: `{object_names}`")
                        
                        if classes and object_names:
                            st.session_state.stream_classes = classes
                            st.session_state.stream_object_names = object_names
                            st.success(f"🎯 Will detect: {object_names} (class IDs: {classes})")
                        else:
                            st.session_state.stream_classes = ""
                            st.session_state.stream_object_names = "all objects"
                            st.info("🎯 Will detect all objects")
                    except Exception as e:
                        st.warning(f"Could not extract classes, will detect all objects. Error: {e}")
                        st.session_state.stream_classes = ""
                        st.session_state.stream_object_names = "all objects"
                    
                    stream_command_placeholder.empty()
                else:
                    speak("Please provide an object detection command for stream processing.")
                    st.warning("Please provide an object detection command (e.g., 'detect person')")
    
    # Display current detection target
    st.info(f"🎯 Current detection target: **{st.session_state.stream_object_names}**")
    
    # Stream control buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        start_button = st.button("▶️ Start Stream", key="start_stream", type="primary")
    with col2:
        stop_button = st.button("⏹️ Stop Stream", key="stop_stream")
    
    if start_button:
        # Validate input
        if not use_webcam and not stream_url:
            st.error("Please enter a stream URL or check 'Use Webcam'")
        else:
            st.session_state.stream_active = True
            speak("Starting live stream detection.")
    
    if stop_button:
        st.session_state.stream_active = False
        speak("Stopping live stream detection.")
        st.info("Stream stopped.")
    
    # Stream processing with WebSocket
    if st.session_state.stream_active:
        # Determine stream source
        if use_webcam:
            source = 0
            st.info("📹 Connecting to webcam...")
        else:
            source = stream_url
            st.info(f"📹 Connecting to stream: {stream_url}")
        
        # Create placeholders for stream display
        stream_placeholder = st.empty()
        stats_placeholder = st.empty()
        
        # Try to open stream
        cap = cv2.VideoCapture(source)
        
        if not cap.isOpened():
            st.error(f"❌ Failed to connect to stream: {source}")
            st.session_state.stream_active = False
            speak("Failed to connect to stream.")
        else:
            st.success("✅ Stream connected successfully!")
            
            frame_count = 0
            detection_count = 0
            start_time = time.time()
            frame_delay = 1.0 / fps_limit
            
            # Connect to WebSocket
            try:
                ws = websocket.create_connection(BACKEND_WS_STREAM_URL, timeout=10)
                st.success("✅ WebSocket connected!")
                
                try:
                    while st.session_state.stream_active:
                        ret, frame = cap.read()
                        
                        if not ret:
                            st.warning("⚠️ Failed to read frame from stream. Reconnecting...")
                            cap.release()
                            time.sleep(2)
                            cap = cv2.VideoCapture(source)
                            continue
                        
                        frame_count += 1
                        
                        # Encode frame to base64
                        try:
                            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                            frame_b64 = base64.b64encode(buffer).decode('utf-8')
                            
                            # Send frame via WebSocket with classes and confidence threshold
                            message = {
                                "frame": frame_b64,
                                "classes": st.session_state.stream_classes,
                                "conf": confidence_threshold  # Send confidence threshold to backend
                            }
                            
                            # Debug: Log what's being sent (only first frame)
                            if frame_count == 1:
                                st.write(f"DEBUG - Sending to backend: classes=`{st.session_state.stream_classes}`, conf={confidence_threshold}")
                            
                            ws.send(json.dumps(message))
                            
                            # Receive detection results
                            ws.settimeout(5.0)  # 5 second timeout
                            response = ws.recv()
                            result = json.loads(response)
                            
                            if result.get("status") == "success":
                                detections = result.get("detections", [])
                                
                                # Draw detections on frame
                                annotated_frame = frame.copy()
                                for det in detections:
                                    x1, y1, x2, y2 = det["bbox"]
                                    class_name = det["class_name"]
                                    confidence = det["confidence"]
                                    
                                    # Note: Backend already filters by confidence threshold
                                    # but we can add additional filtering if needed
                                    
                                    # Draw bounding box
                                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                    
                                    # Draw label with confidence as percentage
                                    label = f"{class_name} {confidence*100:.1f}%"
                                    cv2.putText(
                                        annotated_frame,
                                        label,
                                        (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.5,
                                        (0, 255, 0),
                                        2
                                    )
                                    
                                    detection_count += 1
                                
                                # Convert BGR to RGB for display
                                annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                                
                                # Display frame
                                stream_placeholder.image(annotated_frame_rgb, channels="RGB", use_container_width=True)
                                
                                # Display stats
                                elapsed_time = time.time() - start_time
                                actual_fps = frame_count / elapsed_time if elapsed_time > 0 else 0
                                stats_placeholder.metric(
                                    "Stream Stats",
                                    f"FPS: {actual_fps:.1f} | Frames: {frame_count} | Detections: {len(detections)}"
                                )
                            else:
                                error_msg = result.get("error", "Unknown error")
                                st.warning(f"⚠️ Detection error: {error_msg}")
                        
                        except websocket.WebSocketTimeoutException:
                            st.warning("⚠️ WebSocket timeout - skipping frame")
                        except Exception as e:
                            st.error(f"❌ Error processing frame: {e}")
                            break
                        
                        # Control frame rate
                        time.sleep(frame_delay)
                        
                except Exception as e:
                    st.error(f"❌ Stream error: {e}")
                finally:
                    ws.close()
                    cap.release()
                    st.session_state.stream_active = False
                    st.info("Stream ended.")
                    
            except Exception as e:
                st.error(f"❌ WebSocket connection failed: {e}")
                cap.release()
                st.session_state.stream_active = False
    
    # Help section
    with st.expander("ℹ️ Help & Examples"):
        st.markdown("""
        ### Supported Stream Types:
        - **Webcam**: Check "Use Webcam" to use your local webcam
        - **HTTP Stream**: `http://example.com/stream.mjpg`
        - **RTSP Stream**: `rtsp://username:password@camera-ip:554/stream`
        - **RTMP Stream**: `rtmp://example.com/live/stream`
        
        ### How It Works:
        - Uses **WebSocket** for efficient real-time streaming
        - Maintains a single persistent connection
        - Model stays loaded in memory for faster detection
        - Frames are sent continuously without HTTP overhead
        
        ### Tips:
        - Lower FPS = Less CPU usage but slower detections
        - Use voice commands to specify what objects to detect
        - Adjust confidence threshold to filter out weak detections
        - Some streams may require authentication in the URL
        - If stream fails, check your network connection and stream URL
        
        ### Voice Command Examples:
        - "detect person"
        - "find cars and trucks"
        - "detect all objects"
        - "locate dogs and cats"
        """)

