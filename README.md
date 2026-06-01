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

## 📂 Project Structure

```text
ANVIKSHA---BORDER-SURVIELLANCE-SYSTEM/
├── dataset/                        # Stored imagery for face & vehicle samples
├── frontend/                       # React Web Command Center
│   ├── public/
│   └── src/
│       ├── components/             # Reusable UI dashboard panels
│       │   ├── AlertHistory.css / .jsx
│       │   ├── AnalyticsPanel.css / .jsx
│       │   ├── CameraFeed.css / .jsx
│       │   ├── EnvironmentalControls.css / .jsx
│       │   ├── IncidentLogger.css / .jsx
│       │   ├── LiveSurveillance.css / .jsx
│       │   ├── Navbar.css / .jsx
│       │   ├── RiskMatrix.css / .jsx
│       │   ├── Sidebar.css / .jsx
│       │   ├── SystemHealth.css / .jsx
│       │   └── WeatherMetrics.css / .jsx
│       ├── context/                # WebSocket persistent states
│       │   └── SocketContext.jsx
│       ├── pages/                  # Views and routing entry-points
│       │   ├── Dashboard.css / .jsx
│       │   ├── Homepage.css / .jsx
│       │   └── Login.css / .jsx
│       ├── utils/
│       │   └── constants.js
│       ├── App.css / .jsx
│       ├── index.css
│       └── main.jsx
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
