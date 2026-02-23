"""Fine-tuning utilities for YOLO model"""
from ultralytics import YOLO
import os
import shutil
import yaml
from pathlib import Path
import zipfile


def prepare_dataset(zip_path: str, extract_dir: str):
    """
    Extract and organize uploaded dataset into YOLO format.
    
    Args:
        zip_path: Path to the uploaded zip file
        extract_dir: Directory to extract files to
        
    Returns:
        dict: Dataset paths and statistics
    """
    # Create directory structure
    dataset_dir = os.path.join(extract_dir, "dataset")
    images_dir = os.path.join(dataset_dir, "images", "train")
    labels_dir = os.path.join(dataset_dir, "labels", "train")
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)
    
    # Extract zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # Organize files
    image_extensions = {'.jpg', '.jpeg', '.png'}
    image_count = 0
    label_count = 0
    
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            if file_ext in image_extensions:
                # Copy image to images/train
                shutil.copy(file_path, os.path.join(images_dir, file))
                image_count += 1
            elif file_ext == '.txt':
                # Copy label to labels/train
                shutil.copy(file_path, os.path.join(labels_dir, file))
                label_count += 1
    
    return {
        "dataset_dir": dataset_dir,
        "images_dir": images_dir,
        "labels_dir": labels_dir,
        "image_count": image_count,
        "label_count": label_count
    }


def create_dataset_yaml(dataset_dir: str, num_classes: int = 80):
    """
    Create dataset.yaml file for YOLO training.
    
    Args:
        dataset_dir: Root directory of the dataset
        num_classes: Number of classes in the dataset
        
    Returns:
        str: Path to the created yaml file
    """
    yaml_path = os.path.join(dataset_dir, "dataset.yaml")
    
    # Create YAML configuration
    dataset_config = {
        'path': dataset_dir,
        'train': 'images/train',
        'val': 'images/train',  # Using same for validation (simple setup)
        'nc': num_classes,
        'names': [f'class_{i}' for i in range(num_classes)]
    }
    
    with open(yaml_path, 'w') as f:
        yaml.dump(dataset_config, f, default_flow_style=False)
    
    return yaml_path


def train_yolo_model(
    data_yaml: str,
    epochs: int = 10,
    batch_size: int = 16,
    img_size: int = 640,
    base_model: str = "yolov8n.pt",
    project_dir: str = "runs/finetune",
    name: str = "exp"
):
    """
    Train/fine-tune YOLO model.
    
    Args:
        data_yaml: Path to dataset.yaml file
        epochs: Number of training epochs
        batch_size: Batch size for training
        img_size: Image size for training
        base_model: Base YOLO model to fine-tune from
        project_dir: Directory to save training results
        name: Experiment name
        
    Returns:
        dict: Training results and metrics
    """
    # Load base model
    model = YOLO(base_model)
    
    # Train the model
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=img_size,
        project=project_dir,
        name=name,
        exist_ok=True,
        patience=50,  # Early stopping patience
        save=True,
        plots=True,
        verbose=True
    )
    
    # Get best model path
    best_model_path = os.path.join(project_dir, name, "weights", "best.pt")
    last_model_path = os.path.join(project_dir, name, "weights", "last.pt")
    
    # Extract metrics
    metrics = {}
    if hasattr(results, 'results_dict'):
        metrics = results.results_dict
    
    return {
        "best_model_path": best_model_path,
        "last_model_path": last_model_path,
        "metrics": metrics,
        "results": results
    }


def list_trained_models(models_dir: str = "runs/finetune"):
    """
    List all trained models.
    
    Args:
        models_dir: Directory containing trained models
        
    Returns:
        list: List of model paths
    """
    models = []
    
    if not os.path.exists(models_dir):
        return models
    
    for root, dirs, files in os.walk(models_dir):
        for file in files:
            if file == "best.pt" or file == "last.pt":
                models.append(os.path.join(root, file))
    
    return models


def cleanup_training_files(extract_dir: str):
    """Clean up temporary training files"""
    try:
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
    except Exception as e:
        print(f"Warning: Could not clean up {extract_dir}: {e}")
