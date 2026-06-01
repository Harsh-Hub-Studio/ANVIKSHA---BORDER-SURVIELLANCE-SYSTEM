# Anviksha: AI-Based Infiltration Risk Prediction & Surveillance Decision Support System

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-19.2-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Backend-green.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red.svg)
![YOLO](https://img.shields.io/badge/YOLO-v3%20%7C%20v8-yellow.svg)

## 📖 Overview
**Anviksha** is a real-time, multi-modal AI surveillance platform that automates advanced threat detection entirely on standard commodity hardware. It processes live video from multiple sources to detect faces, identify objects and weapons, verify credentials, and dynamically assess environmental infiltration risks—delivering instantaneous alerts with sub-200ms latency.

## ✨ Key Features
* **Multi-Feed Surveillance**: Fault-tolerant MJPEG streaming from webcams and IP cameras.
* **Computer Vision Pipeline**:
  * **Face & ID Verification**: Viola-Jones Haar Cascades with LBPH recognition and HSV color-space segmentation for ID cards.
  * **Threat Detection (COCO)**: YOLOv3 and YOLOv8 models for robust person, vehicle, and weapon identification.
* **Environmental Risk Engine**: A Multi-Criteria Decision Analysis (MCDA) algorithm that scales threat scores based on visibility conditions (e.g., fog, rain).
* **Zero-Latency Dashboard**: React-based command center powered by Socket.IO for real-time incident logging.

---

## 📂 Project Structure

```text
ANVIKSHA---BORDER-SURVIELLANCE-SYSTEM/
├── dataset/                        # Stored imagery for face & vehicle samples
├── frontend/                       # React Web Command Center
│   ├── public/
│   └── src/
│       ├── components/             # Reusable UI dashboard panels
│       ├── context/                # WebSocket persistent states
│       ├── pages/                  # Views and routing entry-points
│       ├── utils/
│       ├── App.jsx / main.jsx
├── runs/                           # YOLO execution runs and output logs
├── alerts.py                       # Socket.IO instant alert broadcast pipeline
├── best.pt                         # Fine-tuned YOLOv8 custom weights for weapons
├── camera.py                       # Multi-source multi-threaded MJPEG ingestion 
├── coco.names                      # Standard 80 Microsoft COCO dataset classes
├── collect_dataset.py              # Script to build custom facial/object tracking profiles
├── detection.py                    # Cascade-classifiers and HSV credential filtering
├── haarcascade_frontalface_default.xml # Pre-trained OpenCV face tracking weights
├── main.py                         # Master Flask application server & unified pipeline
├── rename_dataset.py               # Utility to sanitize dataset formatting for training
├── risk.py                         # Dynamic MCDA weather score logic engine
├── start_command_center.bat        # Concurrent dual-system microservice startup routine
├── test_live.py                    # Independent localized validation interface
├── train_faces.py                  # Localized LBPH facial architecture trainer suite
├── train_weapons.py                # Specialized ultralytics customization tool
├── update_yolo.py                  # Single-run optimization script updating object classes
├── yolov3.cfg                      # Darknet layers structural topology
└── yolov3.weights                  # Darknet network parameters


## 📂 Project Structure & Modules

*(Awaiting your custom folder structure to be inserted here!)*

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
| `frontend/` | JSX/CSS | React application containing routing, authentication, and the command dashboard. |

---

## ⚙️ Core Functions & Methods

### `main.py`
* **`master_detection(frame, cam_id)`**: The unified pipeline that processes every camera frame through YOLO object detection, Haar Cascade face detection, and MCDA risk scoring before evaluating alert logic.
* **`get_current_risk()`**: Thread-safe method returning the live risk score, threat level, and environmental breakdown.

### `yolo.py`
* **`load_yolo()`**: Initializes Darknet-53 weights and classes into the OpenCV DNN backend. Maps detections against the Microsoft COCO class labels.
* **`detect_objects(frame)`**: Executes a forward pass through YOLO layers, applies Non-Maximum Suppression (NMS), and annotates the frame.

### `alerts.py`
* **`send_alert(message, level, cam_id)`**: Emits an asynchronous JSON payload over WebSockets to all connected frontends.

---

## 🚀 Installation & How to Run

### Prerequisites
* **Python 3.9+** installed on your system.
* **Node.js & npm** installed.
* Standard Webcam or an IP Camera Network (like a smartphone with DroidCam).

### Step 1: Clone the Repository
```bash
git clone [https://github.com/Harsh-Hub-Studio/ANVIKSHA---BORDER-SURVIELLANCE-SYSTEM.git](https://github.com/Harsh-Hub-Studio/ANVIKSHA---BORDER-SURVIELLANCE-SYSTEM.git)
cd ANVIKSHA---BORDER-SURVIELLANCE-SYSTEM
