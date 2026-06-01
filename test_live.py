import cv2
from detection import full_detection
from yolo import detect_objects, yolo_loaded

def main():
    print("==================================================")
    print("  LIVE CAMERA TEST: Face + Weapon Detection       ")
    print("==================================================")
    
    print("Initializing camera...")
    # Use cv2.CAP_DSHOW for reliable Windows camera access
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("ERROR: Could not open laptop camera.")
        return

    print("Camera opened successfully!")
    print("Press the 'q' key on your keyboard to close the window.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("ERROR: Failed to grab frame from camera.")
            break
            
        # 1. Run YOLO Object/Weapon Detection
        if yolo_loaded:
            frame, detected_labels = detect_objects(frame)
            
        # 2. Run Face Detection
        frame, face_count, is_intruder, is_authorized = full_detection(frame)
        
        # Display the output directly on screen
        cv2.imshow("Anviksha LIVE - Face & Weapon Detection", frame)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Camera closed.")

if __name__ == "__main__":
    main()
