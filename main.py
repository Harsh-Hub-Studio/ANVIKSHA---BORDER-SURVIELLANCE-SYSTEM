import cv2
import numpy as np
from flask import Flask, Response
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def make_offline_frame(label="CAMERA OFFLINE"):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(frame, label, (120, 220), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 200), 3)
    cv2.putText(frame, "Reconnecting...", (185, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
    ret, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes() if ret else None

# CAM 1 — Laptop webcam with face detection
def generate_cam1():
    camera = cv2.VideoCapture(0)
    try:
        while True:
            success, frame = camera.read()
            if not success:
                placeholder = make_offline_frame("CAM 01 OFFLINE")
                if placeholder:
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + placeholder + b'\r\n')
                time.sleep(1)
                camera.release()
                camera = cv2.VideoCapture(0)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "SCANNING...", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    finally:
        camera.release()

# CAM 2 — Second webcam (USB index 1)
def generate_cam2():
    camera = cv2.VideoCapture(1)
    try:
        while True:
            success, frame = camera.read()
            if not success:
                placeholder = make_offline_frame("CAM 02 OFFLINE")
                if placeholder:
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + placeholder + b'\r\n')
                time.sleep(1)
                camera.release()
                camera = cv2.VideoCapture(1)
                continue
            frame = cv2.resize(frame, (640, 480))
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    finally:
        camera.release()

# Generic IP cam generator with auto-reconnect
def generate_ip_cam(ip_url, cam_label="IP CAM"):
    while True:
        camera = cv2.VideoCapture(ip_url)
        if not camera.isOpened():
            placeholder = make_offline_frame(f"{cam_label} OFFLINE")
            if placeholder:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + placeholder + b'\r\n')
            time.sleep(3)
            continue

        consecutive_failures = 0
        try:
            while True:
                success, frame = camera.read()
                if not success:
                    consecutive_failures += 1
                    if consecutive_failures >= 5:
                        break
                    placeholder = make_offline_frame(f"{cam_label} OFFLINE")
                    if placeholder:
                        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + placeholder + b'\r\n')
                    time.sleep(0.5)
                    continue

                consecutive_failures = 0
                frame = cv2.resize(frame, (640, 480))
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        finally:
            camera.release()
        time.sleep(2)

# ── ROUTES ───────────────────────────────────────────────
@app.route('/video_feed_1')
def video_feed_1():
    # Laptop webcam (index 0) — face detection
    return Response(generate_cam1(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_2')
def video_feed_2():
    # DroidCam phone
    return Response(generate_ip_cam('http://192.168.1.6:4747/video', 'CAM 02'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_3')
def video_feed_3():
    # Second USB webcam (index 1)
    return Response(generate_cam2(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_4')
def video_feed_4():
    return Response(generate_ip_cam('http://172.30.104.59:4747/video', 'CAM 04'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_5')
def video_feed_5():
    # THERMAL — mirrors cam 1 (greyscale applied by frontend)
    return Response(generate_cam1(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_6')
def video_feed_6():
    return Response(generate_ip_cam('http://192.168.137.240:8080/video', 'CAM 06'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_7')
def video_feed_7():
    return Response(generate_ip_cam('http://172.30.104.227:8080/video', 'CAM 07'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_8')
def video_feed_8():
    return Response(generate_ip_cam('http://172.30.104.175:8080/video', 'CAM 08'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    print("ARGUS — 8-CAM ARRAY ONLINE on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)