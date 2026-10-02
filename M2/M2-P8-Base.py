# TODO: Import the cv2, numpy, and time packages from the Python package library
# ---
import cv2
import numpy as np
import time
# ---

# TODO: Import the RPi.GPIO package for pump control
# ---
import RPi.GPIO as GPIO
# ---

# TODO: Import the MyCobot280 package from the pymycobot library
# ---
from pymycobot.mycobot280 import MyCobot280
# ---

global POS_HOME_CARTESIAN

# ==========================================
# 1. HARDWARE & COORDINATE CONFIGURATION
# ==========================================

# TODO: Initialize the robot arm connection and verify it works
# ---
mc = MyCobot280('/dev/ttyAMA0', 1000000)
time.sleep(0.5)

# Verify connection (M1 style - no explicit power_on)
try:
    angles = mc.get_angles()
    print(f"Connected. Current angles: {angles}")
except Exception as e:
    print(f"Warning during init: {e}")
    import traceback
    traceback.print_exc()
# ---

# TODO: Initialize GPIO pins for the suction pump
# ---
# GPIO Pump Setup (from M1/Project-08-Base.py)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.output(20, 1)  # Off initially
GPIO.output(21, 1)
# ---

ARM_SPEED = 40

# Rest/Home Position for Camera Scan (joint angles)
POS_HOME_ANGLES = [0, 45, -90, -45, 0, 0]

# Supply Rack where 'O' tokens are waiting to be picked (Cartesian)
POS_TOKEN_SUPPLY_BASE = [94, 180, 117, 180, 0, -45]  # Z=117 for first token
POS_TOKEN_HOVER  = [94, 180, 130, 180, 0, -45]
TOKEN_HEIGHT = 5  # mm per token
tokens_picked = 0

# We'll compute POS_HOME_CARTESIAN after moving to home angles
POS_HOME_CARTESIAN = None

# TODO: Move robot arm to initial home position for camera scanning
# ---
# Move robot to overhead home scan position using joint angles (like M1)
print(f"Moving to home angles: {POS_HOME_ANGLES}")
try:
    print("  Sending send_angles command...")
    result = mc.send_angles(POS_HOME_ANGLES, ARM_SPEED)
    print(f"  send_angles returned: {result}")
    time.sleep(4.0)
    # Capture Cartesian position for return moves
    POS_HOME_CARTESIAN = mc.get_coords()
    print(f"Home position (cartesian): {POS_HOME_CARTESIAN}")
    angles_after = mc.get_angles()
    print(f"Angles after move: {angles_after}")
except Exception as e:
    print(f"Error moving to home: {e}")
    import traceback
    traceback.print_exc()
    POS_HOME_CARTESIAN = [66, -62, 235, 180, 0, 90]  # fallback
set_pump(0)
time.sleep(1.0)
# ---

# ==========================================
# BOARD CELL COORDINATES (hard-coded per cell [X, Y, Z, Rx, Ry, Rz])
# ==========================================
CELL_COORDS = {
    (0, 0): [120.5, -61.5, 138.4, 163.03, 8.84, -61.76], (0, 1): [124.3, -1.7, 123.0, 163.55, 10.06, -50.49], (0, 2): [125.9, 63.8, 96.0, 156.12, 12.49, -21.5],
    (1, 0): [149.8, -48.8, 85.0, 176.56, -3.67, -105.71], (1, 1): [150.5, -2.9, 84.6, 176.45, -2.52, -93.23], (1, 2): [148.4, 42.6, 82.7, 175.27, -4.47, -73.44],
    (2, 0): [193.2, -49.9, 84.2, 174.22, -3.0, -112.6], (2, 1): [193.5, -6.8, 77.8, 176.9, -1.27, -98.32], (2, 2): [189.0, 46.0, 77.5, 177.55, -3.27, -84.59],
}

# ==========================================
# VISION CALIBRATION SETTINGS (match M2-P7-Base.py)
# ==========================================
GRID_SCALE = 0.75       # Scale factor for grid size (1.0 = original)
GRID_OFFSET_X = -10     # Horizontal offset in pixels (+X = right)
GRID_OFFSET_Y = -70     # Vertical offset in pixels (+Y = down)

# Base pixel coordinates for the whole 3x3 board on a 640x480 frame
_BASE_GRID_X_MIN, _BASE_GRID_X_MAX = 170, 470
_BASE_GRID_Y_MIN, _BASE_GRID_Y_MAX = 90, 390

# Apply scale and offset (centered scaling)
grid_w = (_BASE_GRID_X_MAX - _BASE_GRID_X_MIN) * GRID_SCALE
grid_h = (_BASE_GRID_Y_MAX - _BASE_GRID_Y_MIN) * GRID_SCALE
center_x = (_BASE_GRID_X_MIN + _BASE_GRID_X_MAX) / 2
center_y = (_BASE_GRID_Y_MIN + _BASE_GRID_Y_MAX) / 2

GRID_X_MIN = int(center_x - grid_w / 2 + GRID_OFFSET_X)
GRID_X_MAX = int(center_x + grid_w / 2 + GRID_OFFSET_X)
GRID_Y_MIN = int(center_y - grid_h / 2 + GRID_OFFSET_Y)
GRID_Y_MAX = int(center_y + grid_h / 2 + GRID_OFFSET_Y)

CELL_W = (GRID_X_MAX - GRID_X_MIN) // 3
CELL_H = (GRID_Y_MAX - GRID_Y_MIN) // 3

# Red Tokens = 'O' (Robot Player) - HSV wraps at 0/180
LOWER_RED1 = np.array([0, 120, 100]); UPPER_RED1 = np.array([10, 255, 255])
LOWER_RED2 = np.array([170, 120, 100]); UPPER_RED2 = np.array([180, 255, 255])

# Green Tokens = 'X' (Human Player)
LOWER_GREEN = np.array([40, 80, 80]); UPPER_GREEN = np.array([85, 255, 255])

# ==========================================
# 2. HELPER & GAME LOGIC FUNCTIONS
# ==========================================

# TODO: Define pump control function for suction
# ---
def set_pump(state):
    """Controls suction pump via GPIO (1=ON, 0=OFF). Active LOW."""
    if state == 1:
        GPIO.output(20, 0)
        GPIO.output(21, 0)
    else:
        GPIO.output(20, 1)
        GPIO.output(21, 1)
    time.sleep(0.3)
# ---

# TODO: Define function to parse board state from camera frame
# ---
def parse_board_state(frame):
    """Scans all 9 cells and returns 3x3 matrix."""
    board = [[' ' for _ in range(3)] for _ in range(3)]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for r in range(3):
        for c in range(3):
            x1 = GRID_X_MIN + c * CELL_W
            y1 = GRID_Y_MIN + r * CELL_H
            roi = hsv[y1:y1+CELL_H, x1:x1+CELL_W]

            m_red = cv2.bitwise_or(cv2.inRange(roi, LOWER_RED1, UPPER_RED1), cv2.inRange(roi, LOWER_RED2, UPPER_RED2))
            m_green = cv2.inRange(roi, LOWER_GREEN, UPPER_GREEN)

            r_pix, g_pix = cv2.countNonZero(m_red), cv2.countNonZero(m_green)
            if g_pix > 800 and g_pix > r_pix:
                board[r][c] = 'X'
            elif r_pix > 800 and r_pix > g_pix:
                board[r][c] = 'O'
    return board
# ---

# TODO: Define AI logic to find best Tic-Tac-Toe move
# ---
def find_best_move(board):
    """Calculates AI move: Checks for win, block, or picks first empty space."""
    # 1. Check if AI can win immediately or needs to block Human
    for player in ['O', 'X']:
        for r in range(3):
            for c in range(3):
                if board[r][c] == ' ':
                    board[r][c] = player
                    if check_winner(board) == player:
                        return (r, c)
                    board[r][c] = ' ' # Undo

    # 2. Center priority
    if board[1][1] == ' ':
        return (1, 1)

    # 3. Pick first open square
    for r in range(3):
        for c in range(3):
            if board[r][c] == ' ':
                return (r, c)
    return None
# ---

# TODO: Define function to check for winning conditions
# ---
def check_winner(b):
    """Checks for 3-in-a-row winning conditions."""
    for i in range(3):
        if b[i][0] == b[i][1] == b[i][2] != ' ': return b[i][0]
        if b[0][i] == b[1][i] == b[2][i] != ' ': return b[0][i]
    if b[0][0] == b[1][1] == b[2][2] != ' ': return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != ' ': return b[0][2]
    return None
# ---

# TODO: Define robot pick-and-place sequence for placing tokens
# ---
def execute_robot_move(target_cell):
    """Executes pick-and-place sequence to place an 'O' token at target grid cell."""
    global POS_HOME_CARTESIAN, tokens_picked
    row, col = target_cell
    target_coords = CELL_COORDS[(row, col)]
    target_x, target_y, target_z = target_coords[0], target_coords[1], target_coords[2]
    target_rx, target_ry, target_rz = target_coords[3], target_coords[4], target_coords[5]
    print(f"--> myCobot placing 'O' token at Grid Cell ({row}, {col}) -> coords ({target_x}, {target_y}, {target_z}, {target_rx}, {target_ry}, {target_rz})")

    # Calculate supply position with offset for tokens already picked
    supply_z = POS_TOKEN_SUPPLY_BASE[2] - (tokens_picked * TOKEN_HEIGHT)
    pos_token_supply = POS_TOKEN_SUPPLY_BASE.copy()
    pos_token_supply[2] = supply_z
    print(f"  Token #{tokens_picked + 1}: supply Z = {supply_z}mm")

    # 1. Pick up token from supply rack
    print("  Moving to token hover...")
    mc.send_coords(POS_TOKEN_HOVER, ARM_SPEED, 0)
    time.sleep(3.0)
    print("  Moving to token supply...")
    mc.send_coords(pos_token_supply, ARM_SPEED, 0)
    time.sleep(2.5)
    print("  Pump ON")
    set_pump(1)
    time.sleep(1.0)
    print("  Moving back to hover...")
    mc.send_coords(POS_TOKEN_HOVER, ARM_SPEED, 0)
    time.sleep(2.5)

    tokens_picked += 1

    # 2. Hover over target cell (higher Z, same orientation)
    target_hover = [target_x, target_y, 150, target_rx, target_ry, target_rz]
    print(f"  Moving to target hover: {target_hover}")
    mc.send_coords(target_hover, ARM_SPEED, 0)
    time.sleep(3.0)

    # 3. Lower and release token (same orientation)
    target_place = [target_x, target_y, target_z, target_rx, target_ry, target_rz]
    print(f"  Moving to target place: {target_place}")
    mc.send_coords(target_place, ARM_SPEED, 0)
    time.sleep(1.5)
    print("  Pump OFF")
    set_pump(0)
    time.sleep(1.0)

    # 4. Return home to scan position
    print("  Returning home...")
    mc.send_coords(POS_HOME_CARTESIAN, ARM_SPEED, 0)
    time.sleep(3.0)
# ---

# ==========================================
# 3. MAIN GAME LOOP
# ==========================================

# TODO: Initialize camera and start main game loop
# ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# ---

# Move robot to overhead home scan position using joint angles (like M1)
print(f"Moving to home angles: {POS_HOME_ANGLES}")
try:
    print("  Sending send_angles command...")
    result = mc.send_angles(POS_HOME_ANGLES, ARM_SPEED)
    print(f"  send_angles returned: {result}")
    time.sleep(4.0)
    # Capture Cartesian position for return moves
    POS_HOME_CARTESIAN = mc.get_coords()
    print(f"Home position (cartesian): {POS_HOME_CARTESIAN}")
    angles_after = mc.get_angles()
    print(f"Angles after move: {angles_after}")
except Exception as e:
    print(f"Error moving to home: {e}")
    import traceback
    traceback.print_exc()
    POS_HOME_CARTESIAN = [66, -62, 235, 180, 0, 90]  # fallback
set_pump(0)
time.sleep(1.0)

print("Starting Physical Tic-Tac-Toe Game Cell.")
print("Place an 'X' on the grid, then press 'space' to trigger myCobot's turn!")

# TODO: Main game loop - read frames, detect board, handle robot moves
# ---
try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        board = parse_board_state(frame)
        winner = check_winner(board)

        # Draw grid overlay
        for r in range(3):
            for c in range(3):
                x1 = GRID_X_MIN + c * CELL_W
                y1 = GRID_Y_MIN + r * CELL_H
                cv2.rectangle(frame, (x1, y1), (x1 + CELL_W, y1 + CELL_H), (255, 255, 255), 2)
                token = board[r][c]
                if token != ' ':
                    color = (0, 255, 0) if token == 'X' else (0, 0, 255)
                    cv2.putText(frame, token, (x1 + 30, y1 + 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

        # Status text
        if winner:
            cv2.putText(frame, f"GAME OVER! Winner: {winner}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Press SPACE to trigger Robot Move | 'q' to Quit", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        cv2.imshow("Mission 02 Capstone - Tic-Tac-Toe AI", frame)
        key = cv2.waitKey(1) & 0xFF

        if key != 255:
            print(f"Key pressed: {key} ({chr(key) if key < 128 else '?'})")

        if key == ord(' ') and not winner:
            print("SPACE pressed - calculating move...")
            move = find_best_move(board)
            if move:
                print(f"Best move: {move}")
                execute_robot_move(move)
            else:
                print("Game is a Draw!")

        elif key == ord('q'):
            break

# ---
finally:
    cap.release()
    cv2.destroyAllWindows()
    set_pump(0)
    GPIO.cleanup()
    # Don't release servos - keeps arm powered for next run
    # mc.release_all_servos()