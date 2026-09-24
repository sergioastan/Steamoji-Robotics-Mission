import cv2
import mediapipe as mp
import math
import time
import numpy as np
from pymycobot.mycobot280 import MyCobot280

# ==========================================
# 1. HARDWARE & WORKSPACE INITIALIZATION
# ==========================================
# Initialize myCobot (Default Pi serial port)

mc = MyCobot('/dev/ttyAMA0', 1000000)
time.sleep(0.5)

# Safety workspace limits in millimeters (myCobot 280)
X_MIN, X_MAX = 130, 250   # Forward / Backward range
Y_MIN, Y_MAX = -160, 160  # Left / Right range
Z_HEIGHT = 180            # Fixed height above surface (mm)
ARM_SPEED = 50            # Movement speed (1-100)

# ==========================================
# 2. MEDIAPIPE & CAMERA SETUP
# ==========================================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Rate-limiting variables (prevents overloading serial commands)
last_command_time = 0
COMMAND_INTERVAL = 0.15  # Send move command every 150ms

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def map_value(value, in_min, in_max, out_min, out_max):
    """Maps a value from one range to another and clamps it."""
    clamped_val = max(in_min, min(in_max, value))
    return out_min + (clamped_val - in_min) * (out_max - out_min) / (in_max - in_min)

def calculate_distance(p1, p2):
    """Calculates 2D Euclidean distance between two MediaPipe landmarks."""
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

# ==========================================
# 4. MAIN CONTROL LOOP
# ==========================================
print("Starting Hand Control. Press 'q' to exit.")

try:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        # Flip horizontally for intuitive mirror view
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand skeleton on camera view
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Extract key landmarks
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

                # --- STEP A: MAP FINGER POSITION TO ROBOT COORDINATES ---
                # Screen coordinates are normalized 0.0 - 1.0
                robot_x = map_value(index_tip.y, 0.2, 0.8, X_MAX, X_MIN)  # Vertical hand position -> Robot Forward/Back
                robot_y = map_value(index_tip.x, 0.2, 0.8, Y_MIN, Y_MAX)  # Horizontal hand position -> Robot Left/Right

                # --- STEP B: GESTURE DETECTION (PINCH) ---
                pinch_distance = calculate_distance(thumb_tip, index_tip)
                is_pinching = pinch_distance < 0.08  # Threshold for closed pinch

                # --- STEP C: EXECUTE ROBOT COMMANDS (RATE-LIMITED) ---
                current_time = time.time()
                if current_time - last_command_time > COMMAND_INTERVAL:
                    # Send position command: [X, Y, Z, Rx, Ry, Rz]
                    mc.send_coords([robot_x, robot_y, Z_HEIGHT, -180, 0, 0], ARM_SPEED, 1)

                    # Control end-effector based on pinch state
                    if is_pinching:
                        mc.set_gripper_state(1, 80) # Close gripper / activate pump
                        status_text = "Pinch Active (GRIP)"
                    else:
                        mc.set_gripper_state(0, 80) # Open gripper / deactivate pump
                        status_text = "Tracking (OPEN)"

                    last_command_time = current_time

                # --- STEP D: ON-SCREEN TELEMETRY DISPLAY ---
                cx, cy = int(index_tip.x * w), int(index_tip.y * h)
                cv2.circle(frame, (cx, cy), 10, (0, 255, 0) if not is_pinching else (0, 0, 255), -1)
                
                telemetry = f"Robot Target -> X: {int(robot_x)}mm | Y: {int(robot_y)}mm"
                cv2.putText(frame, telemetry, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, f"State: {status_text}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if not is_pinching else (0, 0, 255), 2)

        else:
            cv2.putText(frame, "No hand detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Mission 2 - Project 04: Hand Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    mc.release_all_servos()