from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from .intent_classifier import classify_intent
from .utils import predict_extract_image_detections, predict_extract_video_detections
import shutil
import uuid
import os
import cv2
from pathlib import Path
from .ollma_llm import pull_model, query_llm, extract_classes_from_command
from .config import OLLAMA_MODEL_NAME
# Load environment variables from .env file


app = FastAPI()


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

VIDEO_OUTPUT_DIR = "outputs"
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Pull the llava model on startup (non-blocking)"""
    try:
        print("Checking Ollama model...")
        # Run model pull in background - don't block startup
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, pull_model, OLLAMA_MODEL_NAME)
        print("Model pull initiated in background")
    except Exception as e:
        print(f"Warning: Could not pull model: {e}")

@app.get("/")
async def root():
    return {"message": "YOLO Object Detection API is running."}

@app.post("/detect")
async def detect_image(
    file: UploadFile = File(...),
    classes: str = Form(None)
):
    """Detect objects in image. Optionally filter by class IDs (comma-separated)."""
    # Parse classes if provided
    class_list = None
    if classes:
        try:
            class_list = [int(c.strip()) for c in classes.split(',')]
        except ValueError:
            return {"error": "Invalid classes format. Use comma-separated integers (e.g., '0,2,16')"}
    
    # Save uploaded file
    file_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_DIR}/{file_id}.jpg"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run prediction and extract detections
    detections = predict_extract_image_detections(file_path, classes=class_list)

    # Cleanup uploaded file
    os.remove(file_path)
    
    return {"detections": detections}

@app.post("/detect-video")
async def detect_video(
    file: UploadFile = File(...),
    classes: str = Form(None)
):
    """Process video and return annotated video with detections. Optionally filter by class IDs."""
    # Parse classes if provided
    class_list = None
    if classes:
        try:
            class_list = [int(c.strip()) for c in classes.split(',')]
        except ValueError:
            return {"error": "Invalid classes format. Use comma-separated integers (e.g., '0,2,16')"}
    
    # Save uploaded video
    file_id = str(uuid.uuid4())
    input_path = f"{UPLOAD_DIR}/{file_id}_{file.filename}"
    output_path = f"{VIDEO_OUTPUT_DIR}/{file_id}_output.mp4"
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Open video
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # Video writer - use H.264 codec for web compatibility
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Check if video writer opened successfully
    if not out.isOpened():
        # Fallback to mp4v if avc1 fails
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    
    total_detections, output_frame_count = predict_extract_video_detections(cap, out, classes=class_list)

    # Verify output file was created
    if not os.path.exists(output_path):
        return {"error": "Failed to create output video"}
    
    # Cleanup input file
    os.remove(input_path)
    
    return {
        "message": "Video processed successfully",
        "output_file": f"{file_id}_output.mp4",
        "total_frames": output_frame_count,
        "detections": total_detections
    }

@app.get("/download-video/{filename}")
async def download_video(filename: str):
    """Download processed video"""
    file_path = f"{VIDEO_OUTPUT_DIR}/{filename}"
    print(f"Looking for video at: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        print(f"File size: {file_size} bytes")
        return FileResponse(file_path, media_type="video/mp4", filename=filename)
    
    print(f"File not found: {file_path}")
    return {"error": "File not found"}

@app.post("/classify-intent")
async def classify_intent_endpoint(text: str):
    """Classify user intent from text"""    
    intent = classify_intent(text)
    return {"intent": intent}

@app.post("/extract-classes")
async def extract_classes_endpoint(command: str = Form(...)):
    """Extract YOLO class IDs from natural language command using LLM"""
    result = extract_classes_from_command(command)
    return {
        "class_ids": result["class_ids"],
        "object_names": result["object_names"]
    }

@app.post("/ask-general-query")
async def general_query(
    file: UploadFile = File(...),
    question: str = Form(...),
    isImage: str = Form(...),
    ):
    """Handle LLM queries for images and videos"""
    # Convert string to boolean
    is_image_bool = isImage.lower() in ('true', '1', 'yes')
    
    response = query_llm(await file.read(), question, isImage=is_image_bool)
    return {"response": response}
