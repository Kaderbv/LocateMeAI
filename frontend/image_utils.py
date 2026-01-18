from PIL import Image, ImageDraw, ImageFont
import streamlit as st


@st.dialog("📷 Image Preview")
def show_image_preview(image):
    """Display uploaded image in a modal dialog"""
    st.image(image, caption="Uploaded Image", use_container_width=True)


def image_uploader_section():
    """Handle image upload and preview functionality"""
    st.subheader("📷 Upload Image")
    uploaded_file = st.file_uploader("Upload an image for object detection", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        # add a preview of the uploaded image with a preview button
        if st.button("Preview Uploaded Image"):
            # show image in popup when button is clicked
            show_image_preview(uploaded_file)
    
    return uploaded_file


def draw_bounding_boxes(image_file, detections):
    """Draw bounding boxes on the image and display it"""
    image = Image.open(image_file)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    for det in detections:
        label = det["label"]
        conf = round(det["confidence"], 2)
        x1, y1, x2, y2 = det.get("box", (det["x1"], det["y1"], det["x2"], det["y2"]))
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        draw.text((x1, y1 - 10), f"{label} ({conf})", fill="green", font=font)

    st.image(image, caption="Detected Objects", use_container_width=True)
