# YOLO Model Fine-tuning and Custom Model Usage Guide

## Overview

LocateMeAI now supports fine-tuning the YOLO model with your custom datasets and seamlessly switching between different models for object detection. This allows you to train the model on specific objects relevant to your use case and use those custom-trained models for detection.

## Features

### 1. **Fine-tune YOLO Model**
- Upload custom training datasets (images + annotations)
- Configure training parameters (epochs, batch size, image size)
- Train new models on specific object classes
- View training metrics and results

### 2. **Model Management**
- List all available models (default + fine-tuned)
- Switch between models with one click
- Visual indicators for active model
- Persistent model selection across sessions

### 3. **Use Custom Models for Detection**
- All detection operations (image and video) use the active model
- Real-time feedback on which model is being used
- Easy switching between default and custom models

---

## How to Fine-tune a Model

### Step 1: Prepare Your Dataset

Your dataset must follow the YOLO annotation format:

#### File Structure:
```
dataset/
├── image1.jpg
├── image1.txt
├── image2.jpg
├── image2.txt
└── ...
```

#### Annotation Format (`.txt` files):
Each line represents one object in the format:
```
class_id center_x center_y width height
```

- **class_id**: Integer representing the object class (0, 1, 2, ...)
- **center_x, center_y**: Normalized center coordinates (0-1)
- **width, height**: Normalized dimensions (0-1)

**Example:**
```
0 0.5 0.5 0.3 0.4
1 0.2 0.3 0.15 0.2
```

### Step 2: Upload and Train

1. Navigate to the **"🎯 Fine-tune Model"** tab
2. Configure training parameters:
   - **Epochs**: Number of training iterations (default: 10)
   - **Batch Size**: Images per training batch (default: 16)
   - **Image Size**: Input image dimension (416, 640, or 1280)
   - **Model Name**: Name for your custom model
3. Click **"Upload images and annotation files"**
4. Select all your images and annotation files
5. Click **"🚀 Start Training"**
6. Wait for training to complete (may take several minutes)

### Step 3: View Results

After training completes, you'll see:
- **mAP50**: Mean Average Precision at 50% IoU
- **mAP50-95**: Mean Average Precision from 50% to 95% IoU
- **Final Loss**: Training loss value
- **Model Path**: Location where the model was saved

---

## How to Use Your Fine-tuned Model

### Activate a Custom Model

1. Go to the **"🎯 Fine-tune Model"** tab
2. Scroll to **"📦 Model Management"** section
3. Click **"🔄 Refresh Model List"** to see all available models
4. Select your trained model from the dropdown menu
5. Click **"✅ Set as Active"**
6. You'll see a success message confirming the model switch

### Visual Indicators

**In Fine-tune Tab:**
- At the top: Shows current active model
  - 🔵 Blue info box = Default model active
  - ✅ Green box = Custom model active

**In Detection Tabs (Image/Video):**
- At the top: Shows which model is being used for detection
  - 🔵 Blue = Default (yolov8n.pt)
  - 🟢 Green = Custom Fine-tuned model

**In Model List:**
- 🟢 Green circle = Currently active model
- ⚪ White circle = Available but not active

### Switch Back to Default Model

1. Go to **"🎯 Fine-tune Model"** tab
2. In **"📦 Model Management"** section
3. Select **"yolov8n.pt"** from the dropdown
4. Click **"✅ Set as Active"**

---

## Using Custom Models for Detection

Once a custom model is set as active:

### Image Detection
1. Go to **"📷 Locate By Image"** tab
2. Notice the green indicator showing your custom model
3. Upload an image
4. Use voice commands or text to detect objects
5. Detection uses your fine-tuned model automatically

### Video Detection
1. Go to **"🎥 Locate By Video"** tab
2. Notice the green indicator showing your custom model
3. Upload a video
4. Use voice commands or text to detect objects
5. Video processing uses your fine-tuned model automatically

---

## Technical Implementation

### Backend Architecture

#### New Files:
- **`backend/app/finetune_utils.py`**
  - `prepare_dataset()` - Extracts and organizes datasets
  - `create_dataset_yaml()` - Creates YOLO config files
  - `train_yolo_model()` - Handles model training
  - `list_trained_models()` - Lists all trained models
  - `cleanup_training_files()` - Cleanup utility

#### Modified Files:
- **`backend/app/main.py`**
  - Model state management functions
  - Fine-tuning endpoint: `POST /finetune`
  - Model management endpoints:
    - `GET /list-models` - List all models
    - `GET /active-model` - Get current active model
    - `POST /set-active-model` - Set active model
  - Updated detection endpoints to use active model

- **`backend/app/yolo_model.py`**
  - Added `model_path` parameter to `__init__()`
  - Supports loading custom models

- **`backend/app/utils.py`**
  - Added `model_path` parameter to detection functions
  - Passes custom model to YOLO instances

### Frontend Architecture

#### New Files:
- **`frontend/fine_tuning.py`**
  - Complete fine-tuning UI
  - Training parameter configuration
  - Model management interface
  - Model selection and activation

#### Modified Files:
- **`frontend/app.py`**
  - Added "🎯 Fine-tune Model" tab

- **`frontend/locate_image.py`**
  - Displays active model indicator

- **`frontend/locate_video.py`**
  - Displays active model indicator

### Data Flow

```
1. Training Flow:
   User uploads dataset → Frontend packages as ZIP → Backend extracts files →
   Dataset organized → Training starts → Model saved → User notified

2. Model Activation Flow:
   User selects model → Frontend sends request → Backend updates active_model.txt →
   Confirmation sent → UI updates indicators

3. Detection Flow:
   User uploads media → Backend reads active_model.txt → Loads appropriate model →
   Runs detection → Returns results
```

---

## File Locations

### Trained Models
- Saved in: `backend/runs/finetune/[model_name]/weights/`
- Best model: `best.pt`
- Last checkpoint: `last.pt`

### Active Model Configuration
- Stored in: `backend/active_model.txt`
- Contains path to currently active model

### Temporary Training Files
- Location: `backend/finetune_temp/`
- Automatically cleaned up after training

---

## API Endpoints

### Fine-tuning
```http
POST /finetune
Content-Type: multipart/form-data

Parameters:
- file: ZIP file with images and annotations
- epochs: Number of training epochs (int)
- batch_size: Batch size (int)
- img_size: Image size (int)
- model_name: Name for the model (string)

Response:
{
  "message": "Training completed successfully",
  "model_path": "path/to/model",
  "dataset_info": {...},
  "training_params": {...},
  "metrics": {...}
}
```

### List Models
```http
GET /list-models

Response:
{
  "models": ["yolov8n.pt", "custom_model/weights/best.pt", ...],
  "count": 3
}
```

### Get Active Model
```http
GET /active-model

Response:
{
  "active_model": "yolov8n.pt",
  "is_default": true
}
```

### Set Active Model
```http
POST /set-active-model
Content-Type: application/x-www-form-urlencoded

Parameters:
- model_path: Path to the model (string)

Response:
{
  "message": "Active model updated successfully",
  "active_model": "custom_model/weights/best.pt"
}
```

---

## Best Practices

### Dataset Preparation
- **Minimum images**: At least 100 images per class
- **Image quality**: Clear, well-lit images
- **Annotations**: Accurate bounding boxes
- **Variety**: Different angles, lighting, backgrounds
- **Balance**: Similar number of samples per class

### Training Parameters
- **Start small**: Begin with 10-20 epochs
- **Batch size**: 16 is a good default, reduce if out of memory
- **Image size**: 640 is balanced, use 1280 for small objects
- **Monitor metrics**: Check mAP50 to evaluate performance

### Model Selection
- **Testing**: Test custom models before production use
- **Benchmarking**: Compare with default model on test set
- **Fallback**: Keep default model available as backup
- **Documentation**: Name models descriptively

---

## Troubleshooting

### Training Issues

**Problem**: Training takes too long
- **Solution**: Reduce epochs, batch size, or image size

**Problem**: Out of memory error
- **Solution**: Reduce batch size to 8 or 4

**Problem**: Poor performance (low mAP)
- **Solution**: Add more training data, increase epochs, or improve annotations

### Model Selection Issues

**Problem**: Custom model not appearing in list
- **Solution**: Click "🔄 Refresh Model List" button

**Problem**: Cannot activate model
- **Solution**: Verify model file exists in `runs/finetune/` directory

**Problem**: Detection not using custom model
- **Solution**: Check active model indicator, re-activate if needed

---

## Example Use Cases

### 1. **Custom Item Detection**
- Train on your personal items (phone, keys, glasses)
- Use for everyday object location
- Higher accuracy on specific objects

### 2. **Specialized Objects**
- Industrial parts identification
- Medical equipment detection
- Retail product recognition

### 3. **Domain-Specific Applications**
- Wildlife monitoring (specific species)
- Agriculture (crop/pest detection)
- Security (specific items/people)

---

## Performance Metrics

### mAP (Mean Average Precision)
- **mAP50**: Accuracy at 50% IoU threshold
  - Good: > 0.7
  - Excellent: > 0.9
- **mAP50-95**: Average across multiple IoU thresholds
  - Good: > 0.5
  - Excellent: > 0.7

### Training Loss
- Should decrease over epochs
- Very low loss may indicate overfitting
- Aim for balanced performance

---

## Future Enhancements

Potential improvements for future versions:
- Data augmentation options
- Transfer learning from different base models
- Model performance comparison dashboard
- Automatic hyperparameter tuning
- Model export for edge devices
- Training progress visualization
- Dataset validation tools

---

## Support

For issues or questions:
1. Check training logs in `runs/finetune/[model_name]/`
2. Verify dataset format matches YOLO requirements
3. Review active model selection in the UI
4. Check backend logs for API errors

---

**Last Updated**: February 6, 2026
**Version**: 1.0.0
