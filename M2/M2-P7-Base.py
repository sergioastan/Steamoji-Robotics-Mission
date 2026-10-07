# TODO: Import the cv2, numpy, and time packages from the Python package library
# ---
import cv2
import numpy as np
import time
# ---

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
# 1. GRID CONFIGURATION (3x3 REGION OF INTEREST)
# ==========================================
# Vision calibration settings
GRID_SCALE = 0.75       # Scale factor for grid size (1.0 = original)
GRID_OFFSET_X = -10      # Horizontal offset in pixels (+X = right)
GRID_OFFSET_Y = -70      # Vertical offset in pixels (+Y = down)

# Base pixel coordinates for the whole 3x3 board on a 640x480 frame
_BASE_GRID_X_MIN, _BASE_GRID_X_MAX = 170, 470
_BASE_GRID_Y_MIN, _BASE_GRID_Y_MAX = 90, 390

# TODO: Calculate scaled and offset grid bounds
# ---
# Apply scale and offset
grid_w = (_BASE_GRID_X_MAX - _BASE_GRID_X_MIN) * GRID_SCALE
grid_h = (_BASE_GRID_Y_MAX - _BASE_GRID_Y_MIN) * GRID_SCALE
center_x = (_BASE_GRID_X_MIN + _BASE_GRID_X_MAX) / 2
center_y = (_BASE_GRID_Y_MIN + _BASE_GRID_Y_MAX) / 2

GRID_X_MIN = int(center_x - grid_w / 2 + GRID_OFFSET_X)
GRID_X_MAX = int(center_x + grid_w / 2 + GRID_OFFSET_X)
GRID_Y_MIN = int(center_y - grid_h / 2 + GRID_OFFSET_Y)
GRID_Y_MAX = int(center_y + grid_h / 2 + GRID_OFFSET_Y)
# ---

# TODO: Calculate individual cell width and height
# ---
# Calculate width and height of an individual cell
CELL_W = (GRID_X_MAX - GRID_X_MIN) // 3
CELL_H = (GRID_Y_MAX - GRID_Y_MIN) // 3
# ---

# Color Thresholds (HSV)
# Red Tokens = 'X' (Human Player)
LOWER_RED1 = np.array([0, 120, 100])
UPPER_RED1 = np.array([10, 255, 255])
LOWER_RED2 = np.array([170, 120, 100])
UPPER_RED2 = np.array([180, 255, 255])

# Blue Tokens = 'O' (Robot Player)
LOWER_BLUE = np.array([90, 120, 100])
UPPER_BLUE = np.array([130, 255, 255])

# ==========================================
# 2. BOARD PARSING LOGIC
# ==========================================

# TODO: Define function to scan a single cell for token detection
# ---
def scan_cell(cell_roi):
    """Inspects a single cell ROI and returns 'X', 'O', or ' '."""
    # TODO: Convert cell ROI to HSV color space
    # ---
    hsv = cv2.cvtColor(cell_roi, cv2.COLOR_BGR2HSV)
    # ---

    # TODO: Create red color mask (handles HSV wraparound at 0/180)
    # ---
    # Red Mask (handles HSV wraparound)
    mask_red1 = cv2.inRange(hsv, LOWER_RED1, UPPER_RED1)
    mask_red2 = cv2.inRange(hsv, LOWER_RED2, UPPER_RED2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    # ---

    # TODO: Create blue color mask
    # ---
    # Blue Mask
    mask_blue = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
    # ---

    # TODO: Count non-zero pixels for each color
    # ---
    red_pixels = cv2.countNonZero(mask_red)
    blue_pixels = cv2.countNonZero(mask_blue)
    # ---

    # Threshold for token detection (adjust based on cell size)
    MIN_PIXELS = 800

    # TODO: Determine token type based on pixel counts
    # ---
    if red_pixels > MIN_PIXELS and red_pixels > blue_pixels:
        return 'X'
    elif blue_pixels > MIN_PIXELS and blue_pixels > red_pixels:
        return 'O'
    return ' '
    # ---
# ---


# TODO: Define function to parse full 3x3 board state
# ---
def parse_board_state(frame):
    """Scans all 9 grid cells and returns a 3x3 matrix."""
    board = [[' ' for _ in range(3)] for _ in range(3)]

    for row in range(3):
        for col in range(3):
            # Calculate pixel bounds for current cell
            x1 = GRID_X_MIN + col * CELL_W
            y1 = GRID_Y_MIN + row * CELL_H
            x2 = x1 + CELL_W
            y2 = y1 + CELL_H

            cell_roi = frame[y1:y2, x1:x2]
            board[row][col] = scan_cell(cell_roi)

    return board
# ---

# ==========================================
# 3. MAIN DISPLAY LOOP
# ==========================================

# TODO: Initialize camera capture
# ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# ---

print("Starting Tic-Tac-Toe Vision Scanner. Press 'q' to quit.")

# TODO: Run main vision loop
# ---
try:
    while cap.isOpened():
        # TODO: Read frame from camera
        # ---
        ret, frame = cap.read()
        if not ret:
            break
        # ---

        # TODO: Parse board state from frame
        # ---
        board_state = parse_board_state(frame)
        # ---

        # Draw Grid & Telemetry Overlay
        for row in range(3):
            for col in range(3):
                x1 = GRID_X_MIN + col * CELL_W
                y1 = GRID_Y_MIN + row * CELL_H
                x2 = x1 + CELL_W
                y2 = y1 + CELL_H

                token = board_state[row][col]
                color = (0, 0, 255) if token == 'X' else ((255, 0, 0) if token == 'O' else (200, 200, 200))

                # TODO: Draw cell border
                # ---
                # Draw Cell Border
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
                # ---
                
                # TODO: Draw token text if present
                # ---
                # Draw Token Text centered in cell
                if token != ' ':
                    cv2.putText(frame, token, (x1 + CELL_W // 3, y1 + 2 * CELL_H // 3),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
                # ---

        # TODO: Draw telemetry text
        # ---
        # Telemetry Display
        cv2.putText(frame, "Tic-Tac-Toe Vision Parser", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        # ---

        # TODO: Display the frame
        # ---
        cv2.imshow("Mission 02 - Project 07: Board State Scanner", frame)
        # ---

        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
# ---