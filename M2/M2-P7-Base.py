import cv2
import numpy as np

# ==========================================
# 1. GRID CONFIGURATION (3x3 REGION OF INTEREST)
# ==========================================
# Define pixel coordinates for the whole 3x3 board on a 640x480 frame
GRID_X_MIN, GRID_X_MAX = 170, 470
GRID_Y_MIN, GRID_Y_MAX = 90, 390

# Calculate width and height of an individual cell
CELL_W = (GRID_X_MAX - GRID_X_MIN) // 3
CELL_H = (GRID_Y_MAX - GRID_Y_MIN) // 3

# Color Thresholds (HSV)
# Red Tokens = 'X' (Human Player)
LOWER_RED1 = np.array([0, 120, 100])
UPPER_RED1 = np.array([10, 255, 255])
LOWER_RED2 = np.array([170, 120, 100])
UPPER_RED2 = np.array([180, 255, 255])

# Blue Tokens = 'O' (Robot Player)
LOWER_BLUE = np.array([100, 120, 100])
UPPER_BLUE = np.array([130, 255, 255])

# ==========================================
# 2. BOARD PARSING LOGIC
# ==========================================
def scan_cell(cell_roi):
    """Inspects a single cell ROI and returns 'X', 'O', or ' '."""
    hsv = cv2.cvtColor(cell_roi, cv2.COLOR_BGR2HSV)

    # Red Mask (handles HSV wraparound)
    mask_red1 = cv2.inRange(hsv, LOWER_RED1, UPPER_RED1)
    mask_red2 = cv2.inRange(hsv, LOWER_RED2, UPPER_RED2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    # Blue Mask
    mask_blue = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)

    red_pixels = cv2.countNonZero(mask_red)
    blue_pixels = cv2.countNonZero(mask_blue)

    # Threshold for token detection (adjust based on cell size)
    MIN_PIXELS = 800

    if red_pixels > MIN_PIXELS and red_pixels > blue_pixels:
        return 'X'
    elif blue_pixels > MIN_PIXELS and blue_pixels > red_pixels:
        return 'O'
    return ' '

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

# ==========================================
# 3. MAIN DISPLAY LOOP
# ==========================================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Starting Tic-Tac-Toe Vision Scanner. Press 'q' to quit.")

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        board_state = parse_board_state(frame)

        # Draw Grid & Telemetry Overlay
        for row in range(3):
            for col in range(3):
                x1 = GRID_X_MIN + col * CELL_W
                y1 = GRID_Y_MIN + row * CELL_H
                x2 = x1 + CELL_W
                y2 = y1 + CELL_H

                token = board_state[row][col]
                color = (0, 0, 255) if token == 'X' else ((255, 0, 0) if token == 'O' else (200, 200, 200))

                # Draw Cell Border
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
                
                # Draw Token Text centered in cell
                if token != ' ':
                    cv2.putText(frame, token, (x1 + CELL_W // 3, y1 + 2 * CELL_H // 3),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

        # Telemetry Display
        cv2.putText(frame, "Tic-Tac-Toe Vision Parser", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.imshow("Mission 02 - Project 07: Board State Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()