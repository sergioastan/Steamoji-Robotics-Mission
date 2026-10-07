# Import packages
from pymycobot.mycobot280 import MyCobot280
import RPi.GPIO as GPIO
import time

# Initialize arm
mc = MyCobot280('/dev/ttyAMA0', 1000000)

# Initialize variables
speed = 50
mode = 0

# Angles
home = [0, 45, -90, -45, 0, 0]
loadingArea = [50, -63, -15, -10, 0, 0]

# Coordinates
binA = [136, 157]
binB = [22.5, 154]
binC = [219, -140]
binD = [148, -140]
center = [150, 0, 230, 180, 0, 0]

# Functions
def pump_off():
    GPIO.output(20, GPIO.HIGH)
    GPIO.output(21, GPIO.HIGH)

def pump_on():
    GPIO.output(20, GPIO.LOW)
    GPIO.output(21, GPIO.LOW)

def initialize_pump():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)
    pump_off()

def grab_from_location(bin):
    x = bin[0]
    y = bin[1]

    # Bring arm to bin
    mc.send_coords([x, y, 150, 180, 0, 0], speed, mode)

    # Lower arm
    mc.send_coords([x, y, 100, 180, 0, 0], speed, mode)
    time.sleep(4)

    # Turn on the pump
    pump_on()
    time.sleep(1)

    # Raise arm
    mc.send_coords([x, y, 200, 180, 0, 0], speed, mode)

    # Go to center
    mc.send_coords(center, speed, mode)

    # Go to the loading area
    mc.send_angles(loadingArea, speed)
    time.sleep(6)

    # Drop the object
    pump_off()
    time.sleep(1)

    # Go back to the home position
    mc.send_angles(home, speed)
    time.sleep(2)

# Program loop
if __name__ == "__main__":
    initialize_pump()
    
    mc.send_angles(home, speed)
    time.sleep(2)

    grab_from_location(binA)
    time.sleep(2)

    grab_from_location(binB)
    time.sleep(2)

    grab_from_location(binC)
    time.sleep(2)

    grab_from_location(binD)
    time.sleep(2)