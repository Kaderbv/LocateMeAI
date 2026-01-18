from fastapi import FastAPI, UploadFile, File
from .yolo_model import YOLOModel
import shutil
import uuid
import os

app = FastAPI()
yolo = YOLOModel()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

    return {"detections": detections}
