# ============================================================
# FILE: rename_dataset.py
# PURPOSE: Rename messy image files (img_001, photo_x, etc.)
#          into the clean format the face recognizer needs.
#
# RUN: python rename_dataset.py
# ============================================================

import os

# ── CONFIGURE THESE TWO LINES ─────────────────────────────────
PERSON_NAME  = "harsh"           # ← change to the person's name
IMAGES_FOLDER = r"authorized_faces\harsh"  # ← path to the folder with images
# ──────────────────────────────────────────────────────────────

VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')


def rename_images():
    if not os.path.exists(IMAGES_FOLDER):
        print(f"❌ ERROR: Folder not found: {IMAGES_FOLDER}")
        print("   Please check the IMAGES_FOLDER path above.")
        return

    # Collect all image files (sorted for consistency)
    all_files = sorted([
        f for f in os.listdir(IMAGES_FOLDER)
        if f.lower().endswith(VALID_EXTENSIONS)
    ])

    if not all_files:
        print(f"❌ No image files found in: {IMAGES_FOLDER}")
        return

    name = PERSON_NAME.lower().strip()
    print(f"\n{'='*50}")
    print(f"  Renaming {len(all_files)} images for: {name.upper()}")
    print(f"  Folder: {IMAGES_FOLDER}")
    print(f"{'='*50}\n")

    # First pass: rename to temp names to avoid conflicts
    # (e.g., if harsh_001.jpg already exists)
    temp_files = []
    for i, filename in enumerate(all_files):
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.jpeg':
            ext = '.jpg'
        src  = os.path.join(IMAGES_FOLDER, filename)
        tmp  = os.path.join(IMAGES_FOLDER, f"__tmp_{i:04d}{ext}")
        os.rename(src, tmp)
        temp_files.append(tmp)

    # Second pass: rename temp files to final names
    for i, tmp_path in enumerate(temp_files):
        ext      = os.path.splitext(tmp_path)[1]
        new_name = f"{name}_{i+1:03d}{ext}"
        dst      = os.path.join(IMAGES_FOLDER, new_name)
        os.rename(tmp_path, dst)
        print(f"  [{i+1:03d}] → {new_name}")

    print(f"\n✅ Done! {len(temp_files)} images renamed.")
    print(f"   Now run: python train_faces.py --train\n")


if __name__ == "__main__":
    rename_images()
