# ============================================================
# FILE: camera.py
# ALGORITHMS: 
#   - Algorithm 5: MJPEG Streaming
#   - Algorithm 7: Auto Reconnect Retry
# PURPOSE: Handles all camera feed generation and streaming
# ============================================================

import cv2
import numpy as np
import time


# ── OFFLINE PLACEHOLDER ──────────────────────────────────────
def make_offline_frame(label="CAMERA OFFLINE"):
    """
    Generates a black placeholder frame when camera is unavailable.
    Shown while auto-reconnect is attempting to restore the feed.
    """
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(frame, label,          (120, 220), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 200), 3)
    cv2.putText(frame, "Reconnecting...",(185, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
    return buffer.tobytes() if ret else None


# ── ALGORITHM 5: MJPEG STREAMING (Laptop Webcam) ─────────────
def generate_laptop_cam(face_detect_fn=None):
    """
    Streams laptop webcam via MJPEG.
    Optionally runs a detection function on each frame.

    Algorithm: MJPEG Multipart HTTP Streaming
    - Captures frame from webcam using OpenCV
    - Encodes as JPEG (lossy compression ~80% size reduction)
    - Yields as HTTP multipart boundary
    - Browser renders each JPEG creating live video effect
    """
    camera = cv2.VideoCapture(0)
    try:
        while True:
            success, frame = camera.read()

            # ── ALGORITHM 7: AUTO RECONNECT ──────────────────
            if not success:
                placeholder = make_offline_frame("CAM 01 OFFLINE")
                if placeholder:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n'
                           + placeholder + b'\r\n')
                time.sleep(1)
                camera.release()
                camera = cv2.VideoCapture(0)  # Retry connection
                continue

            # Run detection function if provided (face/object detection)
            if face_detect_fn:
                frame = face_detect_fn(frame)

            # ── ALGORITHM 5: MJPEG FRAME ENCODING ────────
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n'
                       + buffer.tobytes() + b'\r\n')
    finally:
        camera.release()


# ── ALGORITHM 5: MJPEG STREAMING (USB Webcam) ────────────────
def generate_usb_cam(index=1, face_detect_fn=None):
    """
    Streams USB webcam via MJPEG.
    index: camera index (0=laptop, 1=USB, 2=second USB etc.)
    """
    camera = cv2.VideoCapture(index)
    try:
        while True:
            success, frame = camera.read()

            # ── ALGORITHM 7: AUTO RECONNECT ──────────────────
            if not success:
                placeholder = make_offline_frame(f"CAM USB-{index} OFFLINE")
                if placeholder:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n'
                           + placeholder + b'\r\n')
                time.sleep(1)
                camera.release()
                camera = cv2.VideoCapture(index)
                continue

            if face_detect_fn:
                frame = face_detect_fn(frame)

            frame = cv2.resize(frame, (640, 480))
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n'
                       + buffer.tobytes() + b'\r\n')
    finally:
        camera.release()


# ── ALGORITHM 5+7: MJPEG STREAMING (IP / DroidCam) ───────────
def generate_ip_cam(ip_url, cam_label="IP CAM", detect_fn=None):
    """
    Streams any IP camera (DroidCam, RTSP, HTTP) via MJPEG.
    Includes full auto-reconnect with consecutive failure tracking.

    Algorithm 5: MJPEG Streaming
    Algorithm 7: Auto Reconnect Retry
    - Tracks consecutive failures
    - Reconnects after 5 failures
    - Shows offline placeholder during downtime
    - Waits 3 seconds between reconnect attempts
    """
    while True:
        # ── ALGORITHM 7: CONNECTION ATTEMPT ──────────────────
        camera = cv2.VideoCapture(ip_url)
        if not camera.isOpened():
            placeholder = make_offline_frame(f"{cam_label} OFFLINE")
            if placeholder:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n'
                       + placeholder + b'\r\n')
            time.sleep(3)  # Wait before retrying
            continue

        consecutive_failures = 0

        try:
            while True:
                success, frame = camera.read()

                # ── ALGORITHM 7: FAILURE COUNTER ─────────────
                if not success:
                    consecutive_failures += 1
                    if consecutive_failures >= 5:
                        # Too many failures — trigger full reconnect
                        break
                    placeholder = make_offline_frame(f"{cam_label} OFFLINE")
                    if placeholder:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n'
                               + placeholder + b'\r\n')
                    time.sleep(0.5)
                    continue

                consecutive_failures = 0  # Reset on success

                if detect_fn:
                    frame = detect_fn(frame)

                frame = cv2.resize(frame, (640, 480))

                # ── ALGORITHM 5: MJPEG FRAME YIELD ───────────
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n'
                           + buffer.tobytes() + b'\r\n')
        finally:
            camera.release()

        time.sleep(2)  # Brief pause before reconnect
