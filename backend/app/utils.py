from .yolo_model import YOLOModel

yolo = YOLOModel()

def predict_extract_image_detections(file_path):

    """ Run YOLO prediction"""
    result = yolo.predict(file_path)

    """Process detections to count unique objects"""
    detections = []

    for box in result.boxes:
        x1, y1, x2, y2 = map(float, box.xyxy[0])
        cls = int(box.cls[0])
        label = result.names[cls]
        conf = float(box.conf[0])
        detections.append({ 
            "label": label, "confidence": conf, "x1": x1, "y1": y1, "x2": x2, "y2": y2  })  
    
    return detections

def predict_extract_video_detections(cap, out):
    """Process video detections to count unique objects"""
    output_frame_count = 0
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
                    "frame": output_frame_count,
                    "label": label,
                    "confidence": conf
                })
        
        out.write(annotated_frame)
        output_frame_count += 1
    
    cap.release()
    out.release()
    return total_detections, output_frame_count