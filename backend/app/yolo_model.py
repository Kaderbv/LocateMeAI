from ultralytics import YOLO
from .config import DEFAULT_YOLO_MODEL

# Define a YOLOModel class to encapsulate model loading and prediction
class YOLOModel:
    def __init__(self, classes=None, model_path=None):
        """
        Initialize YOLO model.
        
        Args:
            classes: List of class IDs to detect (e.g., [0, 1, 2] for person, bicycle, car)
                    None = detect all classes
                    Common COCO classes:
                    0: person, 1: bicycle, 2: car, 3: motorcycle, 5: bus, 7: truck
                    15: bird, 16: cat, 17: dog, 24: backpack, 39: bottle, 41: cup
            model_path: Path to YOLO model file (default: uses DEFAULT_YOLO_MODEL)
        """      
        # Loads YOLOv8 pretrained or custom model
        if model_path is None:
            model_path = DEFAULT_YOLO_MODEL
        self.model = YOLO(model_path)
        self.classes = classes

    def predict(self, image_path: str, stream: bool = False, conf: float = 0.25, iou: float = 0.7, verbose: bool = False):
        """
        Run YOLO prediction on image or video frame.
        
        Args:
            image_path: Path to image file or numpy array (frame)
            stream: Use stream mode for better memory efficiency (recommended for video)
            conf: Confidence threshold for detections (default: 0.25)
            iou: IoU threshold for NMS (default: 0.7)
            verbose: Print prediction info
            
        Returns:
            Single result object when stream=False, or generator when stream=True
        """
        # Build prediction arguments
        predict_args = {
            'conf': conf,
            'iou': iou,
            'verbose': verbose,
            'stream': stream
        }
        
        # Add class filtering if specified
        if self.classes is not None:
            predict_args['classes'] = self.classes
        
        # Run prediction with optimized parameters
        results = self.model(image_path, **predict_args)
        
        # If stream mode, return generator; otherwise return first result
        if stream:
            return results  # Returns generator
        else:
            return results[0]  # Returns single result
    
    def predict_stream(self, source, conf: float = 0.25, iou: float = 0.7, verbose: bool = False):
        """
        Optimized method for streaming predictions (video/webcam).
        Uses stream=True by default for better performance.
        
        Args:
            source: Video file path, stream URL, or numpy array
            conf: Confidence threshold
            iou: IoU threshold for NMS
            verbose: Print prediction info
            
        Returns:
            Generator yielding results for each frame
        """
        predict_args = {
            'conf': conf,
            'iou': iou,
            'verbose': verbose,
            'stream': True  # Always use stream mode for this method
        }
        
        if self.classes is not None:
            predict_args['classes'] = self.classes
        
        return self.model(source, **predict_args)
