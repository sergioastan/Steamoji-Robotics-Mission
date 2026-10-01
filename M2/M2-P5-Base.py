import cv2
import numpy as np
import time

# TODO: Import the MyCobot280 package from the pymycobot library
# ---
from pymycobot.mycobot280 import MyCobot280
# ---

# =====================================================================
# ROBOT INITIALIZATION
# =====================================================================

try:
    # TODO: Initialize the arm, wait, and ensure the arm is on.
    # ---
    print("Connecting to myCobot280...")

    mc = MyCobot280('/dev/ttyAMA0', 1000000)
    time.sleep(0.5)
    mc.power_on()
    time.sleep(0.5)
    # ---
    
    # TODO: Move arm to initial folded position
    # ---
    home_pos = [0, 45, -90, -45, 0, 0]
    mc.send_angles(home_pos, 50)
    time.sleep(2.0)

    print("Robot ready.")
    # ---

except Exception as e:
    print(f"Robot hardware warning: {e}")
    print("Continuing with OpenCV camera pipeline only...\n")

# ==========================================
# 1. INSPECTION CRITERIA CONFIGURATION
# ==========================================
# ROI Coordinates [y_min, y_max, x_min, x_max] on 640x480 frame
ROI_BOUNDS = [120, 360, 200, 440]

# Acceptable tolerances for passing items
MIN_AREA = 2000       # Minimum contour area (pixels)
MAX_AREA = 6000       # Maximum contour area (pixels)
TARGET_ASPECT = 1.0   # Expected width/height ratio (Square = 1.0)
ASPECT_TOLERANCE = 0.25

# Target Color Range: Green (HSV)
LOWER_GREEN = np.array([35, 70, 70])
UPPER_GREEN = np.array([85, 255, 255])

# ==========================================
# 2. INSPECTION LOGIC FUNCTION
# ==========================================
def inspect_part(roi_frame):
    """
    Analyzes an item within the ROI frame.
    Returns: status (str), reason (str), color_overlay (image)
    """
    hsv = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_GREEN, UPPER_GREEN)
    
    # Noise reduction
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return "FAIL", "No Item / Wrong Color", mask

    # Get largest contour in inspection zone
    largest_contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest_contour)

    # Bounding rectangle and aspect ratio
    x, y, w, h = cv2.boundingRect(largest_contour)
    aspect_ratio = float(w) / h

    # Rule Checks
    if area < MIN_AREA:
        return "FAIL", f"Too Small ({int(area)}px)", mask
    if area > MAX_AREA:
        return "FAIL", f"Too Large ({int(area)}px)", mask
    if abs(aspect_ratio - TARGET_ASPECT) > ASPECT_TOLERANCE:
        return "FAIL", f"Shape Defect (Ratio: {aspect_ratio:.2f})", mask

    return "PASS", f"Good Part ({int(area)}px)", mask

# ==========================================
# 3. MAIN INSPECTION STREAM
# ==========================================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Starting Quality Control Scanner. Press 'q' to quit.")

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        y1, y2, x1, x2 = ROI_BOUNDS
        roi = frame[y1:y2, x1:x2]

        # Run Inspection Algorithm
        status, reason, mask = inspect_part(roi)

        # Visual Feedback Setup
        status_color = (0, 255, 0) if status == "PASS" else (0, 0, 255)
        
        # Draw Inspection Box on Frame
        cv2.rectangle(frame, (x1, y1), (x2, y2), status_color, 2)
        cv2.putText(frame, "INSPECTION ZONE", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)

        # Display Telemetry Banner
        cv2.putText(frame, f"STATUS: {status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, status_color, 3)
        cv2.putText(frame, f"REASON: {reason}", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Show frames
        cv2.imshow("Mission 02 - Project 05: QC Scanner", frame)
        cv2.imshow("Mask View", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()