# TODO: Import the cv2, numpy, and time packages from the Python package library
# ---

# ---

# TODO: Import the MyCobot280 package from the pymycobot library
# ---

# ---

# =====================================================================
# 1. ROBOT INITIALIZATION
# =====================================================================

try:
    # TODO: Initialize the arm, wait, and ensure the arm is on.
    # ---

    # ---
    
    # TODO: Move arm to initial folded position
    # ---

    # ---

    print("Robot ready.")

except Exception as e:
    print(f"Robot hardware warning: {e}")
    print("Continuing with OpenCV camera pipeline only...\n")


# =====================================================================
# 2. OPENCV SHAPE & ARUCO DETECTOR
# =====================================================================

class VisionPipeline:
    def __init__(self):
        self.x1 = self.x2 = self.y1 = self.y2 = 0

        # Safe ArUco initialization across OpenCV 4.x versions
        try:
            self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
            self.aruco_params = cv2.aruco.DetectorParameters()
            self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
            self.use_new_aruco = True
        except AttributeError:
            self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
            self.aruco_params = cv2.aruco.DetectorParameters_create()
            self.use_new_aruco = False

    def calculate_aruco_bounds(self, frame):
        # Detects ArUco markers to establish workspace bounds.
        if frame is None or frame.size == 0:
            return False

        frame_contiguous = np.ascontiguousarray(frame, dtype=np.uint8)
        try:
            gray = cv2.cvtColor(frame_contiguous, cv2.COLOR_BGR2GRAY)
            if self.use_new_aruco:
                corners, ids, _ = self.detector.detectMarkers(gray)
            else:
                corners, ids, _ = cv2.aruco.detectMarkers(
                    gray, self.aruco_dict, parameters=self.aruco_params
                )

            if ids is not None and len(corners) >= 2:
                # Average center points for marker 1 and marker 2
                p1 = corners[0][0]
                p2 = corners[1][0]
                self.x1, self.y1 = int(p1[:, 0].mean()), int(p1[:, 1].mean())
                self.x2, self.y2 = int(p2[:, 0].mean()), int(p2[:, 1].mean())
                return True
        except Exception:
            pass
        return False

    def transform_frame(self, frame):
        # Crops the workspace area inside the ArUco markers.
        if frame is None or frame.size == 0:
            return None

        # Resize for higher processing resolution
        fx, fy = 1.5, 1.5
        resized = cv2.resize(frame, (0, 0), fx=fx, fy=fy, interpolation=cv2.INTER_CUBIC)

        if self.x1 != 0 and self.x2 != 0 and self.y1 != 0 and self.y2 != 0:
            # Scale coordinates
            sx1, sx2 = int(self.x1 * fx), int(self.x2 * fx)
            sy1, sy2 = int(self.y1 * fy), int(self.y2 * fy)

            x_min, x_max = min(sx1, sx2), max(sx1, sx2)
            y_min, y_max = min(sy1, sy2), max(sy1, sy2)

            # Inward crop margin (25px) to keep ArUco markers out of the detection frame
            margin = 25
            x_min, x_max = x_min + margin, x_max - margin
            y_min, y_max = y_min + margin, y_max - margin

            if y_max > y_min and x_max > x_min:
                cropped = resized[y_min:y_max, x_min:x_max]
                if cropped.size > 0:
                    return cropped

        return resized

    def shape_detect(self, img):
        # Identifies shape type and returns modified frame + threshold debug mask.
        if img is None or img.size == 0:
            return img, None, "No Frame"

        img_h, img_w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Binary threshold isolating dark objects on light backgrounds
        _, thresh = cv2.threshold(blurred, 110, 255, cv2.THRESH_BINARY_INV)

        # Morphological cleanup to eliminate outline gaps
        kernel = np.ones((5, 5), np.uint8)
        thresh_clean = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(thresh_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        status_msg = "Searching..."

        for cnt in contours:
            # TODO: Find how much of the screen the shape covers
            # ---

            # ---

            # TODO: Find the perimeter of the shape, if available.
            # ---

            # ---

            # TODO: Find the rectangular area of the shape, if available.
            # ---

            # ---

            # TODO: Calculate the shape metrics
            # ---

            # ---
            
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
            num_vertices = len(approx)

            # TODO: Initialize an object type variable.
            # ---

            # ---

            # TODO: Decide the shape that the camera sees.
            # ---

            # ---
            
            # Draw bounding box and label
            box = np.int32(cv2.boxPoints(rect))
            cv2.drawContours(img, [box], 0, (0, 255, 0), 2)
            cv2.putText(img, object_type, (int(cx) - 35, int(cy)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            status_msg = f"{object_type} | Extent: {extent:.2f} | Circ: {circularity:.2f} | Verts: {num_vertices}"
            break

        return img, thresh_clean, status_msg


def find_working_camera(max_tests=5):
    # Scans video indices and returns the first camera that produces frames.
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
    # TODO: Find the working camera index.
    # ---
    
    # ---

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    vision = VisionPipeline()
    print("Camera active. Press 'q' in any window to exit.")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            continue

        # 1. Update ArUco calibration coordinates
        vision.calculate_aruco_bounds(frame)

        # 2. Crop frame between ArUco markers
        cropped_frame = vision.transform_frame(frame)

        # 3. Perform shape detection
        display_frame, thresh_mask, log_info = vision.shape_detect(cropped_frame)

        # Print metric diagnostics directly to terminal when a shape is evaluated
        if "Searching" not in log_info and "No Frame" not in log_info:
            print(f"\r[Detected] {log_info}", end="")

        # 4. Show OpenCV debug windows
        if display_frame is not None and display_frame.size > 0:
            cv2.imshow("Shape Detection", display_frame)

        if thresh_mask is not None and thresh_mask.size > 0:
            cv2.imshow("Threshold View (Binary)", thresh_mask)

        # Exit program on 'q' keypress
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\nScript terminated cleanly.")

if __name__ == "__main__":
    main()