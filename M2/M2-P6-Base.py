# TODO: Import the cv2, mediapipe, numpy, time, random, and threading packages
# ---
import cv2
import mediapipe as mp
import numpy as np
import time
import random
import threading
# ---

# TODO: Import the MyCobot280 package from the pymycobot library
# ---
from pymycobot.mycobot280 import MyCobot280
# ---

# =====================================================================
# 1. ROBOT INITIALIZATION
# =====================================================================

# The robot handle. None means "no arm", and every use of it below is
# guarded, so the gesture game still runs on a machine with no robot.
mc = None

# Home pose. Used at startup and again at the end of every round, so it
# lives at module level rather than inside the try block below.
home_pos = [0, 0, 0, 0, 0, 0]

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
    mc.send_angles(home_pos, 50)
    time.sleep(2.0)

    print("Robot ready.")
    # ---

except Exception as e:
    mc = None
    print(f"Robot hardware warning: {e}")
    print("Continuing without the robot. Gestures are still detected and scored.\n")


# ==========================================
# 2. GAME CONFIGURATION & POSES
# ==========================================

ARM_SPEED = 50

# Robot poses for each gesture [X, Y, Z, Rx, Ry, Rz]
# Rock = fist closed, Paper = flat hand, Scissors = two fingers
POSE_ROCK     = [180, 0, 150, -180, 0, 0]   # Fist forward
POSE_PAPER    = [180, 0, 150, -180, 0, 90]  # Flat hand forward  
POSE_SCISSORS = [180, 0, 150, -180, 0, 45]  # Two fingers forward

# Gripper states for each gesture
GRIP_ROCK     = 1   # Closed
GRIP_PAPER    = 0   # Open
GRIP_SCISSORS = 0   # Open (two fingers simulated)

# Game state
player_score = 0
robot_score = 0
rounds_played = 0
last_robot_move = None
game_result = "Make a gesture!"

# A gesture must be held this long before it counts as a round. Without
# this, a single noisy frame triggers a 4.5 second arm movement.
GESTURE_HOLD_TIME = 1.0  # seconds
hold_gesture = None
hold_start = 0.0

# How long a verdict stays on screen before it is cleared
RESULT_DISPLAY_TIME = 2.0  # seconds
last_result_time = 0.0

# Gesture labels
GESTURES = ["Rock", "Paper", "Scissors"]
GESTURE_IDX = {"Rock": 0, "Paper": 1, "Scissors": 2}

# Win logic: (player, robot) -> result
# 0=Rock, 1=Paper, 2=Scissors
# Rock(0) beats Scissors(2), Paper(1) beats Rock(0), Scissors(2) beats Paper(1)
WIN_MAP = {
    (0, 2): "PLAYER", (2, 0): "ROBOT",  # Rock > Scissors
    (1, 0): "PLAYER", (0, 1): "ROBOT",  # Paper > Rock
    (2, 1): "PLAYER", (1, 2): "ROBOT",  # Scissors > Paper
}


# =====================================================================
# 2. THREADED CAMERA PIPELINE (Eliminates frame buffer latency)
# =====================================================================
class ThreadedCamera:
    """Asynchronous camera reader thread to eliminate V4L2 frame buffer latency."""
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # Reduce buffer size to minimize latency
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.lock = threading.Lock()
        self.running = True
        self.ret, self.frame = self.cap.read()

        # Start background thread to continually pull frames from the V4L2 buffer
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    with self.lock:
                        self.ret = ret
                        self.frame = frame
            time.sleep(0.005)  # Prevents high CPU usage on dedicated thread execution

    def read(self):
        with self.lock:
            if self.frame is None:
                return False, None
            return self.ret, self.frame.copy()

    def isOpened(self):
        return self.cap.isOpened()

    def release(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=0.5)
        if self.cap.isOpened():
            self.cap.release()


# ==========================================
# 3. MEDIAPIPE HAND SETUP
# ==========================================

# TODO: Initialize MediaPipe Hands solution
# ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
# ---

# TODO: Initialize threaded camera
# ---
cap = ThreadedCamera(0)
# ---

# Cooldown to prevent rapid re-triggering
last_game_time = 0
GAME_COOLDOWN = 2.0  # seconds


# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================

# TODO: Define function to count extended fingers from hand landmarks
# ---
def count_fingers(hand_landmarks):
    """
    Count extended fingers using MediaPipe landmarks.
    Returns: number of extended fingers (0-5)
    """
    tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
    pips = [3, 6, 10, 14, 18]  # Corresponding PIP joints
    
    extended = 0
    
    # Thumb: compare x-coordinates (horizontal)
    if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[pips[0]].x:
        extended += 1
    
    # Other 4 fingers: compare y-coordinates (vertical, tip above pip = extended)
    for i in range(1, 5):
        if hand_landmarks.landmark[tips[i]].y < hand_landmarks.landmark[pips[i]].y:
            extended += 1
            
    return extended
# ---


# TODO: Define function to classify gesture based on finger count
# ---
def classify_gesture(finger_count):
    """
    Classify gesture based on finger count.
    Returns: "Rock", "Paper", "Scissors", or "Unknown"
    """
    # 0 fingers (fist) = Rock
    # 5 fingers (open hand) = Paper  
    # 2 fingers (index + middle) = Scissors
    # Anything else = Unknown
    if finger_count == 0:
        return "Rock"
    elif finger_count == 5:
        return "Paper"
    elif finger_count == 2:
        return "Scissors"
    else:
        return "Unknown"
# ---


# TODO: Define function for robot to randomly choose a move
# ---
def get_robot_move():
    """
    Robot randomly chooses Rock, Paper, or Scissors.
    Returns: gesture string
    """
    return random.choice(GESTURES)
# ---


# TODO: Define function to determine round winner
# ---
def determine_winner(player_move, robot_move):
    """
    Determine round winner.
    Returns: "PLAYER", "ROBOT", or "DRAW"
    """
    if player_move == robot_move:
        return "DRAW"
    
    p_idx = GESTURE_IDX[player_move]
    r_idx = GESTURE_IDX[robot_move]
    
    return WIN_MAP.get((p_idx, r_idx), "DRAW")
# ---


# TODO: Define function to execute robot gesture movement
# ---
def execute_robot_gesture(gesture):
    """
    Move robot to show the chosen gesture.
    """
    global last_robot_move
    
    # Record the move first, so the on-screen label is right even when
    # there is no arm to move.
    last_robot_move = gesture
    
    # No arm attached: the gesture is still recorded and scored, it just
    # is not performed. This is what lets the game run without hardware.
    if mc is None:
        return
    
    if gesture == "Rock":
        pose = POSE_ROCK
        grip = GRIP_ROCK
    elif gesture == "Paper":
        pose = POSE_PAPER
        grip = GRIP_PAPER
    else:  # Scissors
        pose = POSE_SCISSORS
        grip = GRIP_SCISSORS
    
    # Move to gesture pose
    mc.send_coords(pose, ARM_SPEED, 1)
    time.sleep(1.5)
    
    # Set gripper
    mc.set_gripper_state(grip, 80)
    time.sleep(0.5)
    
    # Hold pose briefly for player to see
    time.sleep(1.0)
    
    # Return to home
    mc.send_angles(home_pos, ARM_SPEED)
    time.sleep(1.5)
# ---


# TODO: Define function to draw game UI on frame
# ---
def draw_ui(frame, player_gesture, robot_gesture, result, finger_count):
    """
    Draw game UI on frame.
    """
    h, w = frame.shape[:2]
    
    # Title
    cv2.putText(frame, "Rock Paper Scissors!", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    
    # Score
    score_text = f"Player: {player_score}  |  Robot: {robot_score}  |  Round: {rounds_played}"
    cv2.putText(frame, score_text, (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    # Player gesture detection
    if player_gesture != "Unknown":
        cv2.putText(frame, f"Your Move: {player_gesture}", (20, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    else:
        cv2.putText(frame, f"Fingers: {finger_count} - Make a clear gesture!", (20, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Robot gesture
    if robot_gesture:
        cv2.putText(frame, f"Robot Move: {robot_gesture}", (20, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    
    # Result
    if result == "PLAYER":
        color = (0, 255, 0)
        text = "YOU WIN!"
    elif result == "ROBOT":
        color = (0, 0, 255)
        text = "ROBOT WINS!"
    elif result == "DRAW":
        color = (255, 255, 0)
        text = "DRAW!"
    else:
        color = (255, 255, 255)
        text = game_result
    
    cv2.putText(frame, text, (20, 230),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
    
    # Instructions
    cv2.putText(frame, "Show: Fist=Rock | Open Hand=Paper | Peace=Scissors", (20, h - 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    cv2.putText(frame, "Press 'r' to reset score | 'q' to quit", (20, h - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
# ---


# ==========================================
# 5. MAIN GAME LOOP
# ==========================================

print("Starting Rock-Paper-Scissors!")
print("Gestures: Fist=Rock, Open Hand=Paper, Peace Sign=Scissors")
print("Hold gesture steady for 1 second to play.")

# TODO: Run main game loop
# ---
try:
    while cap.isOpened():
        # TODO: Read and preprocess camera frame
        # ---
        ret, frame = cap.read()
        if not ret:
            break
        
        # Flip for mirror view
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        # ---
        
        player_gesture = "Unknown"
        finger_count = 0
        current_time = time.time()
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # TODO: Draw hand skeleton landmarks
                # ---
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                )
                # ---
                
                # TODO: Count fingers and classify gesture
                # ---
                finger_count = count_fingers(hand_landmarks)
                player_gesture = classify_gesture(finger_count)
                # ---
                
                # A valid gesture must be held steady before it counts
                if player_gesture in GESTURES:
                    if player_gesture != hold_gesture:
                        hold_gesture = player_gesture
                        hold_start = current_time
                    held_for = current_time - hold_start
                else:
                    hold_gesture = None
                    held_for = 0.0
                
                # Check if gesture is valid, held long enough, and cooldown passed
                valid_gesture = (player_gesture in GESTURES
                                 and held_for > GESTURE_HOLD_TIME)
                cooldown_ready = (time.time() - last_game_time) > GAME_COOLDOWN
                
                if valid_gesture and cooldown_ready:
                    # Require a fresh hold before the next round can start
                    hold_gesture = None
                    
                    # TODO: Get robot move and determine winner
                    # ---
                    robot_gesture = get_robot_move()
                    result = determine_winner(player_gesture, robot_gesture)
                    # ---
                    
                    # Update scores
                    rounds_played += 1
                    if result == "PLAYER":
                        player_score += 1
                    elif result == "ROBOT":
                        robot_score += 1
                    
                    # TODO: Execute robot gesture movement
                    # ---
                    execute_robot_gesture(robot_gesture)
                    # ---
                    
                    game_result = result
                    last_game_time = time.time()
                    
                    # Brief pause to show result
                    time.sleep(1.0)
                    
                    # Stamp the start of the on-screen verdict. This has to
                    # happen after the arm movement, which blocks the loop and
                    # would otherwise consume the whole display window.
                    last_result_time = time.time()
        
        # Clear the verdict only after it has been on screen long enough
        if (time.time() - last_result_time) > RESULT_DISPLAY_TIME:
            game_result = "Make a gesture!"
        
        # TODO: Draw game UI on frame
        # ---
        draw_ui(frame, player_gesture, last_robot_move, game_result, finger_count)
        # ---
        
        # TODO: Display the frame
        # ---
        cv2.imshow("Mission 02 - Project 06: Rock Paper Scissors", frame)
        # ---
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            player_score = 0
            robot_score = 0
            rounds_played = 0
            last_robot_move = None
            game_result = "Score reset!"

finally:
    cap.release()
    cv2.destroyAllWindows()
    if mc is not None:
        mc.release_all_servos()
    print("\nGame Over!")
    print(f"Final Score - Player: {player_score} | Robot: {robot_score}")
# ---