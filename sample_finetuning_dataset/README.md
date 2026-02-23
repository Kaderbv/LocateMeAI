# Sample Fine-tuning Dataset

This directory contains sample images and annotations for testing the YOLO fine-tuning feature.

## Dataset Overview

This sample dataset contains images of common objects with their YOLO format annotations:
- **Smartphone** (class 0)
- **Keys** (class 1)
- **Glasses** (class 2)
- **Wallet** (class 3)

## File Structure

```
sample_finetuning_dataset/
├── README.md (this file)
├── sample_image_1.txt
├── sample_image_2.txt
├── sample_image_3.txt
├── sample_image_4.txt
├── sample_image_5.txt
└── INSTRUCTIONS.md
```

## How to Use This Sample Dataset

### Option 1: Use Your Own Images

1. **Take photos** of the objects mentioned above (smartphone, keys, glasses, wallet)
2. **Name them** to match the annotation files:
   - `sample_image_1.jpg`
   - `sample_image_2.jpg`
   - `sample_image_3.jpg`
   - `sample_image_4.jpg`
   - `sample_image_5.jpg`
3. **Adjust the annotations** in the `.txt` files to match your images
4. **Upload** all files together in the Fine-tune tab

### Option 2: Create Your Own Dataset

1. **Take photos** of objects you want to detect
2. **Use a labeling tool** like:
   - [LabelImg](https://github.com/heartexlabs/labelImg) (Desktop)
   - [Roboflow](https://roboflow.com/) (Web-based)
   - [CVAT](https://www.cvat.ai/) (Web-based)
3. **Export** in YOLO format
4. **Upload** to the Fine-tune tab

### Option 3: Download Sample Images

You can download free sample images from:
- [Pexels](https://www.pexels.com/) - Free stock photos
- [Unsplash](https://unsplash.com/) - Free high-quality images
- [Pixabay](https://pixabay.com/) - Free images

Search for: "smartphone", "keys", "glasses", "wallet"

## Annotation Format

Each `.txt` file contains bounding box annotations in YOLO format:

```
class_id center_x center_y width height
```

Where:
- **class_id**: Object class (0=smartphone, 1=keys, 2=glasses, 3=wallet)
- **center_x, center_y**: Normalized center coordinates (0.0 to 1.0)
- **width, height**: Normalized box dimensions (0.0 to 1.0)

### Example:
```
0 0.5 0.5 0.3 0.4
```
This means:
- Class 0 (smartphone)
- Center at 50% width, 50% height
- Box width is 30% of image width
- Box height is 40% of image height

## Class Definitions

| Class ID | Object Name | Description |
|----------|-------------|-------------|
| 0 | Smartphone | Mobile phone, cell phone |
| 1 | Keys | House keys, car keys, key ring |
| 2 | Glasses | Eyeglasses, sunglasses |
| 3 | Wallet | Wallet, purse |

## Sample Scenarios

### Sample 1: Single Smartphone
- Image should contain one smartphone
- Could be on a desk, in hand, or on a table
- Annotation: `0 0.5 0.5 0.25 0.45`

### Sample 2: Keys on Keyring
- Image should contain keys
- Could be hanging, on a table, or in hand
- Annotation: `1 0.4 0.6 0.15 0.25`

### Sample 3: Glasses
- Image should contain eyeglasses or sunglasses
- Could be worn or placed on a surface
- Annotation: `2 0.5 0.4 0.3 0.15`

### Sample 4: Multiple Objects
- Image contains smartphone and keys
- Two annotations in the file
- Example:
  ```
  0 0.3 0.5 0.25 0.45
  1 0.7 0.5 0.15 0.25
  ```

### Sample 5: Wallet
- Image should contain a wallet
- Open or closed
- Annotation: `3 0.5 0.5 0.2 0.3`

## Testing Your Annotations

Before fine-tuning, verify your annotations:

1. **Check format**: Each line should have exactly 5 numbers
2. **Check values**: All coordinates should be between 0.0 and 1.0
3. **Check alignment**: Annotation filename should match image filename
4. **Check class IDs**: Should be 0, 1, 2, or 3

## Quick Start

1. Copy this directory
2. Add your images named `sample_image_1.jpg` through `sample_image_5.jpg`
3. Adjust the annotations if needed
4. Upload all files in the "🎯 Fine-tune Model" tab
5. Set training parameters (start with 10 epochs)
6. Click "🚀 Start Training"

## Expected Results

After training with this small dataset (5 images):
- Training will complete in a few minutes
- Model will learn to recognize these specific objects
- mAP may be lower than production models (more data needed)
- Good for testing the fine-tuning workflow

## Expanding the Dataset

For better results:
- Add at least 50-100 images per class
- Include various angles and lighting
- Include different backgrounds
- Include objects at different scales
- Add more variety (different phone models, key types, etc.)

## Troubleshooting

**Q: My annotations don't match the images**
- Use a labeling tool to create accurate annotations

**Q: Training fails**
- Check that image and annotation filenames match
- Verify annotation format is correct

**Q: Poor detection results**
- Add more training images (aim for 100+ per class)
- Increase training epochs (try 50-100)
- Ensure annotations are accurate

## Next Steps

After fine-tuning:
1. Go to "Model Management" section
2. Find your trained model in the list
3. Click "✅ Set as Active"
4. Test detection in the Image or Video tabs
5. Upload an image with one of these objects
6. Say "detect smartphone" or similar command

---

**Note**: This is a minimal sample dataset for testing purposes. For production use, you should have at least 100 images per class with high-quality annotations.
