# How to Create Images for These Annotations

This guide explains how to take or create images that match the provided annotation files.

## Required Images

You need 5 images named exactly as follows:
- `sample_image_1.jpg`
- `sample_image_2.jpg`
- `sample_image_3.jpg`
- `sample_image_4.jpg`
- `sample_image_5.jpg`

## Image Specifications

### General Guidelines
- **Format**: JPG, JPEG, or PNG
- **Resolution**: 640x640 or higher (1920x1080 recommended)
- **Lighting**: Good, even lighting
- **Background**: Clean, uncluttered background
- **Focus**: Sharp, clear focus on objects

---

## Sample Image 1: Single Smartphone

### Setup:
1. Place a smartphone flat on a clean desk or table
2. Center it in the frame
3. Take photo from directly above (bird's eye view)

### Annotation Details:
- **Object**: Smartphone (any model)
- **Position**: Center of image (50% x, 50% y)
- **Size**: Should occupy roughly 25% width, 45% height

### Example Setup:
```
        |------------|
        |            |
        |   [📱]    |  ← Smartphone centered
        |            |
        |------------|
```

### Tips:
- Ensure entire phone is visible
- Leave some space around edges
- Keep phone flat and straight

---

## Sample Image 2: Keys

### Setup:
1. Place a keyring with 2-3 keys on a surface
2. Position slightly left of center
3. Keys should be in upper portion of image

### Annotation Details:
- **Object**: Keys on keyring
- **Position**: Left-leaning (35% x, 40% y)
- **Size**: About 18% width, 28% height

### Example Setup:
```
        |------------|
        | 🔑         |  ← Keys top-left area
        |            |
        |            |
        |------------|
```

### Tips:
- Keys can overlap slightly
- Ensure all keys are visible
- Natural, casual arrangement

---

## Sample Image 3: Glasses

### Setup:
1. Place eyeglasses or sunglasses flat on a surface
2. Position horizontally (temples extended)
3. Center in the frame

### Annotation Details:
- **Object**: Glasses (eyeglasses or sunglasses)
- **Position**: Centered (50% x, 45% y)
- **Size**: About 35% width, 12% height

### Example Setup:
```
        |------------|
        |            |
        | [=👓=]    |  ← Glasses horizontal
        |            |
        |------------|
```

### Tips:
- Glasses should be open/flat
- Lenses should be visible
- Avoid reflections if possible

---

## Sample Image 4: Multiple Objects (Smartphone + Keys)

### Setup:
1. Place smartphone on LEFT side of frame
2. Place keys on RIGHT side of frame
3. Both objects at similar vertical level

### Annotation Details:
- **Object 1**: Smartphone at left (30% x, 50% y)
- **Object 2**: Keys at right (70% x, 55% y)
- Both should be clearly visible

### Example Setup:
```
        |------------|
        |            |
        | [📱]  🔑  |  ← Phone left, keys right
        |            |
        |------------|
```

### Tips:
- Objects should not overlap
- Leave space between objects
- Both should be clearly identifiable

---

## Sample Image 5: Wallet

### Setup:
1. Place a closed wallet on a surface
2. Center it in the frame
3. Can be photographed from slightly above

### Annotation Details:
- **Object**: Wallet (closed)
- **Position**: Centered (50% x, 50% y)
- **Size**: About 25% width, 35% height

### Example Setup:
```
        |------------|
        |            |
        |   [👛]    |  ← Wallet centered
        |            |
        |------------|
```

### Tips:
- Wallet can be leather, fabric, or any material
- Make sure edges are clearly visible
- Keep wallet closed for consistency

---

## Photography Tips

### Camera Settings:
- **Mode**: Auto is fine
- **Flash**: Use if lighting is poor, but natural light is better
- **Focus**: Tap on the object to ensure focus

### Composition:
- **Framing**: Include some background space
- **Angle**: Mostly top-down (60-90 degrees from surface)
- **Distance**: Close enough that object fills suggested area

### Lighting:
- **Natural light**: Best option (near window)
- **Avoid shadows**: Use even overhead lighting
- **No glare**: Adjust angle to avoid reflections

### Background:
- **Simple**: Plain desk, table, or neutral surface
- **Contrast**: Choose background color different from object
- **Clean**: Remove clutter from frame

---

## Quick Photo Checklist

Before taking each photo:
- [ ] Object(s) positioned correctly
- [ ] Entire object visible in frame
- [ ] Good lighting, no harsh shadows
- [ ] Clean background
- [ ] Camera focused on object
- [ ] Image is sharp and clear

After taking photos:
- [ ] Named correctly (sample_image_1.jpg, etc.)
- [ ] File format is JPG or PNG
- [ ] Resolution is adequate (640+ pixels)
- [ ] Files are in same folder as .txt annotation files

---

## Adjusting Annotations (Optional)

If your photo composition differs from the suggested layout:

### To measure bounding box coordinates:

1. **Find center point**: 
   - Measure pixel position of object center
   - Divide by image width (for X) and height (for Y)

2. **Calculate dimensions**:
   - Measure object width in pixels / image width = box width
   - Measure object height in pixels / image height = box height

3. **Update .txt file**:
   - Replace values with your measurements
   - Format: `class_id center_x center_y width height`

### Example Calculation:
- Image size: 1920x1080 pixels
- Object center at pixel: 960, 540
- Object size: 480x486 pixels

Normalized coordinates:
- center_x = 960/1920 = 0.5
- center_y = 540/1080 = 0.5
- width = 480/1920 = 0.25
- height = 486/1080 = 0.45

Final annotation: `0 0.5 0.5 0.25 0.45`

---

## Using Online Image Sources

If you don't want to take photos yourself:

### Free Stock Photo Sites:
1. **Pexels** (pexels.com)
   - Search: "smartphone flat lay", "keys keyring", "eyeglasses", "wallet"
   - Download high-resolution
   
2. **Unsplash** (unsplash.com)
   - Similar search terms
   - Free for personal use

3. **Pixabay** (pixabay.com)
   - License-free images

### Requirements when using stock photos:
- Choose images with single objects (or as specified)
- Images should match annotation positions
- May need to adjust annotations to match images
- Crop or edit if necessary

---

## Validation

After creating your images:

1. **Visual Check**: Open each image and corresponding .txt file
2. **Verify**: Object position roughly matches annotation
3. **Test**: Upload to fine-tuning interface
4. **Confirm**: Interface shows correct file count

---

## Alternate: Download Complete Dataset

For a faster start, you can:

1. Search for "YOLO format dataset" + your desired objects
2. Download from platforms like:
   - Roboflow Universe
   - Kaggle Datasets
   - Open Images Dataset
3. Extract and use those images/annotations

Just ensure the class IDs match:
- 0 = smartphone
- 1 = keys  
- 2 = glasses
- 3 = wallet

---

## Need Help?

If you're having trouble:
1. Check FINETUNING-GUIDE.md for more details
2. Use an annotation tool like LabelImg for precise boxes
3. Start with 1-2 images to test the workflow
4. Gradually add more images for better results

Happy annotating! 📸
