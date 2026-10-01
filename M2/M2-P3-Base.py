import os
import time
import cv2
import numpy as np
import threading
from pymycobot.mycobot280 import MyCobot280

# =====================================================================
# 1. ROBOT INITIALIZATION
# =====================================================================
try:
    print("Connecting to myCobot280...")
    mc = MyCobot280('/dev/ttyAMA0', 1000000)
    time.sleep(0.5)
    mc.power_on()
    time.sleep(0.5)

    # Move to initial folded position (Angles: J1-J6)
    folded_angles = [0, 45, -90, -45, 0, 0]
    print("Moving arm to initial folded position...")
    mc.send_angles(folded_angles, 20)
    time.sleep(2.0)
    print("Robot ready.")

except Exception as e:
    print(f"Robot hardware warning: {e}")
    print("Continuing with OpenCV camera pipeline only...\n")


# =====================================================================
# 2. THREADED CAMERA PIPELINE
# =====================================================================
class ThreadedCamera:
    """Asynchronous camera reader thread to eliminate V4L2 frame buffer latency."""
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

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


# =====================================================================
# 3. OPENCV YOLOV5 & ARUCO DETECTOR PIPELINE
# =====================================================================
class VisionPipeline:
    def __init__(self, conf_thresh=0.45, score_thresh=0.5, nms_thresh=0.45):
        self.x1 = self.x2 = self.y1 = self.y2 = 0
        self.conf_thresh = conf_thresh
        self.score_thresh = score_thresh
        self.nms_thresh = nms_thresh
        self.input_size = (640, 640)

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

        # Load YOLOv5 Model & Class Names
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, "yolov5s.onnx")
        labels_path = os.path.join(script_dir, "coco.names")

        self.net = cv2.dnn.readNet(model_path) if os.path.exists(model_path) else None
        self.classes = []
        if os.path.exists(labels_path):
            with open(labels_path, "r") as f:
                self.classes = [line.strip() for line in f if line.strip()]

    def calculate_aruco_bounds(self, frame):
        """Detects ArUco markers to establish workspace bounds."""
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
                p1 = corners[0][0]
                p2 = corners[1][0]
                self.x1, self.y1 = int(p1[:, 0].mean()), int(p1[:, 1].mean())
                self.x2, self.y2 = int(p2[:, 0].mean()), int(p2[:, 1].mean())
                return True
        except Exception:
            pass
        return False

    def transform_frame(self, frame):
        """Crops the workspace area inside the ArUco markers."""
        if frame is None or frame.size == 0:
            return None

        fx, fy = 1.5, 1.5
        resized = cv2.resize(frame, (0, 0), fx=fx, fy=fy, interpolation=cv2.INTER_CUBIC)

        if self.x1 != 0 and self.x2 != 0 and self.y1 != 0 and self.y2 != 0:
            sx1, sx2 = int(self.x1 * fx), int(self.x2 * fx)
            sy1, sy2 = int(self.y1 * fy), int(self.y2 * fy)

            x_min, x_max = min(sx1, sx2), max(sx1, sx2)
            y_min, y_max = min(sy1, sy2), max(sy1, sy2)

            margin = 25
            x_min, x_max = x_min + margin, x_max - margin
            y_min, y_max = y_min + margin, y_max - margin

            if y_max > y_min and x_max > x_min:
                cropped = resized[y_min:y_max, x_min:x_max]
                if cropped.size > 0:
                    return cropped

        return resized

    def yolo_detect(self, img):
        """Performs YOLOv5 ONNX detection and returns annotated frame + status string."""
        if img is None or img.size == 0:
            return img, "No Frame"

        if self.net is None:
            return img, "YOLO Model Not Loaded"

        img_h, img_w = img.shape[:2]
        blob = cv2.dnn.blobFromImage(
            img, 1.0 / 255.0, self.input_size, [0, 0, 0], swapRB=True, crop=False
        )
        self.net.setInput(blob)
        outputs = self.net.forward(self.net.getUnconnectedOutLayersNames())

        predictions = outputs[0]
        if len(predictions.shape) == 3:
            predictions = predictions[0]

        boxes, confidences, class_ids = [], [], []
        x_factor = img_w / self.input_size[0]
        y_factor = img_h / self.input_size[1]

        for row in predictions:
            confidence = row[4]
            if confidence > self.conf_thresh:
                scores = row[5:]
                class_id = np.argmax(scores)
                if scores[class_id] > self.score_thresh:
                    cx, cy, w, h = row[0], row[1], row[2], row[3]
                    left = int((cx - w / 2.0) * x_factor)
                    top = int((cy - h / 2.0) * y_factor)
                    width = int(w * x_factor)
                    height = int(h * y_factor)

                    boxes.append([left, top, width, height])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.score_thresh, self.nms_thresh)

        if len(indices) == 0:
            return img, "Searching..."

        if isinstance(indices, tuple) or len(indices.shape) > 1:
            indices = indices.flatten()

        annotated_img = img.copy()
        detected_names = []

        for idx in indices:
            left, top, width, height = boxes[idx]
            cx, cy = left + width // 2, top + height // 2

            class_name = self.classes[class_ids[idx]] if class_ids[idx] < len(self.classes) else str(class_ids[idx])
            label = f"{class_name} {confidences[idx]:.2f}"
            detected_names.append(label)

            cv2.rectangle(annotated_img, (left, top), (left + width, top + height), (0, 255, 0), 2)
            cv2.circle(annotated_img, (cx, cy), 4, (0, 0, 255), -1)
            cv2.putText(annotated_img, label, (left, max(top - 5, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        status_msg = f"Detected: {', '.join(detected_names)}"
        return annotated_img, status_msg


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
# 4. MAIN CAMERA LOOP
# =====================================================================
def main():
    cap_num = find_working_camera()
    if cap_num is None:
        print("Error: No working camera stream found.")
        return

    # Replace standard cv2.VideoCapture with ThreadedCamera
    cap = ThreadedCamera(cap_num)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    vision = VisionPipeline()
    print("Threaded camera active. Press 'q' in any window to exit.")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            time.sleep(0.01)
            continue

        # 1. Update ArUco calibration coordinates
        vision.calculate_aruco_bounds(frame)

        # 2. Crop frame between ArUco markers
        cropped_frame = vision.transform_frame(frame)

        # 3. Perform YOLOv5 object detection
        display_frame, log_info = vision.yolo_detect(cropped_frame)

        # Print metric diagnostics directly to terminal when an object is evaluated
        if "Searching" not in log_info and "No Frame" not in log_info:
            print(f"\r[YOLOv5] {log_info}", end="")

        # 4. Show OpenCV preview window
        if display_frame is not None and display_frame.size > 0:
            cv2.imshow("YOLOv5 Object Detection", display_frame)

        # Exit program on 'q' keypress
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean shutdown of camera thread and openCV windows
    cap.release()
    cv2.destroyAllWindows()
    print("\nScript terminated cleanly.")


if __name__ == "__main__":
    main()