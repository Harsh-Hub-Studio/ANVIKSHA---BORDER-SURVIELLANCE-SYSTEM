# # # # from flask import Flask, Response
# # # # from flask_cors import CORS
# # # # import cv2
# # # # import os
# # # # # Import your existing SurveillanceSystem class from main.py
# # # # from main import SurveillanceSystem 
# # # # from config import settings

# # # # app = Flask(__name__)
# # # # CORS(app) # Allows your React frontend to access this stream

# # # # def generate_frames():
# # # #     # Initialize your system; show_display=False stops the popup window
# # # #     system = SurveillanceSystem(show_display=False)
    
# # # #     if not system.cap.isOpened():
# # # #         print("Error: Could not open video source.")
# # # #         return

# # # #     print("AI Video Stream started on http://localhost:5001/video_feed")
    
# # # #     while True:
# # # #         success, frame = system.cap.read()
# # # #         if not success:
# # # #             # Loop the video if it's a file (like your gettyimages mp4)
# # # #             system.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
# # # #             continue
            
# # # #         # Resize for the web dashboard
# # # #         frame = cv2.resize(frame, (settings.FRAME_WIDTH, settings.FRAME_HEIGHT))
        
# # # #         # Run your AI detection (this calls your existing logic)
# # # #         processed_frame, detections, alerts = system._process_frame(frame)
        
# # # #         # Encode the frame as a JPEG for the browser
# # # #         ret, buffer = cv2.imencode('.jpg', processed_frame)
# # # #         frame_bytes = buffer.tobytes()
        
# # # #         # Stream the bytes
# # # #         yield (b'--frame\r\n'
# # # #                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# # # # @app.route('/video_feed')
# # # # def video_feed():
# # # #     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# # # # if __name__ == '__main__':
# # # #     # Running on 5001 to avoid conflict with your React or Node apps
# # # #     app.run(host='0.0.0.0', port=5001, threaded=True)

# # # import cv2
# # # from flask import Flask, Response
# # # from flask_cors import CORS

# # # app = Flask(__name__)
# # # # This allows your React dashboard (Port 3000) to safely access this Python server (Port 5001)
# # # CORS(app) 

# # # def generate_frames():
# # #     # cv2.VideoCapture(0) tells OpenCV to use your laptop's default built-in webcam
# # #     # If you plug in an external USB camera, you would change this 0 to a 1.
# # #     camera = cv2.VideoCapture(0)
    
# # #     if not camera.isOpened():
# # #         print("Error: Could not open the webcam.")
# # #         return

# # #     while True:
# # #         # Read the current frame from the camera
# # #         success, frame = camera.read()
# # #         if not success:
# # #             break
# # #         else:
# # #             # Convert the frame into a JPEG image
# # #             ret, buffer = cv2.imencode('.jpg', frame)
# # #             frame_bytes = buffer.tobytes()
            
# # #             # Yield the image back to the browser in a continuous stream format (MJPEG)
# # #             yield (b'--frame\r\n'
# # #                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# # # # This is the exact URL path your React dashboard is looking for!
# # # @app.route('/video_feed')
# # # def video_feed():
# # #     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# # # if __name__ == "__main__":
# # #     print("VISION ENGINE ONLINE: Starting camera feed on port 5001...")
# # #     # Run the server on port 5001 to match your React code
# # #     app.run(host='0.0.0.0', port=5001, debug=False)
# # # """'"''"""
# # import cv2
# # from flask import Flask, Response
# # from flask_cors import CORS

# # app = Flask(__name__)
# # CORS(app) # Allows React to talk to Python

# # def generate_frames():
# #     # THE MAGIC NUMBER: '0' activates your laptop's built-in webcam
# #     camera = cv2.VideoCapture(0)
    
# #     if not camera.isOpened():
# #         print("Error: Could not access the laptop camera.")
# #         return

# #     while True:
# #         success, frame = camera.read()
# #         if not success:
# #             break
# #         else:
# #             # Compress the camera frame and send it out
# #             ret, buffer = cv2.imencode('.jpg', frame)
# #             frame_bytes = buffer.tobytes()
# #             yield (b'--frame\r\n'
# #                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# # # This creates the exact link your dashboard uses: http://localhost:5001/video_feed
# # @app.route('/video_feed')
# # def video_feed():
# #     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# # if __name__ == "__main__":
# #     print("CAMERA ENGINE ONLINE: Streaming on port 5001...")
# #     app.run(host='0.0.0.0', port=5001, debug=False)
# import cv2
# import os
# import numpy as np
# import face_recognition
# from flask import Flask, Response
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# # --- 1. INITIALIZE THE DATABASE ---
# KNOWN_FACES_DIR = "authorized_faces"
# known_face_encodings = []
# known_face_names = []

# # Check if the folder exists, create it if it doesn't
# if not os.path.exists(KNOWN_FACES_DIR):
#     os.makedirs(KNOWN_FACES_DIR)
#     print(f"WARNING: Created '{KNOWN_FACES_DIR}' folder. Please put a photo inside it!")
# else:
#     # Load every photo in the authorized folder
#     for filename in os.listdir(KNOWN_FACES_DIR):
#         if filename.endswith((".jpg", ".png", ".jpeg")):
#             image_path = os.path.join(KNOWN_FACES_DIR, filename)
#             image = face_recognition.load_image_file(image_path)
            
#             # Map the face mathematically
#             encodings = face_recognition.face_encodings(image)
#             if len(encodings) > 0:
#                 known_face_encodings.append(encodings[0])
#                 # Remove the .jpg extension to get the name (e.g., "harsh")
#                 known_face_names.append(os.path.splitext(filename)[0].upper())
#                 print(f"Loaded Authorized Profile: {known_face_names[-1]}")

# # --- 2. LIVE CAMERA SCANNER ---
# def generate_frames():
#     camera = cv2.VideoCapture(0)
    
#     while True:
#         success, frame = camera.read()
#         if not success:
#             break
            
#         # Shrink the frame to 1/4 size so the AI processes it much faster
#         small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#         rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
#         # Find all faces in the current frame
#         face_locations = face_recognition.face_locations(rgb_small_frame)
#         face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # Compare the live face to our authorized database
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            
#             # Default state: Intruder
#             name = "UNKNOWN INTRUDER"
#             box_color = (0, 0, 255) # Red Box
            
#             # If a match is found: Authorized
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index] + " (AUTHORIZED)"
#                 box_color = (0, 255, 0) # Green Box
            
#             # Scale the box coordinates back up to normal size
#             top *= 4
#             right *= 4
#             bottom *= 4
#             left *= 4
            
#             # Draw the Targeting Box
#             cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
            
#             # Draw the Name Tag
#             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), box_color, cv2.FILLED)
#             cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

#         # Send the processed frame to the React dashboard
#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame_bytes = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# if __name__ == "__main__":
#     print("AI VISION ENGINE ONLINE: Scanning on port 5001...")
#     app.run(host='0.0.0.0', port=5001, debug=False)
import cv2
import numpy as np
from flask import Flask, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load OpenCV's fast, built-in face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def generate_frames():
    camera = cv2.VideoCapture(0)
    
    while True:
        success, frame = camera.read()
        if not success:
            break
            
        # 1. Detect Faces using basic OpenCV
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        
        # 2. Setup our "Military ID" Color Scanner (Looking for BLUE)
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Define the color blue in HSV format
        lower_blue = np.array([90, 50, 50])
        upper_blue = np.array([130, 255, 255])
        
        # Create a mask that only sees blue things
        blue_mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)
        blue_pixels = cv2.countNonZero(blue_mask)
        
        # 3. Decision Logic: If the camera sees enough blue pixels, consider the person Authorized!
        is_authorized = blue_pixels > 5000 

        for (x, y, w, h) in faces:
            if is_authorized:
                color = (0, 255, 0) # Green Box
                label = "MILITARY ID DETECTED // AUTHORIZED"
            else:
                color = (0, 0, 255) # Red Box
                label = "NO ID // UNKNOWN INTRUDER"
                
            # Draw the targeting box
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Draw the label background and text
            cv2.rectangle(frame, (x, y-35), (x+w, y), color, cv2.FILLED)
            cv2.putText(frame, label, (x + 5, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Broadcast to the React dashboard
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    print("VISION ENGINE ONLINE: Running Fast Scanner on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=False)