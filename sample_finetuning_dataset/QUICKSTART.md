# Quick Start Guide - Sample Fine-tuning Dataset

## 🚀 Fastest Way to Test Fine-tuning

### What You Need
1. **5 Images** of these objects:
   - Smartphone
   - Keys
   - Glasses  
   - Wallet (or multiple objects)

2. **This Directory** (already has annotations!)

### Steps

#### 1️⃣ Add Your Images (5 minutes)

Take or download 5 photos and name them:
```
sample_image_1.jpg  → Single smartphone
sample_image_2.jpg  → Keys on keyring
sample_image_3.jpg  → Glasses
sample_image_4.jpg  → Smartphone + Keys
sample_image_5.jpg  → Wallet
```

**Place them in this directory** alongside the `.txt` files.

#### 2️⃣ Validate (Optional)

Run the validator:
```bash
python validate_annotations.py
```

Should show: ✅ All valid!

#### 3️⃣ Upload for Training

1. Open LocateMeAI
2. Go to **"🎯 Fine-tune Model"** tab
3. Click **"Upload images and annotation files"**
4. Select all 10 files (5 images + 5 txt files)
5. Set parameters:
   - Epochs: 10
   - Batch Size: 16
   - Image Size: 640
   - Model Name: `my_first_model`
6. Click **"🚀 Start Training"**

#### 4️⃣ Activate Your Model

After training completes:
1. Scroll to **"Model Management"** section
2. Select `my_first_model` from dropdown
3. Click **"✅ Set as Active"**

#### 5️⃣ Test Detection

1. Go to **"📷 Locate By Image"** tab
2. Upload an image with your objects
3. Say: **"detect smartphone"** or **"find keys"**
4. See your custom model in action! 🎉

---

## 📁 What's in This Directory

| File | Purpose |
|------|---------|
| `README.md` | Complete guide to the dataset |
| `INSTRUCTIONS.md` | How to take/create matching images |
| `ANNOTATION_FORMAT.md` | YOLO format reference |
| `validate_annotations.py` | Check your annotations |
| `sample_image_1.txt` | Annotation for smartphone |
| `sample_image_2.txt` | Annotation for keys |
| `sample_image_3.txt` | Annotation for glasses |
| `sample_image_4.txt` | Annotation for multiple objects |
| `sample_image_5.txt` | Annotation for wallet |

---

## 💡 Tips

### Taking Photos
- **Lighting**: Good natural light or overhead lights
- **Background**: Simple, clean surface (desk, table)
- **Angle**: Top-down (60-90 degrees)
- **Distance**: Object fills suggested area (see INSTRUCTIONS.md)

### Common Issues
❌ **"No images found"** → Check filenames match exactly  
❌ **"Training fails"** → Run validator to check annotations  
❌ **"Poor results"** → Need more images (aim for 50+ per class)  

### Quick Photo Sources
- Your own phone camera (best!)
- [Pexels](https://pexels.com) - free stock photos
- [Unsplash](https://unsplash.com) - high quality free images

---

## 🎯 Expected Results

With just 5 images:
- ✅ Training will complete in 2-5 minutes
- ✅ Model will learn basic object shapes
- ⚠️  Detection may not be super accurate (need more data!)
- ✅ Perfect for testing the workflow

To improve:
- Add 20-50 more images per object
- Include different angles
- Vary lighting conditions
- Include different backgrounds

---

## 🆘 Troubleshooting

### Problem: Can't take photos right now
**Solution**: Download stock images from Pexels/Unsplash

### Problem: Annotations don't match my images
**Solution**: 
1. Use [LabelImg](https://github.com/heartexlabs/labelImg) to re-annotate
2. Or adjust coordinates in `.txt` files manually

### Problem: Want different objects
**Solution**:
1. Keep the filenames
2. Change images to your objects
3. Update class definitions in `.txt` files
4. Use same class IDs (0, 1, 2, 3)

---

## 📚 Next Steps

After testing with this sample:

1. **Read**: [FINETUNING-GUIDE.md](../FINETUNING-GUIDE.md) for complete details
2. **Create**: Your own larger dataset (100+ images recommended)
3. **Use tools**: LabelImg or Roboflow for precise annotations
4. **Experiment**: Try different objects, more epochs, different parameters

---

## ✅ Checklist

Before uploading:
- [ ] 5 images named correctly
- [ ] 5 .txt files present
- [ ] Ran validation script (optional)
- [ ] All files in same directory
- [ ] Ready to start training!

---

**Time to complete**: ~15 minutes (including photo taking)  
**Difficulty**: Beginner-friendly  
**Result**: Working custom YOLO model!

Happy fine-tuning! 🎯✨
