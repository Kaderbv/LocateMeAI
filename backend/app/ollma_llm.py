import requests
import base64
import cv2
import numpy as np
import tempfile
import os

def pull_model(model_name: str):
    """Pull a model from Ollama. The API returns streaming responses."""
    response = requests.post(
        "http://localhost:11434/api/pull",
        json={"name": model_name},
        stream=True
    )
    # Process streaming response
    for line in response.iter_lines():
        if line:
            # Each line is a JSON object with status updates
            pass  # You could log progress here if needed
    return response.status_code == 200

def query_llm(content: bytes, question: str, isImage: bool) -> str:
    """Query the LLM model with an image/video and a question using Ollama API."""
    try:
        if isImage:
            # Process single image
            encoded_content = base64.b64encode(content).decode('utf-8')
            return _query_ollama_with_image(encoded_content, question)
        else:
            # Process video by extracting frames
            return _query_ollama_with_video(content, question)
    except Exception as e:
        return f"Error querying LLM: {str(e)}"

def _query_ollama_with_image(encoded_image: str, question: str) -> str:
    """Query Ollama with a single image."""
    payload = {
        "model": "llava",
        "prompt": question,
        "images": [encoded_image],
        "stream": False
    }
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        return result.get("response", "No response from LLM.")
    else:
        return f"Error querying LLM: {response.status_code} - {response.text}"

def _query_ollama_with_video(video_content: bytes, question: str) -> str:
    """Query Ollama with video by extracting and analyzing key frames."""
    # Save video to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        tmp.write(video_content)
        tmp_path = tmp.name
    
    try:
        # Open video and extract frames
        cap = cv2.VideoCapture(tmp_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Extract 3-5 evenly spaced frames (adjust as needed)
        num_frames = min(3, total_frames)
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        
        responses = []
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            
            if ret:
                # Encode frame as JPEG then base64
                _, buffer = cv2.imencode('.jpg', frame)
                encoded_frame = base64.b64encode(buffer).decode('utf-8')
                
                # Query with frame-specific prompt
                frame_question = f"Frame {idx}/{total_frames}: {question}"
                response = _query_ollama_with_image(encoded_frame, frame_question)
                responses.append(f"Frame {idx}: {response}")
        
        cap.release()
        
        # Combine responses
        if responses:
            return "\n\n".join(responses)
        else:
            return "Could not extract frames from video."
            
    finally:
        # Cleanup temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
