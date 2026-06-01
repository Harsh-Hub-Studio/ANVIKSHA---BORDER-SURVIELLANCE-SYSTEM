# Anviksha: AI-Based Infiltration Risk Prediction and Decision Support System

## 1. Executive Summary
Anviksha (Argus Sentinel) is a comprehensive, multi-layered surveillance and security platform. It integrates real-time video streaming, multiple AI-driven computer vision pipelines (object and face detection), environmental risk assessment, and a real-time WebSocket-based alert system. The system consists of a Python-based intelligent backend and a React/Node.js frontend command center.

---

## 2. Core Algorithms Implemented

The system explicitly utilizes 7 core algorithms and architectural patterns to achieve real-time security monitoring:

### Algorithm 1: Viola-Jones Haar Cascade (Face Detection) & LBPH
*   **Purpose:** To quickly and efficiently detect human faces in a video frame and recognize if they are authorized personnel.
*   **Mechanism:** 
    *   **Detection:** Uses pre-trained OpenCV Haar Cascades (`haarcascade_frontalface_default.xml`) which applies a sliding window across a grayscale image to detect facial features (edges, lines, and center-surround features).
    *   **Recognition:** Uses **Local Binary Pattern Histograms (LBPH)**. It divides the detected face into a grid, calculates texture histograms, and compares them against trained histograms of authorized personnel using Chi-squared distance. A lower distance (< 80) indicates a recognized match.

### Algorithm 2: YOLOv3 (You Only Look Once) Object Detection
*   **Purpose:** To detect and classify various entities in the environment, such as people, vehicles, weapons, and suspicious baggage.
*   **Mechanism:** A deep learning model that divides the image into a grid and simultaneously predicts bounding boxes and class probabilities for each grid cell. It uses Non-Maximum Suppression (NMS) to eliminate overlapping bounding boxes, ensuring each object is only detected once.

### Algorithm 3: HSV Color Segmentation (ID Card Verification)
*   **Purpose:** To physically verify if a detected person is carrying an authorized blue military ID card.
*   **Mechanism:** Converts the standard BGR video frame into the HSV (Hue, Saturation, Value) color space. It applies a strict masking range to isolate blue pixels. If the count of blue pixels exceeds a predefined threshold (e.g., 5000 pixels), the system confirms the presence of the ID card.

### Algorithm 4: MCDA (Multi-Criteria Decision Analysis) / Weighted Scoring
*   **Purpose:** To dynamically calculate an environmental infiltration risk score (0-100) based on prevailing weather and lighting conditions.
*   **Mechanism:** Assigns specific mathematical weights to threat factors. For example, Nighttime (+25), Fog (+20), Low Visibility (+15). The system sums these factors and classifies the environment into Threat Levels: LOW, ELEVATED (≥40), or CRITICAL (≥70). 

### Algorithm 5: MJPEG HTTP Streaming
*   **Purpose:** To broadcast live camera feeds from the Python backend to the web-based command center.
*   **Mechanism:** Captures frames via OpenCV, compresses them individually as JPEG images (reducing size by ~80%), and serves them over an HTTP connection using a `multipart/x-mixed-replace` boundary. The browser renders these sequential images as a live video feed.

### Algorithm 6: Event-Driven Architecture (Publisher-Subscriber)
*   **Purpose:** To deliver instantaneous alerts and incident logs to the frontend without requiring the dashboard to constantly refresh.
*   **Mechanism:** Implemented using Socket.IO (WebSockets). The Python server acts as the Publisher. When an anomaly is detected (e.g., an intruder or weapon), it emits an event. The React dashboard, acting as a Subscriber, listens for these events and immediately triggers UI popups and alarm sounds.

### Algorithm 7: Auto-Reconnect Retry Logic
*   **Purpose:** To ensure maximum uptime and fault tolerance for network and USB cameras.
*   **Mechanism:** Continuously monitors the status of the `cv2.VideoCapture` read. If a frame fails to grab consecutively, the system releases the camera resource, yields a black "OFFLINE" placeholder frame to the frontend, and initiates a timed backoff loop to automatically re-establish the connection.

---

## 3. System Architecture & File Structure

The project is modularly divided into specific Python scripts, each handling a distinct responsibility within the pipeline.

### The Entry Point
*   **`main.py`**
    *   **Role:** The core Flask web server and orchestration engine.
    *   **Function:** Imports all other modules. It sets up the camera routing (`/video_feed_1` to `8`), initializes the WebSocket server, and exposes API endpoints for environmental risk updates. It contains the `master_detection` pipeline which decides when to fire an alert based on combined inputs from YOLO, Face Detection, and Risk scores.

### The Vision Engines
*   **`detection.py`**
    *   **Role:** Handles all human-centric detection (Algorithms 1 & 3).
    *   **Function:** Loads the Haar Cascade and LBPH face models. It contains `detect_faces()` to identify intruders vs. authorized staff, and `detect_id_card()` to look for the blue color signature of ID cards.
*   **`yolo.py`**
    *   **Role:** Handles deep learning object detection (Algorithm 2).
    *   **Function:** Loads `yolov3.weights` and `yolov3.cfg`. Filters detected objects strictly to surveillance-relevant classes (persons, vehicles, weapons, bags) and draws labeled bounding boxes.

### The Logic & Communication Engines
*   **`risk.py`**
    *   **Role:** The environmental threat calculator (Algorithm 4).
    *   **Function:** Contains the hardcoded weighted values for various weather conditions and calculates the final risk score.
*   **`alerts.py`**
    *   **Role:** The WebSocket dispatcher (Algorithm 6).
    *   **Function:** Maintains an active Socket.IO connection. It exposes functions like `alert_intruder()` and `alert_high_risk()` which format the data and push it instantly to the connected React dashboard.
*   **`camera.py`**
    *   **Role:** Hardware interfacing and streaming (Algorithms 5 & 7).
    *   **Function:** Connects to physical laptop webcams, USB cameras, and IP cameras (like DroidCam). It handles the MJPEG encoding and the automatic reconnection logic if a camera goes offline.

### The Training & Utility Scripts
*   **`train_faces.py`**
    *   **Role:** The data collection and training pipeline for facial recognition.
    *   **Function:** Provides an interactive CLI to: (1) Capture new face photos via webcam, (2) Augment the dataset by flipping/blurring images, (3) Train the LBPH `.xml` model, and (4) Run a live webcam evaluation to test accuracy.
*   **`train_weapons.py`**
    *   **Role:** Model training script for advanced YOLOv8.
    *   **Function:** Uses the `ultralytics` library to train a newer YOLO model on a custom dataset (`weapon_detection/dataset.yaml`) for specialized weapon detection.
*   **`start_command_center.bat`**
    *   **Role:** Deployment script.
    *   **Function:** A Windows batch file that concurrently starts the Python Flask backend and the Node.js/React frontend.

---

## 4. Logical Data Flow

1. **Ingestion:** `camera.py` captures a raw BGR frame from the hardware.
2. **Processing:** `main.py` intercepts the frame and passes it to:
    *   `yolo.py` (Is there a person or suspicious object?)
    *   `detection.py` (Is the person authorized? Do they have an ID?)
3. **Contextualization:** `main.py` checks `risk.py` to see the current environmental threat level.
4. **Decision:** If an unauthorized person is detected, or a high-risk scenario is met, `main.py` triggers `alerts.py`.
5. **Dispatch:** `alerts.py` pushes a JSON payload via WebSockets.
6. **Delivery:** The modified video frame (with bounding boxes) is sent via HTTP MJPEG stream, and the Alert data triggers an alarm on the Frontend Dashboard.
