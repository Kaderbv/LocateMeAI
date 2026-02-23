"""
Annotation Validator for YOLO Format

This script validates YOLO format annotation files to ensure they are correctly formatted
before uploading for fine-tuning.

Usage:
    python validate_annotations.py

The script will check all .txt files in the current directory and report any issues.
"""

import os
import glob

def validate_yolo_annotation(file_path):
    """
    Validate a single YOLO annotation file.
    
    Args:
        file_path: Path to the annotation file (.txt)
        
    Returns:
        tuple: (is_valid, errors, warnings)
    """
    errors = []
    warnings = []
    
    # Check if file exists
    if not os.path.exists(file_path):
        errors.append(f"File does not exist: {file_path}")
        return False, errors, warnings
    
    # Read file
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        errors.append(f"Cannot read file: {str(e)}")
        return False, errors, warnings
    
    # Check if file is empty
    if not lines:
        warnings.append("File is empty (no annotations)")
        return True, errors, warnings
    
    # Validate each line
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Skip comment lines
        if line.startswith('#'):
            continue
        
        # Split values
        parts = line.split()
        
        # Check number of values
        if len(parts) != 5:
            errors.append(f"Line {line_num}: Expected 5 values, found {len(parts)}")
            continue
        
        try:
            class_id, center_x, center_y, width, height = parts
            
            # Validate class_id (should be integer)
            try:
                class_id_int = int(class_id)
                if class_id_int < 0:
                    errors.append(f"Line {line_num}: class_id must be non-negative")
            except ValueError:
                errors.append(f"Line {line_num}: class_id must be an integer")
            
            # Validate normalized coordinates
            for param_name, param_value in [
                ("center_x", center_x),
                ("center_y", center_y),
                ("width", width),
                ("height", height)
            ]:
                try:
                    val = float(param_value)
                    if val < 0.0 or val > 1.0:
                        errors.append(
                            f"Line {line_num}: {param_name} must be between 0.0 and 1.0 " 
                            f"(found {val})"
                        )
                except ValueError:
                    errors.append(f"Line {line_num}: {param_name} must be a number")
            
        except Exception as e:
            errors.append(f"Line {line_num}: Unexpected error: {str(e)}")
    
    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def check_image_annotation_pairs(directory="."):
    """
    Check that each annotation file has a corresponding image file.
    
    Args:
        directory: Directory to check (default: current directory)
        
    Returns:
        tuple: (pairs, missing_images, orphan_annotations)
    """
    # Find all annotation files
    txt_files = glob.glob(os.path.join(directory, "*.txt"))
    
    # Image extensions
    image_extensions = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]
    
    pairs = []
    missing_images = []
    
    for txt_file in txt_files:
        base_name = os.path.splitext(txt_file)[0]
        
        # Look for corresponding image
        image_found = False
        for ext in image_extensions:
            image_file = base_name + ext
            if os.path.exists(image_file):
                pairs.append((image_file, txt_file))
                image_found = True
                break
        
        if not image_found:
            missing_images.append(txt_file)
    
    # Find orphan images (images without annotations)
    all_images = []
    for ext in image_extensions:
        all_images.extend(glob.glob(os.path.join(directory, f"*{ext}")))
    
    orphan_images = []
    for image_file in all_images:
        base_name = os.path.splitext(image_file)[0]
        txt_file = base_name + ".txt"
        if not os.path.exists(txt_file):
            orphan_images.append(image_file)
    
    return pairs, missing_images, orphan_images


def print_validation_results(file_path, is_valid, errors, warnings):
    """Print validation results for a file."""
    file_name = os.path.basename(file_path)
    
    if is_valid and not warnings:
        print(f"✅ {file_name}: Valid")
    elif is_valid and warnings:
        print(f"⚠️  {file_name}: Valid (with warnings)")
        for warning in warnings:
            print(f"   Warning: {warning}")
    else:
        print(f"❌ {file_name}: Invalid")
        for error in errors:
            print(f"   Error: {error}")
        for warning in warnings:
            print(f"   Warning: {warning}")


def main():
    """Main validation function."""
    print("=" * 60)
    print("YOLO Annotation Validator")
    print("=" * 60)
    print()
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"Checking directory: {current_dir}")
    print()
    
    # Find annotation files
    txt_files = glob.glob("*.txt")
    
    # Filter out script files and readme files
    txt_files = [f for f in txt_files if not f.lower().startswith(('readme', 'instructions'))]
    
    if not txt_files:
        print("No annotation files (.txt) found in current directory.")
        return
    
    print(f"Found {len(txt_files)} annotation file(s)")
    print()
    
    # Validate each file
    valid_count = 0
    invalid_count = 0
    
    for txt_file in txt_files:
        is_valid, errors, warnings = validate_yolo_annotation(txt_file)
        print_validation_results(txt_file, is_valid, errors, warnings)
        
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
    
    print()
    print("-" * 60)
    
    # Check image-annotation pairs
    print("\nChecking image-annotation pairs...")
    pairs, missing_images, orphan_images = check_image_annotation_pairs()
    
    print(f"✅ Complete pairs: {len(pairs)}")
    
    if missing_images:
        print(f"⚠️  Annotations without images: {len(missing_images)}")
        for txt_file in missing_images:
            print(f"   - {os.path.basename(txt_file)}")
    
    if orphan_images:
        print(f"⚠️  Images without annotations: {len(orphan_images)}")
        for img_file in orphan_images:
            print(f"   - {os.path.basename(img_file)}")
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Valid annotations: {valid_count}")
    print(f"Invalid annotations: {invalid_count}")
    print(f"Complete pairs (image + annotation): {len(pairs)}")
    print()
    
    if invalid_count == 0 and len(pairs) > 0:
        print("✅ All annotations are valid! Ready for fine-tuning.")
    elif invalid_count > 0:
        print("❌ Fix the errors above before fine-tuning.")
    elif len(pairs) == 0:
        print("⚠️  No image-annotation pairs found. Add images to match your annotations.")
    
    print()


if __name__ == "__main__":
    main()
