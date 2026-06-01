# ============================================================
# FILE: main.py
# PURPOSE: Anviksha— Flask server entry point
#
# MODULES INTEGRATED:
#   camera.py    → MJPEG streaming + auto-reconnect (Alg 5, 7)
#   detection.py → Haar Cascade face detection (Alg 1)
#   yolo.py      → YOLOv3 object detection (Alg 2)
#   risk.py      → Weighted MCDA risk scoring (Alg 4)
#   alerts.py    → Socket.IO event-driven alerts (Alg 6)
#
# ALERT LOGIC:
#   Person detected (YOLO or face) + Risk >= ELEVATED → alert fired
# ============================================================

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import os
import time
import threading
import cv2

from flask import Flask, Response, jsonify
from flask_cors import CORS

# ── MODULE IMPORTS ────────────────────────────────────────────
from camera    import generate_laptop_cam, generate_usb_cam, generate_ip_cam
from detection import detect_faces, full_detection
from yolo      import detect_objects, yolo_loaded
from risk      import calculate_risk, get_risk_advice, CRITICAL_THRESHOLD, ELEVATED_THRESHOLD
from alerts    import init_socketio, send_alert, alert_intruder, alert_person, alert_high_risk, emit_detection

# ── FLASK APP SETUP ───────────────────────────────────────────
app      = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)
socketio = init_socketio(app)

print("=" * 55)
print("  Anvisksha — AI Based Infiltration Risk Prediction and Decision Support System")
print("=" * 55)
print(f"  Face Detection  : Haar Cascade        [OK]")
print(f"  Object Detection: YOLOv3              {'[OK]' if yolo_loaded else '[DISABLED - files missing]'}")
print(f"  Risk Engine     : MCDA Weighted Score  [OK]")
print(f"  Alert System    : Socket.IO            [OK]")
print("=" * 55)


# ── RISK STATE (shared across all camera threads) ─────────────
# Environmental conditions are fetched from /api/risk or set here.
# In production, connect this to a live weather API.
_current_conditions = {
    "isDay":      True,
    "fog":        False,
    "visibility": 10.0,
    "cloudCover": 20,
    "wind":       12.0,
    "humidity":   55,
    "moonPhase":  0.5,
}
_risk_lock = threading.Lock()


def get_current_risk():
    """Thread-safe read of the current risk score and level."""
    with _risk_lock:
        conditions = _current_conditions.copy()
    score, level, breakdown = calculate_risk(conditions)
    return score, level, breakdown


def update_conditions(new_conditions: dict):
    """Update environmental conditions (called by API endpoint)."""
    with _risk_lock:
        _current_conditions.update(new_conditions)


# ── ALERT THROTTLE ────────────────────────────────────────────
# Prevents alert spam: minimum 10 seconds between same-type alerts
_last_alert_time = {}
ALERT_COOLDOWN   = 10  # seconds


def _should_alert(key: str) -> bool:
    now  = time.time()
    last = _last_alert_time.get(key, 0)
    if now - last >= ALERT_COOLDOWN:
        _last_alert_time[key] = now
        return True
    return False


# ── MASTER DETECTION PIPELINE ─────────────────────────────────
def master_detection(frame, cam_id: int = 1):
    """
    Unified detection pipeline — runs on every camera frame.

    Pipeline steps:
      1. YOLOv3 object detection → annotated frame + label list
      2. Haar Cascade face detection → annotated frame + counts
      3. MCDA risk score calculation
      4. Alert logic: person detected + elevated risk → fire alert

    Args:
        frame  : BGR numpy image from camera
        cam_id : Camera identifier for alert context

    Returns:
        Annotated frame (BGR numpy image)
    """
    person_detected = False

    # ── STEP 1: YOLO OBJECT DETECTION ────────────────────────
    if yolo_loaded:
        frame, detected_labels = detect_objects(frame)
        if "person" in detected_labels:
            person_detected = True
    else:
        detected_labels = []

    # ── STEP 2: HAAR CASCADE FACE + ID DETECTION ─────────────
    frame, face_count, is_intruder, is_authorized = full_detection(frame)
    if face_count > 0:
        person_detected = True

    # ── STEP 3: RISK SCORING ──────────────────────────────────
    risk_score, risk_level, _ = get_current_risk()

    # Draw risk overlay on frame (top-right corner)
    _draw_risk_overlay(frame, risk_score, risk_level)

    # ── STEP 4: ALERT LOGIC ────────────────────────────────────
    # Intruder alert fires ALWAYS (not gated by risk level)
    if is_intruder and face_count > 0 and _should_alert(f"intruder_{cam_id}"):
        alert_intruder(cam_id)
        emit_detection(cam_id, 'UNKNOWN INTRUDER', 'face', True, 0.95)
        alert_high_risk(risk_score, risk_level)

    elif not is_intruder and face_count > 0 and _should_alert(f"authorized_{cam_id}"):
        send_alert(
            f"AUTHORIZED PERSON — Risk {risk_level} ({risk_score}/100)",
            level="LOW",
            cam_id=cam_id
        )
        emit_detection(cam_id, 'AUTHORIZED PERSON', 'face', False, 0.92)

    elif "person" in detected_labels and _should_alert(f"yolo_person_{cam_id}"):
        alert_person(cam_id, confidence=0.8)
        emit_detection(cam_id, 'PERSON DETECTED', 'yolo', True, 0.8)
        if risk_level == "CRITICAL" and _should_alert(f"high_risk_{cam_id}"):
            alert_high_risk(risk_score, risk_level)

    return frame


def _draw_risk_overlay(frame, score: int, level: str):
    """Draws the current risk score badge on the frame."""
    color_map = {
        "CRITICAL": (0, 0, 255),    # Red
        "ELEVATED": (0, 165, 255),  # Orange
        "LOW":      (0, 200, 80),   # Green
    }
    color = color_map.get(level, (200, 200, 200))
    h, w  = frame.shape[:2]

    label = f"RISK: {level}  {score}/100"
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
    x = w - tw - 14
    y = 10

    cv2.rectangle(frame, (x - 4, y), (x + tw + 6, y + th + 10), color, cv2.FILLED)
    cv2.putText(frame, label, (x, y + th + 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)


# ── DETECTION WRAPPERS (curried per cam) ─────────────────────
def make_detect_fn(cam_id: int):
    """Returns a frame-processing function bound to a cam_id."""
    def _fn(frame):
        return master_detection(frame, cam_id=cam_id)
    return _fn


# ── VIDEO FEED ROUTES ─────────────────────────────────────────
@app.route('/video_feed_1')
def video_feed_1():
    """CAM 01 — Laptop webcam with full face + YOLO detection."""
    gen = generate_laptop_cam(face_detect_fn=make_detect_fn(1))
    return Response(gen, mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_2')
def video_feed_2():
    """CAM 02 — DroidCam phone (IP camera)."""
    gen = generate_ip_cam(
        'http://10.11.194.205:4747/video',
        cam_label='CAM 02',
        detect_fn=make_detect_fn(2)
    )
    return Response(gen, mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_3')
def video_feed_3():
    """CAM 03 — USB webcam (index 1)."""
    gen = generate_usb_cam(index=1, face_detect_fn=make_detect_fn(3))
    return Response(gen, mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_4')
def video_feed_4():
    """CAM 04 — IP camera."""
    gen = generate_ip_cam(
        'http://172.30.104.59:4747/video',
        cam_label='CAM 04',
        detect_fn=make_detect_fn(4)
    )
    return Response(gen, mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_5')
def video_feed_5():
    """CAM 05 — Thermal mirror (greyscale applied by frontend)."""
    gen = generate_laptop_cam(face_detect_fn=make_detect_fn(5))
    return Response(gen, mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_6')
def video_feed_6():
    """CAM 06 — IP camera."""
    gen = generate_ip_cam(
        'http://192.168.137.240:8080/video',
        cam_label='CAM 06',
        detect_fn=make_detect_fn(6)
    )
    return Response(gen, mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_7')
def video_feed_7():
    """CAM 07 — IP camera."""
    gen = generate_ip_cam(
        'http://172.30.104.227:8080/video',
        cam_label='CAM 07',
        detect_fn=make_detect_fn(7)
    )
    return Response(gen, mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_8')
def video_feed_8():
    """CAM 08 — IP camera."""
    gen = generate_ip_cam(
        'http://172.30.104.175:8080/video',
        cam_label='CAM 08',
        detect_fn=make_detect_fn(8)
    )
    return Response(gen, mimetype='multipart/x-mixed-replace; boundary=frame')


# ── RISK API ──────────────────────────────────────────────────
@app.route('/api/risk', methods=['GET'])
def api_risk():
    """Returns current risk score + threat level as JSON."""
    score, level, breakdown = get_current_risk()
    advice = get_risk_advice(score, level)
    return jsonify({
        "score":      score,
        "level":      level,
        "advice":     advice,
        "breakdown":  breakdown,
        "conditions": _current_conditions,
    })


@app.route('/api/risk/update', methods=['POST'])
def api_risk_update():
    """
    Update environmental conditions via POST JSON body.

    Example body:
    {
        "isDay": false,
        "fog": true,
        "visibility": 1.5,
        "cloudCover": 90,
        "wind": 2,
        "humidity": 92,
        "moonPhase": 0.05
    }
    """
    from flask import request
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400
    update_conditions(data)
    score, level, breakdown = get_current_risk()
    if level in ("ELEVATED", "CRITICAL"):
        alert_high_risk(score, level)
    return jsonify({"score": score, "level": level, "updated": list(data.keys())})


@app.route('/api/status', methods=['GET'])
def api_status():
    """System health check."""
    return jsonify({
        "status":       "online",
        "yolo":         yolo_loaded,
        "face_cascade": True,
        "cameras":      8,
        "port":         5001,
    })


# ── ENTRY POINT ───────────────────────────────────────────────
if __name__ == "__main__":
    print("\n  Server starting on http://0.0.0.0:5001")
    print("  API endpoints:")
    print("    GET  /api/status       — system health")
    print("    GET  /api/risk         — current risk score")
    print("    POST /api/risk/update  — update weather conditions")
    print("    GET  /video_feed_1..8  — MJPEG camera streams\n")
    socketio.run(app, host='0.0.0.0', port=5001, debug=False, allow_unsafe_werkzeug=True)