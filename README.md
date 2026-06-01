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

## 📂 Project Directory & Modules Table

Here is the complete layout of the system, organized by application tier and functionality:

### 📁 Core Directories
| Directory Name | Description |
| :--- | :--- |
| `dataset/` | Local storage for collected facial imagery and vehicle samples used for training. |
| `frontend/` | The complete React.js web application (Dashboard, Incident Logs, Live Video). |
| `runs/` | Output directory containing YOLOv8 execution logs, validation metrics, and weights. |

### 🐍 Backend Python Modules (API & Computer Vision)
| File Name | Purpose |
| :--- | :--- |
| `main.py` | Master Flask application server, unified detection pipeline, and API endpoints. |
| `camera.py` | Multi-source MJPEG video ingestion and auto-reconnect fallback logic. |
| `detection.py` | Implementation of Haar Cascade face detection and HSV ID card validation. |
| `yolo.py` | YOLOv3 & YOLOv8 inference engine mapping to Microsoft COCO dataset classes. |
| `risk.py` | Dynamic MCDA environmental weather risk scoring engine. |
| `alerts.py` | Socket.IO real-time alert broadcast and event-driven logging pipeline. |

### 🛠️ Training & Utility Scripts
| File Name | Purpose |
| :--- | :--- |
| `collect_dataset.py` | Utility script to capture and build custom facial/object datasets. |
| `rename_dataset.py` | Helper tool to sanitize and structure image filenames for training. |
| `train_faces.py` | Localized script to capture, augment, train, and evaluate the LBPH face model. |
| `train_weapons.py` | Specialized script for custom YOLOv8 weapon model training. |
| `update_yolo.py` | Migration utility to add updated YOLO classes to the main detection pipeline. |
| `test_live.py` | Isolated testing environment for verifying camera and detection logic. |

### ⚙️ Configuration & Execution Files
| File Name | Purpose |
| :--- | :--- |
| `start_command_center.bat` | Windows batch file to concurrently launch both the Flask API and React frontend. |
| `coco.names` | Standard Microsoft COCO text file containing 80 target class names. |
| `yolov3.cfg` | Structural configuration file detailing the Darknet-53 network layers. |
| `yolov3.weights` | Pre-trained deep learning parameters for YOLOv3 object detection. |
| `best.pt` | Fine-tuned custom YOLOv8 model weights for tactical weapon detection. |
| `haarcascade_*.xml` | Pre-trained OpenCV XML weights for frontal face feature extraction. |

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
