# Remember to cover the two markers on the board for this project!

# TODO: Import the cv2, numpy, and time packages from the Python package library.
# ---
import time
import cv2
import numpy as np
# ---

# TODO: Import the MyCobot280 package from the pymycobot library
# ---
from pymycobot.mycobot280 import MyCobot280
# ---

# =====================================================================
# 1. ROBOT INITIALIZATION
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
    folded_angles = [0, 45, -90, -45, 0, 0]
    print("Moving arm to initial folded position...")
    mc.send_angles(folded_angles, 20)
    time.sleep(2.0)
    # ---
    
    print("Robot ready.")
    
except Exception as e:
    print(f"Robot hardware warning: {e}")
    print("Continuing with OpenCV camera pipeline only...\n")


# =====================================================================
# 2. OPENCV ARUCO / QR MARKER DETECTOR PIPELINE
# =====================================================================
class ArUcoMarkerPipeline:
    def __init__(self):
        # Pump / End-effector spatial offsets (mm)
        self.pump_x = 15
        self.pump_y = -55
        
        # Camera intrinsic matrix & distortion coefficients
        self.camera_matrix = np.array([
            [781.33379113, 0.0, 347.53500524],
            [0.0, 783.79074192, 246.67627253],
            [0.0, 0.0, 1.0]
        ], dtype=np.float32)

        self.dist_coeffs = np.array([
            [3.41360787e-01, -2.52114260e+00, -1.28012469e-03, 6.70503562e-03, 2.57018000e+00]
        ], dtype=np.float32)

        # ArUco marker size in meters (30mm)
        self.marker_size_m = 0.03

        # Safe ArUco initialization across OpenCV versions
        try:
            self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
            self.aruco_params = cv2.aruco.DetectorParameters()
            self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
            self.use_new_aruco = True
        except AttributeError:
            self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
            self.aruco_params = cv2.aruco.DetectorParameters_create()
            self.use_new_aruco = False

    def process_frame(self, frame):
        """Detects ArUco markers, estimates 3D camera-relative pose, and draws overlays."""
        if frame is None or frame.size == 0:
            return frame, "No Frame"

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect markers based on OpenCV version
        if self.use_new_aruco:
            corners, ids, _ = self.detector.detectMarkers(gray)
        else:
            corners, ids, _ = cv2.aruco.detectMarkers(
                gray, self.aruco_dict, parameters=self.aruco_params
            )

        status_msg = "Searching for markers..."

        if ids is not None and len(corners) > 0:
            # Draw outlines on detected markers
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            # Pose estimation for single markers
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, self.marker_size_m, self.camera_matrix, self.dist_coeffs
            )

            for i in range(len(ids)):
                marker_id = int(ids[i][0])
                tvec = tvecs[i][0]  # [X, Y, Z] in meters

                # Calculate position in mm relative to end-effector pump
                rel_x = round(tvec[0] * 1000 + self.pump_y, 2)
                rel_y = round(tvec[1] * 1000 + self.pump_x, 2)
                rel_z = round(tvec[2] * 1000, 2)

                # Draw axis overlay
                cv2.drawFrameAxes(
                    frame, self.camera_matrix, self.dist_coeffs,
                    rvecs[i], tvecs[i], self.marker_size_m * 0.5
                )

                # Draw coordinate overlay text near marker center
                corner_center = np.mean(corners[i][0], axis=0).astype(int)
                label_text = f"ID:{marker_id} X:{rel_x} Y:{rel_y} Z:{rel_z}mm"
                
                cv2.putText(
                    frame, label_text, (corner_center[0] - 80, corner_center[1] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
                )

                status_msg = f"ID: {marker_id} | X: {rel_x}mm | Y: {rel_y}mm | Z: {rel_z}mm"

        return frame, status_msg


def find_working_camera(max_tests=5):
    """Scans video indices and returns the first camera that produces frames."""
    for idx in range(max_tests):
        cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret and frame is not None and frame.size > 0:
                print(f"Found active camera at index {idx}")
                return idx
    return None

# =====================================================================
# 3. MAIN CAMERA LOOP
# =====================================================================
def main():
    cap_num = find_working_camera()
    if cap_num is None:
        print("Error: No working camera stream found.")
        return

    cap = cv2.VideoCapture(cap_num, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    vision = ArUcoMarkerPipeline()
    print("Camera active. Press 'q' in any window to exit.")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            continue

        # Process ArUco detection & pose estimation
        display_frame, log_info = vision.process_frame(frame)

        # Print metric diagnostics directly to terminal when a marker is in view
        if "Searching" not in log_info and "No Frame" not in log_info:
            print(f"\r[Detected] {log_info}", end="")

        # Show OpenCV window
        if display_frame is not None and display_frame.size > 0:
            cv2.imshow("ArUco Marker Pose Detection", display_frame)

        # Exit program on 'q' keypress
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\nScript terminated cleanly.")

if __name__ == "__main__":
    main()