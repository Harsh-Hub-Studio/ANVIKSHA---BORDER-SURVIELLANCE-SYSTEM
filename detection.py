# ============================================================
# FILE: detection.py
# ALGORITHMS:
#   - Algorithm 1: Viola-Jones Haar Cascade (Face Detection)
#   - Algorithm 3: HSV Color Segmentation (ID Card Detection)
# PURPOSE: All detection logic for faces and ID cards
# DATASET:
#   - Haar Cascade: Pre-trained on MIT+CMU face dataset
#   - HSV: Calibrated on local ID card photos
# ============================================================

import cv2
import numpy as np
import os


# ── ALGORITHM 1: VIOLA-JONES HAAR CASCADE ────────────────────
# Load pre-trained model (trained on MIT+CMU face dataset)
# No custom training needed — OpenCV ships with this model
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# ── FACE RECOGNITION SETUP ───────────────────────────────────
# Load authorized faces from authorized_faces/ folder
# Dataset: Photos of authorized personnel collected manually
recognizer   = cv2.face.LBPHFaceRecognizer_create()
label_map    = {}   # Maps label number → person name
model_loaded = False

AUTHORIZED_FACES_DIR = "authorized_faces"
FACE_MODEL_PATH      = "face_model.xml"


def train_face_recognizer():
    """
    Trains face recognizer on photos in authorized_faces/ folder.

    Dataset needed:
    authorized_faces/
    ├── harsh/
    │   ├── harsh_001.jpg
    │   └── harsh_002.jpg
    └── admin/
        └── admin_001.jpg

    Run this once to generate face_model.xml
    """
    global model_loaded, label_map

    faces  = []
    labels = []
    idx    = 0

    if not os.path.exists(AUTHORIZED_FACES_DIR):
        print(f"WARNING: '{AUTHORIZED_FACES_DIR}' folder not found.")
        return False

    for person_name in os.listdir(AUTHORIZED_FACES_DIR):
        person_path = os.path.join(AUTHORIZED_FACES_DIR, person_name)

        # Handle both flat (harsh.jpg) and folder (harsh/harsh_001.jpg) structures
        if os.path.isfile(person_path) and person_path.endswith(('.jpg','.png','.jpeg')):
            img = cv2.imread(person_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                img = cv2.resize(img, (100, 100))
                faces.append(img)
                labels.append(idx)
                label_map[idx] = os.path.splitext(person_name)[0].upper()
                idx += 1

        elif os.path.isdir(person_path):
            label_map[idx] = person_name.upper()
            for img_file in os.listdir(person_path):
                if img_file.endswith(('.jpg','.png','.jpeg')):
                    img_path = os.path.join(person_path, img_file)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        img = cv2.resize(img, (100, 100))
                        faces.append(img)
                        labels.append(idx)
            idx += 1

    if len(faces) == 0:
        print("WARNING: No face images found in authorized_faces/")
        return False

    recognizer.train(faces, np.array(labels))
    recognizer.save(FACE_MODEL_PATH)
    model_loaded = True
    print(f"Face model trained — {len(faces)} images, {len(label_map)} persons")
    print(f"Authorized: {list(label_map.values())}")
    return True


def load_face_model():
    """Load pre-trained face model if it exists."""
    global model_loaded
    if os.path.exists(FACE_MODEL_PATH):
        recognizer.read(FACE_MODEL_PATH)
        model_loaded = True
        print("Face model loaded from face_model.xml")
        return True
    return False


# Auto-load model on import
if not load_face_model():
    train_face_recognizer()


# ── ALGORITHM 1: FACE DETECTION FUNCTION ─────────────────────
def detect_faces(frame):
    """
    Detects faces using Viola-Jones Haar Cascade algorithm.

    Steps:
    1. Convert frame to grayscale (Haar works on grayscale)
    2. Apply detectMultiScale (sliding window scan)
    3. For each face found — recognize if authorized or intruder
    4. Draw colored bounding box:
       GREEN = AUTHORIZED person
       RED   = UNKNOWN INTRUDER

    Returns: (annotated_frame, face_count, intruder_detected)
    """
    gray         = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_count   = 0
    is_intruder  = False

    # ── VIOLA-JONES DETECTION ─────────────────────────────────
    # scaleFactor=1.1  → how much image is reduced at each scale
    # minNeighbors=4   → how many neighbors each candidate needs
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(50,50))
    face_count = len(faces)

    for (x, y, w, h) in faces:
        face_roi = gray[y:y+h, x:x+w]
        face_roi = cv2.resize(face_roi, (100, 100))

        name  = "UNKNOWN INTRUDER"
        color = (0, 0, 255)  # Red = intruder
        is_intruder = True

        # ── FACE RECOGNITION ─────────────────────────────────
        if model_loaded and label_map:
            try:
                label, confidence = recognizer.predict(face_roi)
                # Lower confidence = better match (LBPH)
                if confidence < 80:
                    name        = label_map.get(label, "UNKNOWN")
                    color       = (0, 255, 0)  # Green = authorized
                    is_intruder = False
            except Exception:
                pass

        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

        # Draw label background
        cv2.rectangle(frame, (x, y-35), (x+w, y), color, cv2.FILLED)
        cv2.putText(frame, name, (x+4, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

        # Draw scanning animation text
        cv2.putText(frame, "SCANNING...", (x, y+h+20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    return frame, face_count, is_intruder


# ── ALGORITHM 3: HSV COLOR SEGMENTATION ──────────────────────
def detect_id_card(frame):
    """
    Detects blue military ID card using HSV color segmentation.

    Dataset needed: Photos of your ID card in different lighting
    Run calibrate_hsv() first to find the right values for YOUR card.

    Steps:
    1. Convert BGR frame to HSV color space
    2. Apply color range mask to isolate blue pixels
    3. Count blue pixels
    4. If > threshold → AUTHORIZED ID card detected

    Returns: (is_authorized, blue_pixel_count, annotated_frame)
    """
    # ── BGR to HSV CONVERSION ─────────────────────────────────
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # ── HSV BLUE RANGE ────────────────────────────────────────
    # Calibrated for standard blue ID/access cards
    # Run calibrate_hsv() to find values for your specific card
    lower_blue = np.array([90,  50,  50 ])
    upper_blue = np.array([130, 255, 255])

    # ── CREATE BLUE MASK ──────────────────────────────────────
    mask        = cv2.inRange(hsv, lower_blue, upper_blue)
    blue_pixels = cv2.countNonZero(mask)

    # ── THRESHOLD DECISION ────────────────────────────────────
    PIXEL_THRESHOLD = 5000
    is_authorized   = blue_pixels > PIXEL_THRESHOLD

    # Visualize detected blue region
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Draw authorization status on frame
    status = "ID DETECTED — AUTHORIZED" if is_authorized else "NO ID — CHECK REQUIRED"
    color  = (0, 255, 0) if is_authorized else (0, 165, 255)
    cv2.putText(frame, status, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    cv2.putText(frame, f"Blue px: {blue_pixels}", (10, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    return is_authorized, blue_pixels, frame


# ── HSV CALIBRATION HELPER ────────────────────────────────────
def calibrate_hsv(image_path):
    """
    Helper to find correct HSV range for YOUR specific ID card.

    Usage:
        calibrate_hsv('your_id_card.jpg')

    Take photos of your ID card in:
    - Bright light
    - Dim light
    - Different angles
    Then run this on each photo to find the HSV range.
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not load image: {image_path}")
        return

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, w = img.shape[:2]

    # Sample multiple points across center region
    points = [
        hsv[h//2,     w//2    ],   # Center
        hsv[h//3,     w//2    ],   # Upper center
        hsv[2*h//3,   w//2    ],   # Lower center
        hsv[h//2,     w//3    ],   # Left center
        hsv[h//2,     2*w//3  ],   # Right center
    ]

    h_vals = [p[0] for p in points]
    s_vals = [p[1] for p in points]
    v_vals = [p[2] for p in points]

    print(f"\n── HSV Calibration for: {image_path} ──")
    print(f"H range: {min(h_vals)} → {max(h_vals)}")
    print(f"S range: {min(s_vals)} → {max(s_vals)}")
    print(f"V range: {min(v_vals)} → {max(v_vals)}")
    print(f"\nSuggested range (with ±15 buffer):")
    print(f"lower_blue = np.array([{max(0,  min(h_vals)-15)}, {max(0,  min(s_vals)-30)}, 50])")
    print(f"upper_blue = np.array([{min(179, max(h_vals)+15)}, 255, 255])")


# ── COMBINED DETECTION (Face + ID) ───────────────────────────
def full_detection(frame):
    """
    Runs both face detection and ID card detection on a frame.
    Used for CAM 01 (laptop webcam).

    Returns annotated frame with both detections shown.
    """
    # Run ID card detection first
    is_authorized, blue_pixels, frame = detect_id_card(frame)

    # Run face detection
    frame, face_count, is_intruder = detect_faces(frame)

    # Override face box color based on ID card presence
    if face_count > 0 and is_authorized:
        cv2.putText(frame, "MILITARY ID VERIFIED", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    elif face_count > 0 and is_intruder:
        cv2.putText(frame, "ALERT: UNKNOWN INTRUDER", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

    return frame, face_count, is_intruder, is_authorized
