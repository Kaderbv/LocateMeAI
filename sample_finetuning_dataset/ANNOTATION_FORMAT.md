# YOLO Annotation Format - Quick Reference

## Format Structure

Each annotation file (`.txt`) contains one line per object:

```
class_id center_x center_y width height
```

## Value Ranges

All values except `class_id` are **normalized** (between 0.0 and 1.0):

| Parameter | Description | Range | Example |
|-----------|-------------|-------|---------|
| class_id | Object class number | Integer (0, 1, 2, ...) | `0` |
| center_x | Horizontal center position | 0.0 - 1.0 | `0.5` |
| center_y | Vertical center position | 0.0 - 1.0 | `0.5` |
| width | Box width | 0.0 - 1.0 | `0.25` |
| height | Box height | 0.0 - 1.0 | `0.45` |

## Coordinate System

```
(0,0) ─────────────────► X (1.0)
  │
  │         Image
  │
  │    (center_x, center_y)
  │           ●
  │      ┌────┴────┐
  │      │ Object  │ ← width, height
  │      └─────────┘
  │
  ▼
  Y
(1.0)
```

## Examples

### Single Object (Centered)
```
0 0.5 0.5 0.3 0.4
```
- Class 0 (smartphone)
- Center: middle of image (50%, 50%)
- Width: 30% of image width
- Height: 40% of image height

### Single Object (Off-center)
```
1 0.7 0.3 0.2 0.25
```
- Class 1 (keys)
- Center: right side (70%), upper area (30%)
- Width: 20% of image width
- Height: 25% of image height

### Multiple Objects
```
0 0.3 0.5 0.25 0.4
2 0.7 0.6 0.35 0.15
```
- Object 1: Smartphone (class 0) on left
- Object 2: Glasses (class 2) on right

## Class IDs (This Dataset)

| ID | Object | Example |
|----|--------|---------|
| 0 | Smartphone | iPhone, Android phone |
| 1 | Keys | House keys, car keys |
| 2 | Glasses | Eyeglasses, sunglasses |
| 3 | Wallet | Leather wallet, purse |

## Common Mistakes

❌ **Wrong**: Values outside 0-1 range
```
0 500 400 300 450  # These are pixel coordinates!
```

✅ **Correct**: Normalized values
```
0 0.5 0.4 0.3 0.45
```

---

❌ **Wrong**: Missing values
```
0 0.5 0.5  # Only 3 values!
```

✅ **Correct**: All 5 values
```
0 0.5 0.5 0.3 0.4
```

---

❌ **Wrong**: Decimal class ID
```
0.5 0.5 0.5 0.3 0.4  # Class ID must be integer!
```

✅ **Correct**: Integer class ID
```
0 0.5 0.5 0.3 0.4
```

## Converting Pixel Coordinates to YOLO Format

If you have pixel coordinates:
- Image width: `img_w`
- Image height: `img_h`
- Bounding box in pixels: `(x1, y1, x2, y2)` (top-left, bottom-right)

**Calculate:**
```python
center_x = ((x1 + x2) / 2) / img_w
center_y = ((y1 + y2) / 2) / img_h
width = (x2 - x1) / img_w
height = (y2 - y1) / img_h
```

**Example:**
- Image: 1920x1080 pixels
- Box: (480, 270, 1440, 810) pixels

```python
center_x = ((480 + 1440) / 2) / 1920 = 0.5
center_y = ((270 + 810) / 2) / 1080 = 0.5
width = (1440 - 480) / 1920 = 0.5
height = (810 - 270) / 1080 = 0.5
```

Result: `0 0.5 0.5 0.5 0.5`

## Validation Checklist

Before using your annotations:
- [ ] Each line has exactly 5 space-separated values
- [ ] Class ID is an integer (0, 1, 2, 3)
- [ ] All other values are between 0.0 and 1.0
- [ ] Filename matches image (e.g., `image1.jpg` → `image1.txt`)
- [ ] Bounding box is within image boundaries
- [ ] No empty lines or extra spaces

## Tools for Creating Annotations

### Desktop:
- **LabelImg**: Free, easy to use, exports to YOLO format
  - https://github.com/heartexlabs/labelImg

### Web-based:
- **Roboflow**: Modern interface, auto-export
  - https://roboflow.com
- **CVAT**: Professional annotation platform
  - https://www.cvat.ai
- **Makesense.ai**: Browser-based, no signup
  - https://www.makesense.ai

## Resources

- [YOLO Official Docs](https://docs.ultralytics.com/)
- [Annotation Best Practices](https://blog.roboflow.com/tips-for-how-to-label-images/)
- [COCO Dataset Format](https://cocodataset.org/)

---

**Pro Tip**: Start with a few images, verify the annotations work, then scale up!
