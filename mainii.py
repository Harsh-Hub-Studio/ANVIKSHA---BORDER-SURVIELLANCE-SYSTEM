# ============================================================
# FILE: main.py
# PURPOSE: Master server — connects all algorithm files
# RUNS ON: Port 5001
#
# FILE STRUCTURE:
#   main.py              ← THIS FILE (run this)
#   camera.py            ← Algorithm 5 (MJPEG) + 7 (Reconnect)
#   detection.py         ← Algorithm 1 (Face) + 3 (HSV ID)
#   object_detection.py  ← Algorithm 2 (YOLO Vehicles)
#   alerts.py            ← Algorithm 6 (Socket.IO)
#   risk.py              ← Algorithm 4 (Risk Scoring)
#
# HOW TO RUN:
#   python main.py
#
# CAMERA URLS (after running):
#   http://localhost:5001/video_feed_1   ← Laptop webcam
#   http://localhost:5001/video_feed_2   ← DroidCam phone
#   http://localhost:5001/video_feed_3   ← USB webcam
#   http://localhost:5001/video_feed_4   ← Second phone
#   http://localhost:5001/video_feed_5   ← Thermal (mirrors cam1)
# ============================================================

from flask import Flask, Response
from flask_cors import CORS
import cv2
import time

# ── IMPORT ALL ALGORITHM FILES ────────────────────────────────
from camera           import generate_laptop_cam, generate_usb_cam, generate_ip_cam, make_offline_frame
from detection        import full_detection, detect_faces
from object_detection import detect_objects
from alerts           import init_socketio, alert_intruder, alert_authorized, alert_vehicle, alert_person, alert_id_card
from risk             import calculate_risk, get_risk_advice

# ── FLASK APP SETUP ───────────────────────────────────────────
app      = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)
socketio = init_socketio(app)

# ── CORS HEADERS ON EVERY RESPONSE ───────────────────────────
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin',  '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response


# ── DroidCam / IP Camera IPs ──────────────────────────────────
# UPDATE THESE when WiFi changes
DROIDCAM_1 = 'http://192.168.7.31:4747/video'   # Phone 1
DROIDCAM_2 = 'http://10.203.101.59:4747/video'  # Phone 2


# ── CAMERA 1: LAPTOP WEBCAM ───────────────────────────────────
# Algorithm 1 (Face) + Algorithm 3 (HSV ID) + Algorithm 5 (MJPEG)
def cam1_stream():
    """
    CAM 01 — Laptop webcam
    Runs: Face detection + ID card detection + alerts
    """
    alert_cooldown = {}  # Prevent alert spam

    def process_frame(frame):
        frame, face_count, is_intruder, is_authorized = full_detection(frame)

        # Send alerts (with 10 second cooldown per type)
        now = time.time()
        if face_count > 0:
            if is_intruder and now - alert_cooldown.get('intruder', 0) > 10:
                alert_intruder(cam_id=1)
                alert_cooldown['intruder'] = now
            elif not is_intruder and now - alert_cooldown.get('authorized', 0) > 30:
                alert_authorized(cam_id=1)
                alert_cooldown['authorized'] = now

            if now - alert_cooldown.get('id_card', 0) > 15:
                alert_id_card(cam_id=1, is_authorized=is_authorized)
                alert_cooldown['id_card'] = now

        return frame

    return generate_laptop_cam(face_detect_fn=process_frame)


# ── CAMERA 2: DroidCam PHONE ──────────────────────────────────
# Algorithm 2 (YOLO) + Algorithm 5 (MJPEG) + Algorithm 7 (Reconnect)
def cam2_stream():
    """
    CAM 02 — DroidCam phone camera
    Runs: YOLO vehicle + person detection + alerts
    """
    alert_cooldown = {}

    def process_frame(frame):
        frame, detections = detect_objects(frame)
        now = time.time()

        for det in detections:
            key = det['class']
            if now - alert_cooldown.get(key, 0) > 15:
                if det['class'] == 'person':
                    alert_person(cam_id=2, confidence=det['confidence'])
                elif det['class'] in ['car', 'truck', 'bus', 'motorbike']:
                    alert_vehicle(cam_id=2, vehicle_type=det['class'], confidence=det['confidence'])
                alert_cooldown[key] = now
        return frame

    return generate_ip_cam(DROIDCAM_1, cam_label="CAM 02", detect_fn=process_frame)


# ── CAMERA 3: USB WEBCAM ──────────────────────────────────────
# Algorithm 1 (Face) + Algorithm 5 (MJPEG)
def cam3_stream():
    """
    CAM 03 — USB webcam
    Runs: Face detection only
    """
    def process_frame(frame):
        frame, face_count, is_intruder = detect_faces(frame)
        return frame

    return generate_usb_cam(index=1, face_detect_fn=process_frame)


# ── CAMERA 4: SECOND PHONE ────────────────────────────────────
# Algorithm 2 (YOLO) + Algorithm 5 (MJPEG)
def cam4_stream():
    """
    CAM 04 — Second DroidCam phone
    Runs: YOLO object detection
    """
    def process_frame(frame):
        frame, _ = detect_objects(frame)
        return frame

    return generate_ip_cam(DROIDCAM_2, cam_label="CAM 04", detect_fn=process_frame)


# ── CAMERA 5: THERMAL (Mirrors CAM 1) ────────────────────────
# Algorithm 5 (MJPEG) — greyscale filter applied by frontend
def cam5_stream():
    """
    CAM 05 — Thermal IR simulation
    Same feed as CAM 01 — greyscale applied by React frontend
    Runs: Face detection (works in greyscale)
    """
    return generate_laptop_cam()


# ── FLASK ROUTES ──────────────────────────────────────────────
@app.route('/video_feed_1')
def video_feed_1():
    return Response(cam1_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_2')
def video_feed_2():
    return Response(cam2_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_3')
def video_feed_3():
    return Response(cam3_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_4')
def video_feed_4():
    return Response(cam4_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_5')
def video_feed_5():
    return Response(cam5_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_6')
def video_feed_6():
    return Response(generate_ip_cam('http://0.0.0.0:8080/video', 'CAM 06'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_7')
def video_feed_7():
    return Response(generate_ip_cam('http://0.0.0.0:8080/video', 'CAM 07'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_8')
def video_feed_8():
    return Response(generate_ip_cam('http://0.0.0.0:8080/video', 'CAM 08'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# ── STARTUP ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  ARGUS SENTINEL — FULL SYSTEM ONLINE")
    print("=" * 55)
    print("  Algorithm 1: Haar Cascade Face Detection    ✅")
    print("  Algorithm 2: YOLOv3 Vehicle Detection       ✅")
    print("  Algorithm 3: HSV Color ID Detection         ✅")
    print("  Algorithm 4: Weighted Risk Scoring          ✅")
    print("  Algorithm 5: MJPEG Streaming                ✅")
    print("  Algorithm 6: Socket.IO Event Alerts         ✅")
    print("  Algorithm 7: Auto Reconnect Retry           ✅")
    print("=" * 55)
    print("  Camera feeds: http://localhost:5001/video_feed_1")
    print("=" * 55)

    socketio.run(
        app,
        host='0.0.0.0',
        port=5001,
        debug=False,
        allow_unsafe_werkzeug=True
    )
