# ============================================================
# FILE: train_faces.py
# PURPOSE: Collect, augment, train, and evaluate the LBPH
#          face recognizer for authorized personnel.
#
# WORKFLOW:
#   Step 1  →  Capture new face photos via webcam
#   Step 2  →  Augment existing photos (flip, brighten, blur…)
#   Step 3  →  Train LBPH model and save face_model.xml
#   Step 4  →  Evaluate: live confidence readout on webcam
#
# RUN:
#   python train_faces.py          ← interactive menu
#   python train_faces.py --train  ← train only (skip capture)
#   python train_faces.py --eval   ← evaluate only
# ============================================================

import cv2
import numpy as np
import os
import sys
import time
import pickle

# ── CONFIG ───────────────────────────────────────────────────
FACES_DIR   = "authorized_faces"   # Root folder for all persons
MODEL_PATH  = "face_model.xml"     # Output LBPH model
NAMES_PATH  = "name_dict.pkl"      # Maps label int → name str
IMG_SIZE    = (100, 100)           # All face crops resized to this
MIN_IMAGES  = 30                   # Warn if a person has fewer
CAPTURE_N   = 50                   # Photos to capture per session
CONFIDENCE_THRESHOLD = 80          # < 80 = recognized (LBPH metric)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)


# ════════════════════════════════════════════════════════════
# STEP 1 — CAPTURE NEW FACE PHOTOS
# ════════════════════════════════════════════════════════════
def capture_faces():
    """
    Opens webcam and lets user capture CAPTURE_N face photos.
    Saves crops (face-only, grayscale) into authorized_faces/<name>/

    Tips for best model accuracy:
    - Look directly at camera for first 15 shots
    - Slightly tilt left, right, up, down
    - Try with / without glasses
    - Vary distance (close, medium, far)
    - Different lighting if possible
    """
    name = input("\nEnter person name (e.g. HARSH): ").strip().upper()
    if not name:
        print("Name cannot be empty.")
        return

    save_dir = os.path.join(FACES_DIR, name.lower())
    os.makedirs(save_dir, exist_ok=True)

    # Count existing images
    existing = len([f for f in os.listdir(save_dir)
                    if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
    start_idx = existing

    print(f"\n  Saving to      : {save_dir}/")
    print(f"  Existing images: {existing}")
    print(f"  Will capture   : {CAPTURE_N} more")
    print()
    print("  TIPS: Look straight → tilt left → right → up → down")
    print("  SPACE = capture frame    Q = quit early\n")

    cam   = cv2.VideoCapture(0)
    count = 0

    while count < CAPTURE_N:
        ret, frame = cam.read()
        if not ret:
            break

        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))

        # Draw detection box
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # HUD
        cv2.putText(frame, f"Person : {name}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Saved  : {count}/{CAPTURE_N}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        face_status = f"Face detected ({len(faces)})" if len(faces) > 0 else "NO FACE — move closer"
        cv2.putText(frame, face_status, (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 0) if len(faces) > 0 else (0, 0, 255), 2)
        cv2.putText(frame, "SPACE=capture  Q=quit", (10, frame.shape[0] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow(f"Capture — {name}", frame)
        key = cv2.waitKey(1)

        if key == ord(' '):
            if len(faces) == 0:
                print("  No face detected — skipping")
                continue
            # Save the FACE CROP (not full frame) — better training signal
            x, y, w, h = faces[0]
            face_crop  = gray[y:y+h, x:x+w]
            face_crop  = cv2.resize(face_crop, IMG_SIZE)
            filename   = os.path.join(save_dir, f"{name.lower()}_{start_idx + count:03d}.jpg")
            cv2.imwrite(filename, face_crop)
            count += 1
            print(f"  [{count:02d}/{CAPTURE_N}] Saved → {filename}")

        elif key == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
    print(f"\n  Captured {count} photos for {name}")
    print(f"  Total in folder: {existing + count}")
    if existing + count < MIN_IMAGES:
        print(f"  ⚠ Recommended: at least {MIN_IMAGES} photos for good accuracy.")
    print("\n  Run Step 2 (augment) then Step 3 (train) from the menu.\n")


# ════════════════════════════════════════════════════════════
# STEP 2 — DATA AUGMENTATION
# ════════════════════════════════════════════════════════════
def augment_dataset():
    """
    Expands the dataset by generating transformed variants of each
    existing image. This is critical when you have < 30 photos.

    Augmentations applied per original image:
      1. Horizontal flip
      2. Brightness +40
      3. Brightness -40
      4. Slight Gaussian blur (simulates out-of-focus)
      5. Gaussian noise (simulates low-light grain)

    Net effect: 5x dataset size (e.g. 5 images → 30 images)
    """
    if not os.path.exists(FACES_DIR):
        print(f"ERROR: {FACES_DIR}/ folder not found.")
        return

    total_new = 0

    for person in sorted(os.listdir(FACES_DIR)):
        person_dir = os.path.join(FACES_DIR, person)
        if not os.path.isdir(person_dir):
            continue

        originals = [
            f for f in os.listdir(person_dir)
            if f.lower().endswith(('.jpg', '.png', '.jpeg'))
            and "_aug" not in f  # Don't re-augment already-augmented images
        ]

        print(f"  [{person.upper()}]  {len(originals)} originals", end="")
        new_count = 0

        for fname in originals:
            img_path = os.path.join(person_dir, fname)
            img      = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            img = cv2.resize(img, IMG_SIZE)
            stem = os.path.splitext(fname)[0]

            augmentations = {
                "aug_flip":   cv2.flip(img, 1),
                "aug_bright": np.clip(img.astype(np.int16) + 40, 0, 255).astype(np.uint8),
                "aug_dark":   np.clip(img.astype(np.int16) - 40, 0, 255).astype(np.uint8),
                "aug_blur":   cv2.GaussianBlur(img, (5, 5), 0),
                "aug_noise":  _add_noise(img),
            }

            for aug_name, aug_img in augmentations.items():
                out_path = os.path.join(person_dir, f"{stem}_{aug_name}.jpg")
                if not os.path.exists(out_path):   # Don't overwrite existing
                    cv2.imwrite(out_path, aug_img)
                    new_count += 1

        total_new += new_count
        total_after = len([
            f for f in os.listdir(person_dir)
            if f.lower().endswith(('.jpg', '.png', '.jpeg'))
        ])
        print(f"  >>  +{new_count} augmented  =  {total_after} total")

    print(f"\n  Augmentation complete. {total_new} new images created.\n")


def _add_noise(img):
    """Add Gaussian noise to simulate low-light grain."""
    noise  = np.random.normal(0, 15, img.shape).astype(np.int16)
    noisy  = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return noisy


# ════════════════════════════════════════════════════════════
# STEP 3 — TRAIN LBPH MODEL
# ════════════════════════════════════════════════════════════
def train_model():
    """
    Trains the LBPH Face Recognizer on all images in authorized_faces/.

    LBPH (Local Binary Pattern Histograms) algorithm:
    - Divides face into grid cells
    - Computes LBP texture code for each pixel
    - Builds histogram per cell
    - Concatenates all histograms → feature vector
    - Chi-squared distance used at recognition time

    Outputs:
      face_model.xml   ← LBPH model weights
      name_dict.pkl    ← label index → person name mapping
    """
    if not os.path.exists(FACES_DIR):
        print(f"ERROR: {FACES_DIR}/ folder not found.")
        return False

    faces, labels, label_map = [], [], {}
    idx = 0

    print("\n  Loading training images...")
    for person in sorted(os.listdir(FACES_DIR)):
        person_dir = os.path.join(FACES_DIR, person)
        if not os.path.isdir(person_dir):
            continue

        imgs_loaded = 0
        for fname in os.listdir(person_dir):
            if not fname.lower().endswith(('.jpg', '.png', '.jpeg')):
                continue
            img_path = os.path.join(person_dir, fname)
            img      = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            img = cv2.resize(img, IMG_SIZE)
            faces.append(img)
            labels.append(idx)
            imgs_loaded += 1

        if imgs_loaded > 0:
            label_map[idx] = person.upper()
            print(f"    [{idx}] {person.upper():<15} — {imgs_loaded} images")
            idx += 1

    if len(faces) == 0:
        print("\n  ERROR: No training images found.")
        print(f"  Add photos to {FACES_DIR}/<person_name>/ and retry.")
        return False

    print(f"\n  Total images : {len(faces)}")
    print(f"  Persons      : {len(label_map)}")
    print(f"  Training LBPH model...", end=" ", flush=True)

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))
    recognizer.save(MODEL_PATH)

    with open(NAMES_PATH, 'wb') as f:
        pickle.dump(label_map, f)

    print("Done.")
    print(f"  Model saved  : {MODEL_PATH}")
    print(f"  Names saved  : {NAMES_PATH}")
    print(f"  Authorized   : {list(label_map.values())}\n")
    return True


# ════════════════════════════════════════════════════════════
# STEP 4 — EVALUATE: LIVE CONFIDENCE TEST
# ════════════════════════════════════════════════════════════
def evaluate_model():
    """
    Live webcam test. Shows recognition name + confidence for each
    detected face in real time.

    Confidence (LBPH chi-squared distance):
      < 50  = Strong match ✅
      50–80 = Acceptable match ✅
      > 80  = Unknown / rejected ❌

    Press Q to quit.
    """
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: {MODEL_PATH} not found — run Step 3 first.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)

    with open(NAMES_PATH, 'rb') as f:
        label_map = pickle.load(f)

    print(f"\n  Model loaded : {MODEL_PATH}")
    print(f"  Authorized   : {list(label_map.values())}")
    print(f"  Threshold    : < {CONFIDENCE_THRESHOLD} = recognized")
    print("  Press Q to quit\n")

    cam = cv2.VideoCapture(0)
    recognized_count = 0
    unknown_count    = 0
    total_frames     = 0

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        total_frames += 1
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))

        for (x, y, w, h) in faces:
            face_roi = cv2.resize(gray[y:y+h, x:x+w], IMG_SIZE)

            try:
                label, confidence = recognizer.predict(face_roi)
                if confidence < CONFIDENCE_THRESHOLD:
                    name  = label_map.get(label, "UNKNOWN")
                    color = (0, 255, 0)   # Green = authorized
                    tag   = f"{name}  conf:{confidence:.1f}"
                    recognized_count += 1
                else:
                    name  = "UNKNOWN"
                    color = (0, 0, 255)   # Red = intruder
                    tag   = f"UNKNOWN  conf:{confidence:.1f}"
                    unknown_count += 1
            except Exception as e:
                tag, color = "ERROR", (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.rectangle(frame, (x, y-32), (x+w, y), color, cv2.FILLED)
            cv2.putText(frame, tag, (x+4, y-8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        # Stats HUD
        acc = recognized_count / max(recognized_count + unknown_count, 1) * 100
        cv2.putText(frame, f"Frames: {total_frames}   Recognized: {recognized_count}   Unknown: {unknown_count}",
                    (10, frame.shape[0] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

        cv2.imshow("ARGUS — Face Recognition Evaluation", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

    print(f"\n  Evaluation results:")
    print(f"  Frames tested   : {total_frames}")
    print(f"  Recognized      : {recognized_count}")
    print(f"  Unknown         : {unknown_count}")
    print(f"  Recognition rate: {acc:.1f}%\n")


# ════════════════════════════════════════════════════════════
# DATASET STATUS
# ════════════════════════════════════════════════════════════
def dataset_status():
    """Print a summary of the current dataset."""
    print("\n  ── Dataset Status ──────────────────────────────────")
    if not os.path.exists(FACES_DIR):
        print(f"  {FACES_DIR}/ not found.\n")
        return

    total_images = 0
    for person in sorted(os.listdir(FACES_DIR)):
        person_dir = os.path.join(FACES_DIR, person)
        if not os.path.isdir(person_dir):
            continue
        imgs = [f for f in os.listdir(person_dir)
                if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        originals  = [f for f in imgs if "_aug" not in f]
        augmented  = [f for f in imgs if "_aug" in f]
        status     = "✅" if len(imgs) >= MIN_IMAGES else "⚠ needs more"
        total_images += len(imgs)
        print(f"  {person.upper():<15} {len(originals):>3} originals  "
              f"{len(augmented):>3} augmented  "
              f"= {len(imgs):>3} total  {status}")

    model_status = "✅ exists" if os.path.exists(MODEL_PATH) else "❌ not trained yet"
    print(f"\n  Total images    : {total_images}")
    print(f"  Model ({MODEL_PATH}): {model_status}\n")


# ════════════════════════════════════════════════════════════
# MAIN MENU
# ════════════════════════════════════════════════════════════
def main():
    # Handle CLI flags
    if "--train" in sys.argv:
        dataset_status()
        train_model()
        return
    if "--eval" in sys.argv:
        evaluate_model()
        return
    if "--augment" in sys.argv:
        augment_dataset()
        return
    if "--status" in sys.argv:
        dataset_status()
        return

    # Interactive menu
    while True:
        print("\n" + "=" * 55)
        print("  ARGUS SENTINEL — Face Recognition Training Tool")
        print("=" * 55)
        dataset_status()
        print("  1. Capture new face photos (webcam)")
        print("  2. Augment existing photos (5× dataset)")
        print("  3. Train LBPH model")
        print("  4. Evaluate model (live webcam test)")
        print("  5. Full pipeline (augment → train → evaluate)")
        print("  0. Exit")
        print("=" * 55)

        choice = input("  Select option: ").strip()

        if choice == '1':
            capture_faces()
        elif choice == '2':
            augment_dataset()
        elif choice == '3':
            train_model()
        elif choice == '4':
            evaluate_model()
        elif choice == '5':
            print("\n  Running full pipeline...")
            augment_dataset()
            ok = train_model()
            if ok:
                evaluate_model()
        elif choice == '0':
            print("  Exiting.\n")
            break
        else:
            print("  Invalid choice.")


if __name__ == "__main__":
    main()
