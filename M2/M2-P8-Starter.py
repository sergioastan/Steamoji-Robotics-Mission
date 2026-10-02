# TODO: Import the cv2, numpy, and time packages from the Python package library
# ---
# 
# ---

# TODO: Import the RPi.GPIO package for pump control
# ---
# 
# ---

# TODO: Import the MyCobot280 package from the pymycobot library
# ---
# 
# ---

global POS_HOME_CARTESIAN

# ==========================================
# 1. HARDWARE & COORDINATE CONFIGURATION
# ==========================================

# TODO: Initialize the robot arm connection and verify it works
# ---
# 
# ---

# TODO: Initialize GPIO pins for the suction pump
# ---
# 
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
# 
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
# 
# ---

# TODO: Define function to parse board state from camera frame
# ---
# 
# ---

# TODO: Define AI logic to find best Tic-Tac-Toe move
# ---
# 
# ---

# TODO: Define function to check for winning conditions
# ---
# 
# ---

# TODO: Define robot pick-and-place sequence for placing tokens
# ---
# 
# ---

# ==========================================
# 3. MAIN GAME LOOP
# ==========================================

# TODO: Initialize camera and start main game loop
# ---
# 
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
# 
# ---
finally:
    cap.release()
    cv2.destroyAllWindows()
    set_pump(0)
    GPIO.cleanup()
    # Don't release servos - keeps arm powered for next run
    # mc.release_all_servos()