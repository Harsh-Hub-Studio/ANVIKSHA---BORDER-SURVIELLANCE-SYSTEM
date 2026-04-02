# ============================================================
# FILE: collect_dataset.py
# PURPOSE: Collect your own face and vehicle dataset
# RUN: python collect_dataset.py
# ============================================================

import cv2
import os
import time


def collect_face_dataset():
    """
    Captures face photos from webcam for face recognition training.
    Press SPACE to capture, Q to quit.
    Saves to: authorized_faces/<name>/
    """
    name     = input("\nEnter person name (e.g. HARSH): ").strip().upper()
    save_dir = f"authorized_faces/{name}"
    os.makedirs(save_dir, exist_ok=True)

    print(f"\nCapturing 50 photos for {name}")
    print("Tips for best results:")
    print("  - Look directly at camera")
    print("  - Slightly turn left, right, up, down")
    print("  - Try with and without glasses")
    print("  - Try in different lighting")
    print("\nPress SPACE to capture | Q to quit\n")

    camera = cv2.VideoCapture(0)
    count  = 0

    while count < 50:
        ret, frame = camera.read()
        if not ret:
            break

        # Show progress on frame
        cv2.putText(frame, f"Capturing: {name}", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
        cv2.putText(frame, f"Photos: {count}/50", (10,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.putText(frame, "SPACE=capture  Q=quit", (10, frame.shape[0]-15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        cv2.imshow(f'Collecting: {name}', frame)

        key = cv2.waitKey(1)
        if key == ord(' '):
            filename = f"{save_dir}/{name}_{count:03d}.jpg"
            cv2.imwrite(filename, frame)
            count += 1
            print(f"  Saved: {filename} ({count}/50)")
        elif key == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
    print(f"\nDone! {count} photos saved in {save_dir}/")
    print("Now run: python train_test.py to train the model")


def collect_vehicle_dataset():
    """
    Captures vehicle images from phone camera (DroidCam).
    Auto-captures every 2 seconds.
    Saves to: dataset/vehicles/<type>/
    """
    vehicle_type = input("\nVehicle type (car/bike/truck/bus): ").strip().lower()
    droidcam_ip  = input("DroidCam IP (e.g. 192.168.7.31): ").strip()
    url          = f"http://{droidcam_ip}:4747/video"
    save_dir     = f"dataset/vehicles/{vehicle_type}"
    os.makedirs(save_dir, exist_ok=True)

    print(f"\nConnecting to DroidCam at {url}...")
    print(f"Auto-capturing {vehicle_type} images every 2 seconds")
    print("Press Q to stop\n")

    camera = cv2.VideoCapture(url)
    count  = 0

    if not camera.isOpened():
        print(f"ERROR: Could not connect to {url}")
        print("Make sure DroidCam app is running on your phone")
        return

    while count < 200:
        ret, frame = camera.read()
        if not ret:
            print("Connection lost — retrying...")
            time.sleep(2)
            camera = cv2.VideoCapture(url)
            continue

        # Show info on frame
        cv2.putText(frame, f"Type: {vehicle_type.upper()}", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
        cv2.putText(frame, f"Captured: {count}/200", (10,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        cv2.imshow(f'Collecting: {vehicle_type}', frame)

        # Auto capture every 2 seconds
        filename = f"{save_dir}/{vehicle_type}_{count:04d}.jpg"
        cv2.imwrite(filename, frame)
        count += 1
        print(f"  Saved: {filename}")

        if cv2.waitKey(2000) == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
    print(f"\nDone! {count} images saved in {save_dir}/")
    print("Next step: Label images using LabelImg tool")
    print("  pip install labelImg")
    print("  labelImg")


def collect_id_card_dataset():
    """
    Captures ID card photos in different lighting conditions.
    Used to calibrate HSV color range.
    Saves to: dataset/id_cards/
    """
    save_dir = "dataset/id_cards"
    os.makedirs(save_dir, exist_ok=True)

    print("\nID Card HSV Calibration Dataset")
    print("Hold your blue ID card in front of camera")
    print("Capture in DIFFERENT lighting conditions:")
    print("  1. Bright light")
    print("  2. Dim light")
    print("  3. Partial shadow")
    print("  4. Different angles")
    print("\nPress SPACE to capture | Q to quit\n")

    camera = cv2.VideoCapture(0)
    count  = 0

    while True:
        ret, frame = camera.read()
        if not ret:
            break

        # Show HSV values at center
        hsv    = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, w   = frame.shape[:2]
        center = hsv[h//2, w//2]

        cv2.putText(frame, f"Center HSV: H={center[0]} S={center[1]} V={center[2]}", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
        cv2.putText(frame, f"Photos: {count}", (10,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        cv2.putText(frame, "SPACE=capture  Q=quit", (10, h-15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        # Draw center crosshair
        cv2.line(frame, (w//2-20, h//2), (w//2+20, h//2), (0,255,255), 1)
        cv2.line(frame, (w//2, h//2-20), (w//2, h//2+20), (0,255,255), 1)

        cv2.imshow('ID Card Calibration', frame)

        key = cv2.waitKey(1)
        if key == ord(' '):
            filename = f"{save_dir}/card_{count:03d}.jpg"
            cv2.imwrite(filename, frame)
            count += 1
            print(f"  H={center[0]} S={center[1]} V={center[2]} → saved {filename}")
        elif key == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
    print(f"\nSaved {count} ID card photos")
    print("Update HSV range in detection.py based on the H values shown above")


# ── MAIN MENU ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  ARGUS SENTINEL — Dataset Collection Tool")
    print("=" * 50)
    print("  1. Collect face photos (authorized persons)")
    print("  2. Collect vehicle images (DroidCam)")
    print("  3. Collect ID card photos (HSV calibration)")
    print("=" * 50)

    choice = input("Select (1/2/3): ").strip()

    if choice == '1':
        collect_face_dataset()
    elif choice == '2':
        collect_vehicle_dataset()
    elif choice == '3':
        collect_id_card_dataset()
    else:
        print("Invalid choice")
