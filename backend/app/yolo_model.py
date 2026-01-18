from ultralytics import YOLO

# Define a YOLOModel class to encapsulate model loading and prediction
class YOLOModel:
    def __init__(self):
        # Loads YOLOv8 pretrained on COCO dataset 
        self.model = YOLO("yolov8n.pt")

    def predict(self, image_path: str):
        results = self.model(image_path)
        return results[0]
