import cv2
import numpy as np
import time
from pymycobot.mycobot import MyCobot

# ==========================================
# 1. HARDWARE & WAYPOINT CONFIGURATION
# ==========================================
mc = MyCobot('/dev/ttyAMA0', 115200)
time.sleep(0.5)

SPEED = 40

# Robot Positions [X, Y, Z, Rx, Ry, Rz]
POS_SCAN    = [180, 0, 220, -180, 0, 0]      # Overhead camera view
POS_PICK    = [180, 0, 110, -180, 0, 0]      # Pick height at inspection pad
POS_PASS_BIN = [100, -180, 150, -180, 0, 0]   # Shipping Bin (Right)
POS_FAIL_BIN = [100, 180, 150, -180, 0, 0]    # Reject Bin (Left)

# ROI Bounds on 640x480 frame
ROI_BOUNDS = [120, 360, 200, 440]

# Green Color Limits
LOWER_GREEN = np.array([35, 70, 70])
UPPER_GREEN = np.array([85, 255, 255])

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def set_pump(state):
    """Controls suction pump (1=ON, 0=OFF)."""
    if state == 1:
        mc.set_basic_output(2, 0) # Pump ON
        mc.set_basic_output(5, 0) # Valve closed
    else:
        mc.set_basic_output(2, 1) # Pump OFF
        mc.set_basic_output(5, 1) # Valve release
    time.sleep(0.3)

def inspect_part(roi):
    """Evaluates presence and quality of part in ROI."""
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_GREEN, UPPER_GREEN)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return "NO_ITEM", "Inspection Zone Empty"

    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)

    if area < 2000:
        return "FAIL", f"Defective Size ({int(area)}px)"
    elif area > 6000:
        return "FAIL", f"Over-Sized ({int(area)}px)"
    else:
        return "PASS", f"Quality Approved ({int(area)}px)"

def execute_sorting_routine(status):
    """Executes physical pick-and-sort routine based on inspection status."""
    print(f"--> Executing Sort Routine for status: {status}")
    
    # 1. Lower to pick part
    mc.send_coords(POS_PICK, SPEED, 1)
    time.sleep(2.0)
    
    # 2. Engage suction
    set_pump(1)
    time.sleep(0.5)

    # 3. Lift part back to clearance height
    mc.send_coords(POS_SCAN, SPEED, 1)
    time.sleep(1.5)

    # 4. Route to target bin
    target_bin = POS_PASS_BIN if status == "PASS" else POS_FAIL_BIN
    mc.send_coords(target_bin, SPEED, 1)
    time.sleep(2.5)

    # 5. Release part
    set_pump(0)
    time.sleep(0.5)

    # 6. Return home to scan position
    mc.send_coords(POS_SCAN, SPEED, 1)
    time.sleep(2.0)

# ==========================================
# 3. MAIN AUTOMATION LOOP
# ==========================================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Move robot to scan position initially
mc.send_coords(POS_SCAN, SPEED, 1)
set_pump(0)
time.sleep(2.0)

print("Starting Quality Control Sorting Line. Press 'q' to quit.")

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        y1, y2, x1, x2 = ROI_BOUNDS
        roi = frame[y1:y2, x1:x2]

        status, reason = inspect_part(roi)

        # On-screen display
        color = (0, 255, 0) if status == "PASS" else ((0, 0, 255) if status == "FAIL" else (255, 255, 255))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"STATUS: {status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        cv2.putText(frame, f"REASON: {reason}", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, "Press 's' to Scan & Sort Item | 'q' to Quit", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        cv2.imshow("Mission 02 - Project 06: QC Sort Cell", frame)
        key = cv2.waitKey(1) & 0xFF

        # Trigger physical inspection routine when operator presses 's'
        if key == ord('s'):
            if status in ["PASS", "FAIL"]:
                execute_sorting_routine(status)
            else:
                print("Cannot sort: No valid item detected in zone!")

        elif key == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    set_pump(0)
    mc.release_all_servos()