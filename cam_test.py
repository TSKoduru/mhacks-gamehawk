import cv2

# Open the default camera (usually /dev/video0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise IOError("Cannot open webcam")

# Read one frame
ret, frame = cap.read()

if ret:
    # Save the frame as an image
    cv2.imwrite("usb_cam_capture.jpg", frame)
    print("Image saved as usb_cam_capture.jpg")
else:
    print("Failed to capture image")

cap.release()
