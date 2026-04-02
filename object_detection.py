# ============================================================
# FILE: object_detection.py
# ALGORITHM: Algorithm 2 — YOLOv3 Object Detection
# PURPOSE: Vehicle and person detection on phone camera
# DATASET: Pre-trained on Microsoft COCO (330K images, 80 classes)
# FILES NEEDED:
#   - yolov3.weights → https://pjreddie.com/media/files/yolov3.weights
#   - yolov3.cfg    → https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg
#   - coco.names    → https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names
# ============================================================

import cv2
import numpy as np
import os
import time


# ── YOLO FILES CHECK ──────────────────────────────────────────
WEIGHTS_PATH = "yolov3.weights"
CONFIG_PATH  = "yolov3.cfg"
NAMES_PATH   = "coco.names"

yolo_loaded  = False
net          = None
classes      = []
output_layers = []


# ── SURVEILLANCE RELEVANT CLASSES ─────────────────────────────
# From COCO 80 classes — only these matter for surveillance
SURVEILLANCE_CLASSES = {
    "person":    {"color": (0, 0, 255),   "alert": "HIGH",   "label": "PERSON DETECTED"},
    "car":       {"color": (0, 255, 0),   "alert": "MED",    "label": "VEHICLE: CAR"},
    "truck":     {"color": (0, 165, 255), "alert": "MED",    "label": "VEHICLE: TRUCK"},
    "bus":       {"color": (255, 0, 255), "alert": "MED",    "label": "VEHICLE: BUS"},
    "motorbike": {"color": (0, 255, 255), "alert": "MED",    "label": "VEHICLE: BIKE"},
    "bicycle":   {"color": (255, 255, 0), "alert": "LOW",    "label": "VEHICLE: BICYCLE"},
    "backpack":  {"color": (128, 0, 255), "alert": "LOW",    "label": "SUSPICIOUS BAG"},
    "suitcase":  {"color": (128, 0, 255), "alert": "LOW",    "label": "SUSPICIOUS LUGGAGE"},
}


def load_yolo():
    """
    Loads YOLOv3 pre-trained weights.

    Algorithm: YOLOv3 (You Only Look Once v3)
    Dataset:   Microsoft COCO — 330,000 images, 80 object classes
    Training:  Done by Joseph Redmon — we use pre-trained weights directly

    Download required files:
    wget https://pjreddie.com/media/files/yolov3.weights
    wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg
    wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names
    """
    global yolo_loaded, net, classes, output_layers

    # Check if files exist
    missing = []
    for f in [WEIGHTS_PATH, CONFIG_PATH, NAMES_PATH]:
        if not os.path.exists(f):
            missing.append(f)

    if missing:
        print(f"WARNING: YOLO files missing: {missing}")
        print("Download from:")
        print("  https://pjreddie.com/media/files/yolov3.weights")
        print("  https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg")
        print("  https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names")
        return False

    # Load YOLO neural network
    print("Loading YOLO model (this takes ~10 seconds)...")
    net = cv2.dnn.readNet(WEIGHTS_PATH, CONFIG_PATH)

    # Use CPU — change to GPU if available
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    # Load class names
    with open(NAMES_PATH, "r") as f:
        classes = [line.strip() for line in f.readlines()]

    # Get output layer names
    layer_names   = net.getLayerNames()
    output_layers = [layer_names[i-1] for i in net.getUnconnectedOutLayers()]

    yolo_loaded = True
    print(f"YOLO loaded — {len(classes)} classes ready")
    return True


# Auto-load on import
load_yolo()


# ── ALGORITHM 2: YOLO OBJECT DETECTION ───────────────────────
def detect_objects(frame, confidence_threshold=0.5, nms_threshold=0.4):
    """
    Detects vehicles and people using YOLOv3.

    Algorithm steps:
    1. Resize frame to 416x416 (YOLO input size)
    2. Create blob (normalize pixel values 0-1)
    3. Forward pass through neural network (single pass — YOLO's key advantage)
    4. Parse output — extract boxes, confidences, class IDs
    5. Apply Non-Maximum Suppression (remove duplicate boxes)
    6. Draw boxes with class labels

    Returns: (annotated_frame, detections_list)
    detections_list = [{'class': 'car', 'confidence': 0.92, 'box': [x,y,w,h]}, ...]
    """
    if not yolo_loaded:
        return frame, []

    height, width = frame.shape[:2]
    detections    = []

    # ── STEP 1: PREPARE INPUT ─────────────────────────────────
    # blobFromImage: resize, normalize, swap BGR→RGB
    blob = cv2.dnn.blobFromImage(
        frame, 1/255.0, (416, 416),
        swapRB=True, crop=False
    )
    net.setInput(blob)

    # ── STEP 2: FORWARD PASS (Single Neural Network Pass) ─────
    start   = time.time()
    outputs = net.forward(output_layers)
    elapsed = time.time() - start

    boxes, confidences, class_ids = [], [], []

    # ── STEP 3: PARSE YOLO OUTPUT ─────────────────────────────
    for output in outputs:
        for detection in output:
            scores    = detection[5:]
            class_id  = np.argmax(scores)
            confidence = scores[class_id]

            # Only keep high confidence detections of surveillance classes
            if confidence > confidence_threshold:
                class_name = classes[class_id] if class_id < len(classes) else "unknown"

                if class_name in SURVEILLANCE_CLASSES:
                    # Convert normalized coordinates to pixel coordinates
                    cx = int(detection[0] * width)
                    cy = int(detection[1] * height)
                    w  = int(detection[2] * width)
                    h  = int(detection[3] * height)
                    x  = cx - w // 2
                    y  = cy - h // 2

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

    # ── STEP 4: NON-MAXIMUM SUPPRESSION ───────────────────────
    # Removes duplicate overlapping boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, nms_threshold)

    # ── STEP 5: DRAW RESULTS ──────────────────────────────────
    if len(indices) > 0:
        for i in indices.flatten():
            x, y, w, h    = boxes[i]
            class_name     = classes[class_ids[i]]
            confidence_pct = confidences[i]
            info           = SURVEILLANCE_CLASSES.get(class_name, {"color":(255,255,255), "alert":"LOW", "label":class_name.upper()})
            color          = info["color"]
            label          = f"{info['label']} {confidence_pct:.0%}"

            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

            # Draw label background
            cv2.rectangle(frame, (x, y-28), (x+w, y), color, cv2.FILLED)
            cv2.putText(frame, label, (x+4, y-8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,255), 2)

            detections.append({
                'class':      class_name,
                'confidence': confidence_pct,
                'alert':      info["alert"],
                'box':        [x, y, w, h]
            })

    # Show FPS and count on frame
    fps = f"YOLO FPS: {1/elapsed:.1f}" if elapsed > 0 else "YOLO"
    cv2.putText(frame, fps, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
    cv2.putText(frame, f"Objects: {len(indices) if len(indices)>0 else 0}", (10, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

    return frame, detections


# ── QUICK TEST ────────────────────────────────────────────────
def test_on_image(image_path):
    """
    Test YOLO on a single image.
    Usage: python -c "from object_detection import test_on_image; test_on_image('test.jpg')"
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not load: {image_path}")
        return

    result, detections = detect_objects(img)

    print(f"\nDetections in {image_path}:")
    for d in detections:
        print(f"  {d['class'].upper():<12} confidence={d['confidence']:.0%}  alert={d['alert']}")

    if not detections:
        print("  No surveillance-relevant objects detected")

    cv2.imwrite("yolo_result.jpg", result)
    print("Result saved as yolo_result.jpg")
