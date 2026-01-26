from ultralytics import YOLO
from .config import DEFAULT_YOLO_MODEL

# Define a YOLOModel class to encapsulate model loading and prediction
class YOLOModel:
    def __init__(self, classes=None):
        """
        Initialize YOLO model.
        
        Args:
            classes: List of class IDs to detect (e.g., [0, 1, 2] for person, bicycle, car)
                    None = detect all classes
                    Common COCO classes:
                    0: person, 1: bicycle, 2: car, 3: motorcycle, 5: bus, 7: truck
                    15: bird, 16: cat, 17: dog, 24: backpack, 39: bottle, 41: cup
        """      
        # Loads YOLOv8 pretrained on COCO dataset 
        model_path = DEFAULT_YOLO_MODEL
        self.model = YOLO(model_path)
        self.classes = classes

    def predict(self, image_path: str):
        # Only detect specified classes if provided
        if self.classes is not None:
            results = self.model(image_path, classes=self.classes)
        else:
            results = self.model(image_path)
        return results[0]
