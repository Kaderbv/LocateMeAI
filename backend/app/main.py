from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from .intent_classifier import classify_intent
from .utils import predict_extract_image_detections, predict_extract_video_detections
from .finetune_utils import prepare_dataset, create_dataset_yaml, train_yolo_model, list_trained_models, cleanup_training_files
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

FINETUNE_DIR = "finetune_temp"
os.makedirs(FINETUNE_DIR, exist_ok=True)

MODELS_DIR = "runs/finetune"
os.makedirs(MODELS_DIR, exist_ok=True)

# Data directory for configuration files
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Active model configuration
ACTIVE_MODEL_FILE = os.path.join(DATA_DIR, "active_model.txt")
DEFAULT_MODEL = "yolov8n.pt"

def get_active_model():
    """Get the currently active model path"""
    if os.path.exists(ACTIVE_MODEL_FILE):
        with open(ACTIVE_MODEL_FILE, 'r') as f:
            model_path = f.read().strip()
            if model_path and os.path.exists(model_path):
                return model_path
    return DEFAULT_MODEL

def set_active_model(model_path: str):
    """Set the active model path"""
    with open(ACTIVE_MODEL_FILE, 'w') as f:
        f.write(model_path)


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

    # Get active model
    active_model = get_active_model()

    # Run prediction and extract detections
    detections = predict_extract_image_detections(file_path, classes=class_list, model_path=active_model)

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
    
    # Get active model
    active_model = get_active_model()
    
    total_detections, output_frame_count = predict_extract_video_detections(cap, out, classes=class_list, model_path=active_model)

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

@app.post("/finetune")
async def finetune_model(
    file: UploadFile = File(...),
    epochs: int = Form(10),
    batch_size: int = Form(16),
    img_size: int = Form(640),
    model_name: str = Form("yolov8n_finetuned")
):
    """
    Fine-tune YOLO model with uploaded dataset.
    
    Args:
        file: ZIP file containing images and annotation files
        epochs: Number of training epochs
        batch_size: Batch size for training
        img_size: Image size for training
        model_name: Name for the fine-tuned model
    """
    extract_dir = None
    try:
        # Save uploaded zip file
        file_id = str(uuid.uuid4())
        extract_dir = os.path.join(FINETUNE_DIR, file_id)
        os.makedirs(extract_dir, exist_ok=True)
        
        zip_path = os.path.join(extract_dir, "dataset.zip")
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Prepare dataset
        dataset_info = prepare_dataset(zip_path, extract_dir)
        
        if dataset_info["image_count"] == 0:
            return {"error": "No images found in uploaded dataset"}
        
        if dataset_info["label_count"] == 0:
            return {"error": "No annotation files found in uploaded dataset"}
        
        # Create dataset.yaml
        yaml_path = create_dataset_yaml(dataset_info["dataset_dir"])
        
        # Train model
        training_results = train_yolo_model(
            data_yaml=yaml_path,
            epochs=epochs,
            batch_size=batch_size,
            img_size=img_size,
            base_model="yolov8n.pt",
            project_dir=MODELS_DIR,
            name=model_name
        )
        
        # Prepare response
        response = {
            "message": "Training completed successfully",
            "model_path": training_results["best_model_path"],
            "dataset_info": {
                "images": dataset_info["image_count"],
                "labels": dataset_info["label_count"]
            },
            "training_params": {
                "epochs": epochs,
                "batch_size": batch_size,
                "img_size": img_size
            }
        }
        
        # Add metrics if available
        if training_results["metrics"]:
            response["metrics"] = {
                "mAP50": training_results["metrics"].get("metrics/mAP50(B)", 0),
                "mAP50-95": training_results["metrics"].get("metrics/mAP50-95(B)", 0),
                "loss": training_results["metrics"].get("train/box_loss", 0)
            }
        
        return response
        
    except Exception as e:
        return {"error": f"Training failed: {str(e)}"}
    
    finally:
        # Cleanup temporary files
        if extract_dir:
            cleanup_training_files(extract_dir)

@app.get("/list-models")
async def list_models():
    """List all trained models"""
    try:
        models = list_trained_models(MODELS_DIR)
        model_list = [os.path.relpath(m, MODELS_DIR) for m in models]
        
        # Add default model to the list
        model_list.insert(0, DEFAULT_MODEL)
        
        return {
            "models": model_list,
            "count": len(model_list)
        }
    except Exception as e:
        return {"error": f"Failed to list models: {str(e)}"}

@app.get("/active-model")
async def get_current_active_model():
    """Get the currently active model"""
    try:
        active_model = get_active_model()
        return {
            "active_model": active_model,
            "is_default": active_model == DEFAULT_MODEL
        }
    except Exception as e:
        return {"error": f"Failed to get active model: {str(e)}"}

@app.post("/set-active-model")
async def set_current_active_model(model_path: str = Form(...)):
    """Set the active model for detection"""
    try:
        # Validate model exists
        if model_path != DEFAULT_MODEL:
            full_path = os.path.join(MODELS_DIR, model_path) if not os.path.isabs(model_path) else model_path
            if not os.path.exists(full_path):
                return {"error": f"Model not found: {model_path}"}
            set_active_model(full_path)
        else:
            set_active_model(DEFAULT_MODEL)
        
        return {
            "message": "Active model updated successfully",
            "active_model": model_path
        }
    except Exception as e:
        return {"error": f"Failed to set active model: {str(e)}"}
