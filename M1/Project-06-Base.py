#!/usr/bin/env python3

# TODO: Import the cv2, GPIO, and time packages from the Python library.
# The cv2 package will help us work with the camera,
# the GPIO package will allow us to control the pump, 
# and the time package will help us add delays to our script.
# We also need to import the numpy package to help us work with
# numbers for color values.
# ---
import cv2
import time
import RPi.GPIO as GPIO
import numpy as np
# ---

import sys

# TODO: Import the MyCobot280 package from the pymycobot library
# ---

# ---


IS_CV_4 = cv2.__version__[0] == '4'
__version__ = "1.0"
# Adaptive seed


class Object_detect():

    def __init__(self, camera_x = 155, camera_y = 0):
        # inherit the parent class
        super(Object_detect, self).__init__()
        
        # declare mycobot280
        self.mc = None

        # TODO: Store the home location and the starting point for each action in a list.
        # ---

        # ---

        # TODO: Store the coordinates of each bin in a 2D array.
        # Make sure to label which bin each coordinate represents.
        # ---

        # ---

        GPIO.setwarnings(False)
        self.GPIO = GPIO

        # TODO: Initialize the GPIO mode to BCM, initialize pins 20 and 21,
        # and make sure the pump is turned off when starting.=
        # ---

        # ---

        # TODO: Turn off pump at the start of the program
        # ---

        # ---

        # TODO: Create a variable that will determine what color the object is, and where to place the object.
        # 0: Red
        # 1: Green
        # 2: Blue
        # 3: Yellow
        # ---
        self.color = 0
        # ---

        # Parameters to calculate camera clipping
        self.x1 = self.x2 = self.y1 = self.y2 = 0

        # Set a cache of real coords
        self.cache_x = self.cache_y = 0

        # TODO: Set the upper and lower bounds of each color using HSV.
        # ---
        self.HSV = {
            "yellow": [np.array([11, 85, 70]), np.array([59, 255, 245])],
            "red": [np.array([0, 43, 46]), np.array([20, 255, 255])],
            "red2": [np.array([160, 43, 46]), np.array([179, 255, 255])],
            "green": [np.array([35, 43, 35]), np.array([90, 255, 255])],
            "blue": [np.array([100, 100, 46]), np.array([124, 255, 255])],
            "cyan": [np.array([78, 100, 46]), np.array([99, 255, 255])],
        }
        # ---
   
        # use to calculate coord between cube and mycobot280
        self.sum_x1 = self.sum_x2 = self.sum_y2 = self.sum_y1 = 0

        # The coordinates of the grab center point relative to the mycobot280
        self.camera_x, self.camera_y = camera_x, camera_y

        # The coordinates of the cube relative to the mycobot280
        self.c_x, self.c_y = 0, 0

        # The ratio of pixels to actual values
        self.ratio = 0
        
        # Get ArUco marker dict that can be detected.
        self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)

        # Get ArUco marker params.
        self.aruco_params = cv2.aruco.DetectorParameters_create()

    def run(self):
        pass
        # TODO: Initialize the arm's port and baud rate
        # ---

        # ---

        # TODO: Go to the home position
        # ---

        # ---
        

    # TODO: Build a function to control the on/off state of the pump
    # ---
    def gpio_status(self, flag):
        pass
    # ---

    # TODO: Build a function that uses the detected color and the x & y coordinates of the object
    # to move the object into its corresponding bin.
    # ---
    def move(self, x, y, color):
        pass
    # ---

    # decide whether grab cube
    def decide_move(self, x, y, color):
        # print(x, y, self.cache_x, self.cache_y)
        # detect the cube status move or run
        if (abs(x - self.cache_x) + abs(y - self.cache_y)) / 2 > 5:  # mm
            self.cache_x, self.cache_y = x, y
            return
        else:
            self.cache_x = self.cache_y = 0
            # Adjust suction pump pickup position: y increases, moves left; y decreases, moves right; x increases, moves forward; x decreases, moves backward
            print(color)
            self.move(x, y, color)

    # draw aruco markers
    def draw_marker(self, img, x, y):
        # draw rectangle on img
        cv2.rectangle( 
            img,
            (x - 20, y - 20),
            (x + 20, y + 20),
            (0, 255, 0),
            thickness=2,
            lineType=cv2.FONT_HERSHEY_COMPLEX,
        )
        # add text on rectangle
        cv2.putText(img, "({},{})".format(x, y), (x, y),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (243, 0, 0), 2,)

    # get points of two aruco
    def get_calculate_params(self, img):
        # Convert the image to a gray image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Detect ArUco marker.
        corners, ids, rejectImaPoint = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.aruco_params
        )

        
        # Two Arucos must be present in the picture and in the same order.
        # There are two Arucos in the Corners, and each aruco contains the pixels of its four corners.
        # Determine the center of the aruco by the four corners of the aruco.
        
        if len(corners) > 0:
            if ids is not None:
                if len(corners) < 2:
                    return None
                x1 = x2 = y1 = y2 = 0
                point_11, point_21, point_31, point_41 = corners[0][0]
                x1, y1 = int((point_11[0] + point_21[0] + point_31[0] + point_41[0]) / 4.0), int(
                    (point_11[1] + point_21[1] + point_31[1] + point_41[1]) / 4.0)
                point_1, point_2, point_3, point_4 = corners[1][0]
                x2, y2 = int((point_1[0] + point_2[0] + point_3[0] + point_4[0]) / 4.0), int(
                    (point_1[1] + point_2[1] + point_3[1] + point_4[1]) / 4.0)
                
                return x1, x2, y1, y2
        return None

    # set camera clipping parameters 
    def set_cut_params(self, x1, y1, x2, y2):
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.x2 = int(x2)
        self.y2 = int(y2)

    # set parameters to calculate the coords between cube and mycobot280
    def set_params(self, c_x, c_y, ratio):
        self.c_x = c_x
        self.c_y = c_y
        self.ratio = 220.0/ratio

    # calculate the coords between cube and mycobot280
    def get_position(self, x, y):
        return ((y - self.c_y)*self.ratio + self.camera_x), ((x - self.c_x)*self.ratio + self.camera_y)

    # Calibrate the camera according to the calibration parameters.
    # Enlarge the video pixel by 1.5 times, which means enlarge the video size by 1.5 times.
    # If two ARuco values have been calculated, clip the video.
    
    def transform_frame(self, frame):
        # enlarge the image by 1.5 times
        fx = 1.5
        fy = 1.5
        frame = cv2.resize(frame, (0, 0), fx=fx, fy=fy,
                           interpolation=cv2.INTER_CUBIC)
        if self.x1 != self.x2:
            # the cutting ratio here is adjusted according to the actual situation
            frame = frame[int(self.y2*0.78):int(self.y1*1.1),
                          int(self.x1*0.86):int(self.x2*1.08)]
        return frame

    # detect cube color
    def color_detect(self, img):
        # set the arrangement of color'HSV
        x = y = 0
        for mycolor, item in self.HSV.items():
            # transform the img to model of gray
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # wipe off all color expect color in range
            mask = cv2.inRange(hsv, item[0], item[1])

            # an etching operation on a picture to remove edge roughness
            erosion = cv2.erode(mask, np.ones((1, 1), np.uint8), iterations=2)

            # the image for expansion operation, its role is to deepen the color depth in the picture
            dilation = cv2.dilate(erosion, np.ones(
                (1, 1), np.uint8), iterations=2)

            # adds pixels to the image
            target = cv2.bitwise_and(img, img, mask=dilation)

            # the filtered image is transformed into a binary image and placed in binary
            ret, binary = cv2.threshold(dilation, 127, 255, cv2.THRESH_BINARY)

            # get the contour coordinates of the image, where contours is the coordinate value, here only the contour is detected
            contours, hierarchy = cv2.findContours(
                dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if len(contours) > 0:
                # do something about misidentification
                boxes = [
                    box
                    for box in [cv2.boundingRect(c) for c in contours]
                    if min(img.shape[0], img.shape[1]) / 10
                    < min(box[2], box[3])
                    < min(img.shape[0], img.shape[1]) / 1
                ]
                if boxes:
                    for box in boxes:
                        x, y, w, h = box
                    # find the largest object that fits the requirements
                    c = max(contours, key=cv2.contourArea)
                    # get the lower left and upper right points of the positioning object
                    x, y, w, h = cv2.boundingRect(c)
                    # locate the target by drawing rectangle
                    cv2.rectangle(img, (x, y), (x+w, y+h), (153, 153, 0), 2)
                    # calculate the rectangle center
                    x, y = (x*2+w)/2, (y*2+h)/2
                    # calculate the real coordinates of mycobot280 relative to the target
                    
                    # TODO: Assign a number to each color.
                    # ---
                    if mycolor  == "yellow":
                        self.color = 3
                        break

                    elif mycolor == "red" or mycolor == "red2":
                        self.color = 0
                        break

                    elif mycolor == "cyan" or mycolor == "blue":
                        self.color = 2
                        break

                    elif mycolor == "green":
                        self.color = 1
                        break
                    # ---
        
        # Determine if recognition is normal
        if abs(x) + abs(y) > 0:
            return x, y
        else:
            return None

if __name__ == "__main__":

    # TODO: Open the camera
    # ---
    cap_num = 0
    cap = cv2.VideoCapture(cap_num, cv2.CAP_V4L)
 
    if not cap.isOpened():
        cap.open(cap_num)
    # ---
    
    # init a class of Object_detect
    detect = Object_detect()

    # init mycobot280
    detect.run()

    _init_ = 20  
    init_num = 0
    nparams = 0
    num = 0
    real_sx = real_sy = 0
    while cv2.waitKey(1) < 0:
       # read camera
        _, frame = cap.read()
        # deal img
        frame = detect.transform_frame(frame)
        if _init_ > 0:
            _init_ -= 1
            continue

        # calculate the parameters of camera clipping
        if init_num < 20:
            if detect.get_calculate_params(frame) is None:
                cv2.imshow("figure", frame)
                continue
            else:
                x1, x2, y1, y2 = detect.get_calculate_params(frame)
                detect.draw_marker(frame, x1, y1)
                detect.draw_marker(frame, x2, y2)
                detect.sum_x1 += x1
                detect.sum_x2 += x2
                detect.sum_y1 += y1
                detect.sum_y2 += y2
                init_num += 1
                continue
        elif init_num == 20:
            detect.set_cut_params(
                (detect.sum_x1)/20.0,
                (detect.sum_y1)/20.0,
                (detect.sum_x2)/20.0,
                (detect.sum_y2)/20.0,
            )
            detect.sum_x1 = detect.sum_x2 = detect.sum_y1 = detect.sum_y2 = 0
            init_num += 1
            continue

        # calculate params of the coords between cube and mycobot280
        if nparams < 10:
            if detect.get_calculate_params(frame) is None:
                cv2.imshow("figure", frame)
                continue
            else:
                x1, x2, y1, y2 = detect.get_calculate_params(frame)
                detect.draw_marker(frame, x1, y1)
                detect.draw_marker(frame, x2, y2)
                detect.sum_x1 += x1
                detect.sum_x2 += x2
                detect.sum_y1 += y1
                detect.sum_y2 += y2
                nparams += 1
                continue
        elif nparams == 10:
            nparams += 1
            # calculate and set params of calculating real coord between cube and mycobot280
            detect.set_params(
                (detect.sum_x1+detect.sum_x2)/20.0,
                (detect.sum_y1+detect.sum_y2)/20.0,
                abs(detect.sum_x1-detect.sum_x2)/10.0 +
                abs(detect.sum_y1-detect.sum_y2)/10.0
            )
            print("Ready")
            continue

        # get detect result
        detect_result = detect.color_detect(frame)
        if detect_result is None:
            cv2.imshow("figure", frame)
            continue
        else:
            x, y = detect_result
            # calculate real coord between cube and mycobot280
            real_x, real_y = detect.get_position(x, y)
            if num == 20:
                
                detect.decide_move(real_sx/20.0, real_sy/20.0, detect.color)
                num = real_sx = real_sy = 0

            else:
                num += 1
                real_sy += real_y
                real_sx += real_x

        cv2.imshow("figure", frame)

        # close the window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            sys.exit()
