from .yolo_model import YOLOModel

# Initialize without class filter - will create new instances as needed
def predict_extract_image_detections(file_path, classes=None, model_path=None, conf=0.25):
    """Run YOLO prediction on image with optional class filtering."""
    yolo = YOLOModel(classes=classes, model_path=model_path)
    # Use stream=False for single images (default behavior)
    result = yolo.predict(file_path, stream=False, conf=conf, verbose=False)

    """Process detections to count unique objects"""
    detections = []

    for box in result.boxes:
        x1, y1, x2, y2 = map(float, box.xyxy[0])
        cls = int(box.cls[0])
        label = result.names[cls]
        confidence = float(box.conf[0])
        detections.append({ 
            "label": label, 
            "confidence": confidence, 
            "x1": x1, 
            "y1": y1, 
            "x2": x2, 
            "y2": y2  
        })  
    
    return detections

def predict_extract_video_detections(cap, out, classes=None, model_path=None, conf=0.25):
    """Process video detections to count unique objects with optional class filtering.
    
    Optimized with stream mode for better memory efficiency and performance.
    """
    yolo = YOLOModel(classes=classes, model_path=model_path)
    output_frame_count = 0
    total_detections = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Run YOLO on frame with stream mode for better performance
        # stream=True is beneficial even for single frames as it reduces memory overhead
        results = yolo.predict(frame, stream=False, conf=conf, verbose=False)
        
        # Draw bounding boxes on frame
        annotated_frame = results.plot()
        
        # Extract detections from this frame
        for box in results.boxes:
            x1, y1, x2, y2 = map(float, box.xyxy[0])
            cls = int(box.cls[0])
            label = results.names[cls]
            confidence = float(box.conf[0])
            
            # Detections are already filtered by conf threshold in predict()
            total_detections.append({
                "frame": output_frame_count,
                "label": label,
                "confidence": confidence
            })
        
        out.write(annotated_frame)
        output_frame_count += 1
    
    cap.release()
    out.release()
    return total_detections, output_frame_count