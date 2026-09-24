import cv2
import time

def find_working_camera():
    print("Searching for cameras...")
    # Test indices 0 through 4
    for i in range(5):
        print(f"Testing index {i}...")
        
        # Try default backend first
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            # Sometimes a camera opens but takes a second to warm up
            time.sleep(0.5) 
            ret, frame = cap.read()
            
            if ret and frame is not None:
                print(f"\SUCCESS: Camera found and streaming on index {i}")
                cap.release()
                return i
            else:
                print(f"Index {i} opened, but returned no video frames.")
        else:
            print(f"Index {i} could not be opened.")
            
        cap.release()
        
    print("\n🚨 No working cameras found. Check USB connection and permissions.")
    return None

find_working_camera()