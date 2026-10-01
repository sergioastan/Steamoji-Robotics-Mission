import cv2
import numpy as np
import time
from pymycobot.mycobot import MyCobot

# ==========================================
# 1. HARDWARE & COORDINATE CONFIGURATION
# ==========================================
mc = MyCobot('/dev/ttyAMA0', 1000000)
time.sleep(0.5)

ARM_SPEED = 40

# Rest/Home Position for Camera Scan
POS_HOME = [66, -62, 235, 180, 0, 90]

# Supply Rack where 'O' tokens are waiting to be picked
POS_TOKEN_SUPPLY = [120, -180, 110, -180, 0, 0]
POS_TOKEN_HOVER  = [120, -180, 200, -180, 0, 0]

# ==========================================
# BOARD CALIBRATION SETTINGS
# ==========================================
BOARD_SCALE = 1.0      # Scale factor for board size (1.0 = original, 0.8 = 80% size)
BOARD_OFFSET_X = 0.0   # Offset in arm's +X direction (mm)
BOARD_OFFSET_Y = 0.0   # Offset in arm's +Y direction (mm)

# Base coordinates (unscaled, unoffset)
_BASE_CELL_COORDS = {
    (0, 0): [220, -60], (0, 1): [220, 0], (0, 2): [220, 60],
    (1, 0): [180, -60], (1, 1): [180, 0], (1, 2): [180, 60],
    (2, 0): [140, -60], (2, 1): [140, 0], (2, 2): [140, 60]
}

# Apply scale and offset
CELL_COORDS = {}
for (r, c), (x, y) in _BASE_CELL_COORDS.items():
    CELL_COORDS[(r, c)] = [
        x * BOARD_SCALE + BOARD_OFFSET_X,
        y * BOARD_SCALE + BOARD_OFFSET_Y
    ]

Z_PLACE_HEIGHT = 110

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

LOWER_RED1 = np.array([0, 120, 100]); UPPER_RED1 = np.array([10, 255, 255])
LOWER_RED2 = np.array([170, 120, 100]); UPPER_RED2 = np.array([180, 255, 255])
LOWER_BLUE = np.array([100, 120, 100]); UPPER_BLUE = np.array([130, 255, 255])

# ==========================================
# 2. HELPER & GAME LOGIC FUNCTIONS
# ==========================================
def set_pump(state):
    """Controls suction pump (1=ON, 0=OFF)."""
    if state == 1:
        mc.set_basic_output(2, 0)
        mc.set_basic_output(5, 0)
    else:
        mc.set_basic_output(2, 1)
        mc.set_basic_output(5, 1)
    time.sleep(0.3)

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
            m_blue = cv2.inRange(roi, LOWER_BLUE, UPPER_BLUE)

            r_pix, b_pix = cv2.countNonZero(m_red), cv2.countNonZero(m_blue)
            if r_pix > 800 and r_pix > b_pix:
                board[r][c] = 'X'
            elif b_pix > 800 and b_pix > r_pix:
                board[r][c] = 'O'
    return board

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

def check_winner(b):
    """Checks for 3-in-a-row winning conditions."""
    for i in range(3):
        if b[i][0] == b[i][1] == b[i][2] != ' ': return b[i][0]
        if b[0][i] == b[1][i] == b[2][i] != ' ': return b[0][i]
    if b[0][0] == b[1][1] == b[2][2] != ' ': return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != ' ': return b[0][2]
    return None

def execute_robot_move(target_cell):
    """Executes pick-and-place sequence to place an 'O' token at target grid cell."""
    row, col = target_cell
    target_x, target_y = CELL_COORDS[(row, col)]
    print(f"--> myCobot placing 'O' token at Grid Cell ({row}, {col})")

    # 1. Pick up token from supply rack
    mc.send_coords(POS_TOKEN_HOVER, ARM_SPEED, 1)
    time.sleep(2.0)
    mc.send_coords(POS_TOKEN_SUPPLY, ARM_SPEED, 1)
    time.sleep(1.5)
    set_pump(1)
    time.sleep(0.5)
    mc.send_coords(POS_TOKEN_HOVER, ARM_SPEED, 1)
    time.sleep(1.5)

    # 2. Hover over target cell
    mc.send_coords([target_x, target_y, 180, -180, 0, 0], ARM_SPEED, 1)
    time.sleep(2.0)

    # 3. Lower and release token
    mc.send_coords([target_x, target_y, Z_PLACE_HEIGHT, -180, 0, 0], ARM_SPEED, 1)
    time.sleep(1.0)
    set_pump(0)
    time.sleep(0.5)

    # 4. Return home to scan position
    mc.send_coords(POS_HOME, ARM_SPEED, 1)
    time.sleep(2.0)

# ==========================================
# 3. MAIN GAME LOOP
# ==========================================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Move robot to overhead home scan position
mc.send_coords(POS_HOME, ARM_SPEED, 1)
set_pump(0)
time.sleep(2.0)

print("Starting Physical Tic-Tac-Toe Game Cell.")
print("Place an 'X' on the grid, then press 'space' to trigger myCobot's turn!")

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
                    color = (0, 0, 255) if token == 'X' else (255, 0, 0)
                    cv2.putText(frame, token, (x1 + 30, y1 + 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

        # Status text
        if winner:
            cv2.putText(frame, f"GAME OVER! Winner: {winner}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Press SPACE to trigger Robot Move | 'q' to Quit", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        cv2.imshow("Mission 02 Capstone - Tic-Tac-Toe AI", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' ') and not winner:
            move = find_best_move(board)
            if move:
                execute_robot_move(move)
            else:
                print("Game is a Draw!")

        elif key == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    set_pump(0)
    mc.release_all_servos()