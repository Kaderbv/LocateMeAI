"""Fine-tuning module for YOLO model"""
import streamlit as st
import requests
from config import BACKEND_URL
from model_utils import get_active_model_cached, invalidate_model_cache
import io
import zipfile

BACKEND_FINETUNE_URL = f"{BACKEND_URL}/finetune"
BACKEND_LIST_MODELS_URL = f"{BACKEND_URL}/list-models"
BACKEND_ACTIVE_MODEL_URL = f"{BACKEND_URL}/active-model"
BACKEND_SET_ACTIVE_MODEL_URL = f"{BACKEND_URL}/set-active-model"

def fine_tune_model():
    """UI for fine-tuning the YOLO model"""
    
    st.header("🎯 Fine-tune YOLO Model")
    
    # Display current active model (cached)
    active_model_info = get_active_model_cached()
    if active_model_info:
        active_model = active_model_info.get('active_model', 'yolov8n.pt')
        is_default = active_model_info.get('is_default', True)
        
        if is_default:
            st.info(f"🔵 **Currently using:** Default Model ({active_model})")
        else:
            st.success(f"✅ **Currently using:** Custom Model - {active_model}")
    
    st.markdown("""
    Upload training images with their annotations to fine-tune the YOLO model for your specific use case.
    """)
    
    # Instructions
    with st.expander("📋 Instructions"):
        st.markdown("""
        **How to prepare your dataset:**
        1. Organize your images in a folder
        2. Create YOLO format annotation files (.txt) for each image
        3. Each annotation file should have the same name as the image (e.g., image1.jpg → image1.txt)
        4. Annotation format: `class_id center_x center_y width height` (normalized 0-1)
        5. Upload all files (images and annotations) together
        
        **Example annotation:**
        ```
        0 0.5 0.5 0.3 0.4
        1 0.2 0.3 0.15 0.2
        ```
        """)
    
    # Training parameters
    st.subheader("⚙️ Training Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        epochs = st.number_input("Number of Epochs", min_value=1, max_value=300, value=10, step=1)
        batch_size = st.number_input("Batch Size", min_value=1, max_value=64, value=16, step=1)
    
    with col2:
        img_size = st.selectbox("Image Size", [416, 640, 1280], index=1)
        model_name = st.text_input("Model Name", value="yolov8n_finetuned", 
                                   help="Name for your fine-tuned model")
    
    # File upload
    st.subheader("📁 Upload Training Data")
    
    uploaded_files = st.file_uploader(
        "Upload images and annotation files",
        type=["jpg", "jpeg", "png", "txt"],
        accept_multiple_files=True,
        help="Select both images and their corresponding .txt annotation files"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} files uploaded")
        
        # Show file summary
        images = [f for f in uploaded_files if f.name.lower().endswith(('.jpg', '.jpeg', '.png'))]
        annotations = [f for f in uploaded_files if f.name.lower().endswith('.txt')]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Images", len(images))
        with col2:
            st.metric("Annotations", len(annotations))
        
        # Validation
        if len(images) == 0:
            st.warning("⚠️ No images found. Please upload image files.")
        elif len(annotations) == 0:
            st.warning("⚠️ No annotation files found. Please upload .txt annotation files.")
        elif len(images) != len(annotations):
            st.warning(f"⚠️ Number of images ({len(images)}) doesn't match annotations ({len(annotations)})")
    
    # Start training button
    if st.button("🚀 Start Training", type="primary", disabled=not uploaded_files):
        if not uploaded_files:
            st.error("Please upload training data first")
            return
        
        with st.spinner("Training model... This may take several minutes."):
            try:
                # Create a zip file in memory
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file in uploaded_files:
                        file.seek(0)  # Reset file pointer
                        zip_file.writestr(file.name, file.read())
                
                zip_buffer.seek(0)
                
                # Prepare the request
                files = {
                    'file': ('dataset.zip', zip_buffer, 'application/zip')
                }
                
                data = {
                    'epochs': epochs,
                    'batch_size': batch_size,
                    'img_size': img_size,
                    'model_name': model_name
                }
                
                # Send request to backend
                response = requests.post(
                    BACKEND_FINETUNE_URL,
                    files=files,
                    data=data,
                    timeout=3600  # 1 hour timeout for training
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Training completed successfully!")
                    
                    # Display results
                    st.subheader("📊 Training Results")
                    col1, col2, col3 = st.columns(3)
                    
                    if 'metrics' in result:
                        metrics = result['metrics']
                        with col1:
                            st.metric("mAP50", f"{metrics.get('mAP50', 0):.3f}")
                        with col2:
                            st.metric("mAP50-95", f"{metrics.get('mAP50-95', 0):.3f}")
                        with col3:
                            st.metric("Final Loss", f"{metrics.get('loss', 0):.4f}")
                    
                    st.info(f"📦 Model saved as: {result.get('model_path', model_name)}")
                    
                else:
                    st.error(f"Training failed: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error during training: {str(e)}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Refresh Model List", key="refresh_models"):
            st.rerun()
    
    try:
        response = requests.get(BACKEND_LIST_MODELS_URL)
        if response.status_code == 200:
            models_data = response.json()
            models = models_data.get('models', [])
            
            if models:
                st.markdown("**Available Models:**")
                
                # Get current active model (using cached value)
                current_active = "yolov8n.pt"
                active_model_info = get_active_model_cached()
                if active_model_info:
                    current_active = active_model_info.get('active_model', 'yolov8n.pt')
                
                # Model selection
                selected_model = st.selectbox(
                    "Select a model to use for detection:",
                    options=models,
                    index=models.index(current_active) if current_active in models else 0,
                    key="model_selector"
                )
                
                # Set as active button
                col_btn1, col_btn2 = st.columns([1, 3])
                with col_btn1:
                    if st.button("✅ Set as Active", key="set_active_btn"):
                        try:
                            set_response = requests.post(
                                BACKEND_SET_ACTIVE_MODEL_URL,
                                data={'model_path': selected_model}
                            )
                            if set_response.status_code == 200:
                                # Invalidate cache so next fetch gets fresh data
                                invalidate_model_cache()
                                st.success(f"✅ Active model set to: {selected_model}")
                                st.rerun()
                            else:
                                st.error("Failed to set active model")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                # Display model list
                st.markdown("---")
                st.markdown("**All Available Models:**")
                for i, model in enumerate(models):
                    is_active = model == current_active
                    icon = "🟢" if is_active else "⚪"
                    status = " **(ACTIVE)**" if is_active else ""
                    st.text(f"{icon} {model}{status}")
            else:
                st.info("No models found. Train a model to see it here!")
    except Exception as e:
        st.error(f"Error loading models: {str(e)}")

    # Model management
    st.divider()
    st.subheader("📦 Trained Models")
    
    if st.button("🔄 Refresh Model List"):
        try:
            response = requests.get(f"{BACKEND_URL}/list-models")
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    for model in models:
                        st.text(f"• {model}")
                else:
                    st.info("No custom models found")
        except Exception as e:
            st.error(f"Error loading models: {str(e)}")
