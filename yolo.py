# ============================================================
# FILE: yolo.py
# ALGORITHM: Algorithm 2 — YOLOv3 Object Detection
# PURPOSE: Standalone YOLO inference module
# DATASET: COCO (80 classes) — pjreddie.com
# REFERENCE: Redmon & Farhadi (2018), YOLOv3: An Incremental Improvement
# ============================================================

import cv2
import numpy as np
import os
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None


# ── FILE PATHS ───────────────────────────────────────────────
WEIGHTS_PATH  = "yolov3.weights"
CONFIG_PATH   = "yolov3.cfg"
NAMES_PATH    = "coco.names"

# ── GLOBAL MODEL STATE ───────────────────────────────────────
_net           = None
_classes       = []
_output_layers = []
yolo_loaded    = False
_weapon_model  = None
weapon_loaded  = False
WEAPON_WEIGHTS = 'runs/detect/runs/detect/weapons3/weights/best.pt'
WEAPON_CLASSES = {
    0: {'color': (0, 0, 255), 'label': 'WEAPON-AUTO-RIFLE'},
    1: {'color': (0, 0, 255), 'label': 'WEAPON-BAZOOKA'},
    2: {'color': (0, 0, 255), 'label': 'WEAPON-GRENADE'},
    3: {'color': (0, 0, 255), 'label': 'WEAPON-HANDGUN'},
    4: {'color': (0, 0, 200), 'label': 'WEAPON-KNIFE'},
    5: {'color': (0, 0, 255), 'label': 'WEAPON-SMG'},
    6: {'color': (0, 0, 255), 'label': 'WEAPON-SHOTGUN'},
    7: {'color': (0, 0, 255), 'label': 'WEAPON-SNIPER'},
    8: {'color': (0, 0, 200), 'label': 'WEAPON-SWORD'},
}

_frame_counter = 0          # used for frame skipping
_last_result   = ([], []) # cache last detection result
SKIP_FRAMES    = 5          # run YOLO on every frame
BLOB_SIZE      = 320        # reduced from 416 → faster CPU inference

# ── SURVEILLANCE TARGET CLASSES ──────────────────────────────
# Only these COCO classes will be drawn and alerted upon.
# Priority: person (HIGH), vehicles (MED), suspicious items (LOW)
SURVEILLANCE_CLASSES = {
    # ── PEOPLE ───────────────────────────────────────────────
    "person":        {"color": (0,   0,   255), "alert": "HIGH", "label": "PERSON"},

    # ── VEHICLES ─────────────────────────────────────────────
    "car":           {"color": (0,   255,  0),  "alert": "MED",  "label": "CAR"},
    "truck":         {"color": (0,   165, 255), "alert": "MED",  "label": "TRUCK"},
    "bus":           {"color": (255,   0, 255), "alert": "MED",  "label": "BUS"},
    "motorbike":     {"color": (0,   255, 255), "alert": "MED",  "label": "BIKE"},
    "bicycle":       {"color": (255, 255,   0), "alert": "LOW",  "label": "BICYCLE"},
    "aeroplane":     {"color": (0,   200, 255), "alert": "HIGH", "label": "AIRCRAFT"},
    "boat":          {"color": (255, 128,   0), "alert": "MED",  "label": "BOAT"},
    "train":         {"color": (200, 200,   0), "alert": "LOW",  "label": "TRAIN"},

    # ── WEAPONS / DANGEROUS ITEMS (COCO-available) ───────────
    "knife":         {"color": (0,     0, 200), "alert": "HIGH", "label": "WEAPON-KNIFE"},
    "scissors":      {"color": (0,     0, 160), "alert": "HIGH", "label": "WEAPON-SCISSORS"},
    "baseball bat":  {"color": (0,     0, 180), "alert": "HIGH", "label": "WEAPON-BAT"},

    # ── SUSPICIOUS ITEMS / CONTRABAND ────────────────────────
    "backpack":      {"color": (128,   0, 255), "alert": "LOW",  "label": "BACKPACK"},
    "suitcase":      {"color": (128,   0, 255), "alert": "LOW",  "label": "LUGGAGE"},
    "handbag":       {"color": (180,   0, 255), "alert": "LOW",  "label": "BAG"},
    "bottle":        {"color": (100, 100, 255), "alert": "LOW",  "label": "BOTTLE"},
    "cell phone":    {"color": (200, 200,   0), "alert": "LOW",  "label": "PHONE"},
}

CONFIDENCE_THRESHOLD = 0.25   # lowered to 0.25 -> better recall indoors
NMS_THRESHOLD        = 0.45


# ── LOAD YOLO (run once at startup) ──────────────────────────
def load_yolo():
    """
    Loads YOLOv3 weights and config into OpenCV DNN backend.

    Algorithm 2: YOLOv3
    - DNN backend reads the Darknet model format
    - CPU inference used for maximum compatibility
    - Output layers are the three YOLO detection heads

    Returns True if loaded successfully, False otherwise.
    """
    global _net, _classes, _output_layers, yolo_loaded

    missing = [f for f in [WEIGHTS_PATH, CONFIG_PATH, NAMES_PATH] if not os.path.exists(f)]
    if missing:
        print(f"[YOLO] WARNING: Missing files — {missing}")
        print("[YOLO] Object detection disabled. Place yolov3.weights/cfg/coco.names in root.")
        return False

    print("[YOLO] Loading YOLOv3 model (this may take ~10s)...")
    _net = cv2.dnn.readNet(WEIGHTS_PATH, CONFIG_PATH)
    _net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    _net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    with open(NAMES_PATH, "r") as f:
        _classes = [line.strip() for line in f.readlines()]

    layer_names    = _net.getLayerNames()
    _output_layers = [layer_names[i - 1] for i in _net.getUnconnectedOutLayers()]

    yolo_loaded = True
    print(f"[YOLO] Model loaded — {len(_classes)} classes, {len(_output_layers)} output layers.")
    
    global _weapon_model, weapon_loaded
    if YOLO is not None and os.path.exists(WEAPON_WEIGHTS):
        print(f"[YOLO] Loading Weapon Model YOLOv8...")
        _weapon_model = YOLO(WEAPON_WEIGHTS)
        weapon_loaded = True
        print(f"[YOLO] Weapon Model loaded!")
    else:
        print(f"[YOLO] YOLOv8 Weapon model not found or ultralytics not installed.")
        
    return True


# ── ALGORITHM 2: YOLO INFERENCE ──────────────────────────────
def detect_objects(frame):
    """
    Runs YOLOv3 inference on a single frame.

    Algorithm: YOLOv3 with Non-Maximum Suppression
    Steps:
    1. Create 416x416 blob from frame (normalise + BGR→RGB)
    2. Forward pass through all 3 YOLO detection heads
    3. Filter by confidence threshold
    4. Apply NMS to remove overlapping boxes
    5. Draw bounding boxes for surveillance classes only

    Args:
        frame: BGR numpy array (camera frame)

    Returns:
        annotated_frame : frame with bounding boxes drawn
        detected_labels : list of class name strings that were found
                          e.g. ['person', 'car']
    """
    global _frame_counter, _last_result

    if not yolo_loaded or _net is None:
        return frame, []

    # ── FRAME SKIP: only run YOLO every (SKIP_FRAMES+1) frames ──
    _frame_counter += 1
    if _frame_counter % (SKIP_FRAMES + 1) != 0:
        boxes_to_draw, last_labels = _last_result
        for (x, y, bw, bh, color, tag) in boxes_to_draw:
            cv2.rectangle(frame, (x, y), (x + bw, y + bh), color, 2)
            (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
            cv2.rectangle(frame, (x, y - th - 10), (x + tw + 6, y), color, cv2.FILLED)
            cv2.putText(frame, tag, (x + 3, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        return frame, last_labels
        
    boxes_to_draw = []


    h, w = frame.shape[:2]

    # ── STEP 1: BLOB CREATION ────────────────────────────────
    blob = cv2.dnn.blobFromImage(
        frame, 1 / 255.0, (BLOB_SIZE, BLOB_SIZE), swapRB=True, crop=False
    )
    _net.setInput(blob)

    # ── STEP 2: FORWARD PASS ─────────────────────────────────
    outs = _net.forward(_output_layers)

    # ── STEP 3: PARSE DETECTIONS ─────────────────────────────
    boxes, confidences, class_ids = [], [], []
    for out in outs:
        for detection in out:
            scores     = detection[5:]
            class_id   = int(np.argmax(scores))
            confidence = float(scores[class_id])
            if confidence < CONFIDENCE_THRESHOLD:
                continue

            class_name = _classes[class_id] if class_id < len(_classes) else ""
            if class_name not in SURVEILLANCE_CLASSES:
                continue

            cx, cy, bw, bh = (
                int(detection[0] * w),
                int(detection[1] * h),
                int(detection[2] * w),
                int(detection[3] * h),
            )
            x = cx - bw // 2
            y = cy - bh // 2
            boxes.append([x, y, bw, bh])
            confidences.append(confidence)
            class_ids.append(class_id)

    # ── STEP 4: NON-MAXIMUM SUPPRESSION ──────────────────────
    indices = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)

    detected_labels = []
    if len(indices) == 0:
        return frame, []

    # OpenCV 4.x returns indices as a flat array or nested — handle both
    flat_indices = indices.flatten() if hasattr(indices, 'flatten') else indices

    for i in flat_indices:
        x, y, bw, bh = [int(v) for v in boxes[i]]   # cast to plain int (fixes numpy int64 error)
        conf          = confidences[i]
        class_name    = _classes[class_ids[i]]
        info          = SURVEILLANCE_CLASSES.get(class_name, {})
        color         = info.get("color", (0, 255, 0))
        label_text    = info.get("label", class_name.upper())

        detected_labels.append(class_name)

        tag = f"{label_text} {conf:.0%}"
        boxes_to_draw.append((x, y, bw, bh, color, tag))
        
        cv2.rectangle(frame, (x, y), (x + bw, y + bh), color, 2)
        (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        cv2.rectangle(frame, (x, y - th - 10), (x + tw + 6, y), color, cv2.FILLED)
        cv2.putText(frame, tag, (x + 3, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)


    # ── YOLOv8 WEAPON DETECTION ─────────────────────────────
    if weapon_loaded and _weapon_model is not None:
        results = _weapon_model(frame, verbose=False)
        for r in results:
            for box in r.boxes:
                if box.conf[0].item() < CONFIDENCE_THRESHOLD:
                    continue
                cls_id = int(box.cls[0].item())
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
                conf = box.conf[0].item()
                
                info = WEAPON_CLASSES.get(cls_id, {'color': (0,0,255), 'label': f'WEAPON-{cls_id}'})
                label_text = info['label']
                color = info['color']
                detected_labels.append("weapon")
                
                bw, bh = x2 - x1, y2 - y1
                tag = f"{label_text} {conf:.0%}"
                boxes_to_draw.append((x1, y1, bw, bh, color, tag))
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
                cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 6, y1), color, cv2.FILLED)
                cv2.putText(frame, tag, (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
                
    _last_result = (boxes_to_draw, detected_labels)
    return frame, detected_labels



# ── INIT ON IMPORT ────────────────────────────────────────────
load_yolo()
