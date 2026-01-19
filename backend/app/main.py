from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from .yolo_model import YOLOModel
from .intent_classifier import classify_intent
import shutil
import uuid
import os
import cv2
from pathlib import Path

app = FastAPI()
yolo = YOLOModel()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

VIDEO_OUTPUT_DIR = "outputs"
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "YOLO Object Detection API is running."}

@app.post("/detect")
async def detect_objects(file: UploadFile = File(...)):
    # Save uploaded file
    file_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_DIR}/{file_id}.jpg"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run YOLO prediction
    result = yolo.predict(file_path)

    # Extract detections
    detections = []
    for box in result.boxes:
        x1, y1, x2, y2 = map(float, box.xyxy[0])
        cls = int(box.cls[0])
        label = result.names[cls]
        conf = float(box.conf[0])
        detections.append({ 
            "label": label, "confidence": conf, "x1": x1, "y1": y1, "x2": x2, "y2": y2  })
    
    # Cleanup uploaded file
    os.remove(file_path)
    
    return {"detections": detections}

@app.post("/detect-video")
async def detect_video(file: UploadFile = File(...)):
    """Process video and return annotated video with detections"""
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
    
    frame_count = 0
    total_detections = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Run YOLO on frame
        results = yolo.predict(frame)
        
        # Draw bounding boxes on frame
        annotated_frame = results.plot()
        
        # Extract detections from this frame
        for box in results.boxes:
            x1, y1, x2, y2 = map(float, box.xyxy[0])
            cls = int(box.cls[0])
            label = results.names[cls]
            conf = float(box.conf[0])
            
            if conf > 0.5:  # Only include high confidence detections
                total_detections.append({
                    "frame": frame_count,
                    "label": label,
                    "confidence": conf
                })
        
        out.write(annotated_frame)
        frame_count += 1
    
    cap.release()
    out.release()
    
    # Verify output file was created
    if not os.path.exists(output_path):
        return {"error": "Failed to create output video"}
    
    # Cleanup input file
    os.remove(input_path)
    
    return {
        "message": "Video processed successfully",
        "output_file": f"{file_id}_output.mp4",
        "total_frames": frame_count,
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
