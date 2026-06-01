# Anviksha: AI-Based Infiltration Risk Prediction & Surveillance Decision Support System

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-19.2-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Backend-green.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red.svg)
![YOLO](https://img.shields.io/badge/YOLO-v3%20%7C%20v8-yellow.svg)

## 📖 Overview
Traditional surveillance systems depend on continuous human monitoring and proprietary hardware, making them vulnerable to fatigue, lag, and high costs. **Anviksha** is a real-time, multi-modal surveillance platform designed to automate advanced threat detection entirely on standard commodity hardware. 

The system simultaneously streams live video from heterogeneous network sources, detects human faces, identifies specific objects, vehicles, and weapons, verifies secure credentials, assesses environmental threat levels, and pushes instantaneous alerts. It achieves sub-200ms glass-to-glass latency using HTTP multipart MJPEG streaming and event-driven WebSockets.

## ✨ Key Features
* **Multi-Feed Surveillance**: Seamlessly monitors multiple sources (Webcams, IP Cameras, DroidCam) with auto-reconnection and fault tolerance.
* **Computer Vision Pipeline**:
  * **Facial Detection & Recognition**: Viola-Jones Haar Cascades combined with an LBPH recognizer to instantly flag intruders vs. authorized personnel.
  * **Object & Weapon Detection (Microsoft COCO)**: YOLOv3 and YOLOv8 models for robust, multi-class object, vehicle, and weapon identification. The models leverage weights pre-trained on the **Microsoft COCO (Common Objects in Context)** dataset, ensuring high-accuracy recognition across 80 standard object classes in complex environments.
  * **Illumination-Invariant Verification**: HSV color-space segmentation for rule-based authorized ID card verification.
* **Infiltration Risk Engine**: A proprietary Multi-Criteria Decision Analysis (MCDA) algorithm that dynamically calculates threat scores by weighing visibility-impairing atmospheric conditions (e.g., fog, moonlight, rain).
* **Real-Time Command Dashboard**: A unified React-based command center displaying live streams, tracking incident logs, and visualizing environmental intel, powered by Socket.IO for zero-polling lag.

---

## 📂 Project Structure & Modules

| File / Module | Language | Description |
| :--- | :--- | :--- |
| `main.py` | Python | Flask server, master detection pipeline, and API endpoints. |
| `camera.py` | Python | MJPEG streaming & auto-reconnect fallback logic. |
| `detection.py` | Python | Haar Cascade face detection + HSV ID card detection. |
| `yolo.py` | Python | YOLOv3 (objects) + YOLOv8 (weapons) inference engine using Microsoft COCO classes. |
| `risk.py` | Python | MCDA weighted environmental risk scoring engine. |
| `alerts.py` | Python | Socket.IO real-time alert push and incident logging. |
| `train_faces.py` | Python | LBPH face recognizer suite: capture, augment, train, evaluate. |
| `train_weapons.py` | Python | YOLOv8 weapon model automated training script. |
| `collect_dataset.py`| Python | Dataset collection tool for faces, ID cards, and vehicles. |
| `rename_dataset.py` | Python | Bulk rename utility for structuring training images. |
| `update_yolo.py` | Python | Migration script adding YOLOv8 weapon detection support. |
| `test_live.py` | Python | Live camera test environment for face and weapon detection. |
| `start_command_center.bat` | Batch | Native launcher that boots the Python API and React dashboard. |
| `frontend/` | JSX/CSS | React application containing routing, authentication, and the command dashboard. |

---

## ⚙️ Core Functions & Methods

### `main.py`
* **`master_detection(frame, cam_id)`**: The unified pipeline that processes every camera frame through YOLO object detection, Haar Cascade face detection, and MCDA risk scoring before evaluating alert logic.
* **`get_current_risk()`**: Thread-safe method returning the live risk score, threat level, and environmental breakdown.
* **`update_conditions(new_conditions)`**: REST endpoint handler for updating real-time weather metrics.

### `camera.py`
* **`generate_laptop_cam()` / `generate_usb_cam()` / `generate_ip_cam()`**: Captures frames via OpenCV, handles camera dropouts by yielding placeholder offline frames, and encodes successful frames into JPEG format for multipart HTTP boundary streaming.

### `detection.py`
* **`detect_faces(frame)`**: Scans for human faces, runs LBPH recognition to determine authorization status, and draws bounding boxes (Green = Authorized, Red = Unknown Intruder).
* **`detect_id_card(frame)`**: Isolates predefined blue pixel ranges in the HSV color space to verify physical military/security IDs.
* **`train_face_recognizer()`**: Automates the training of the LBPH Face Recognizer using local image datasets.

### `yolo.py`
* **`load_yolo()`**: Initializes Darknet-53 weights and classes into the OpenCV DNN backend. It maps detections against the Microsoft COCO class labels to identify persons, vehicles, and distinct threats.
* **`detect_objects(frame)`**: Executes a forward pass through YOLO layers, applies Non-Maximum Suppression (NMS) to filter overlapping bounding boxes, and annotates the frame with classifications and confidence percentages.

### `risk.py`
* **`calculate_risk(conditions)`**: Applies the MCDA mathematical formula, summing up weighted penalties for variables like low visibility (`+15`), heavy fog (`+20`), or low light (`+25`), returning an aggregate risk score out of 100.

### `alerts.py`
* **`send_alert(message, level, cam_id)`**: Emits an asynchronous JSON payload over WebSockets to all connected frontends.
* **`emit_detection()`**: Triggers incident log entries, frontend camera auto-zoom, and risk threat boosts dynamically.

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.9+
* Node.js & npm
* Standard Webcam or IP Camera Network

### 1. Clone the Repository
```bash
git clone [https://github.com/Harsh-Hub-Studio/ANVIKSHA---BORDER-SURVIELLANCE-SYSTEM.git](https://github.com/Harsh-Hub-Studio/ANVIKSHA---BORDER-SURVIELLANCE-SYSTEM.git)
cd ANVIKSHA---BORDER-SURVIELLANCE-SYSTEM
