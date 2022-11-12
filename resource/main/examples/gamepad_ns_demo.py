#!/usb/bin/python3
"""
NS Demo
Test Gamepad_MF class by pressing and releasing all buttons then moving
the Gamepad in all directions.
"""
import time
import sys
sys.path.append('../')
from module.gamepad_MF import *

def main():
    """ test NSGamepad class """

    Gamepad = Gamepad_MF()
    Gamepad.begin('/dev/hidg0')

    while True:
        # Press and hold every button 0..13
        for button in range(0, 14):
            Gamepad.press(button)
            time.sleep(0.1)
        time.sleep(1)
        # Release all buttons
        Gamepad.releaseAll()
        time.sleep(1)
        # Press all 14 buttons at the same time
        Gamepad.buttons(0x3fff)
        time.sleep(1)
        # Release all buttons
        Gamepad.releaseAll()
        time.sleep(1)
        # Move directional pad in all directions
        # 0 = North, 1 = North-East, 2 = East, etc.
        for direction in range(0, 8):
            Gamepad.dPad(direction)
            time.sleep(0.5)
        # Move directional pad to center
        Gamepad.dPad(DPad.CENTERED)

        # Move the left stick then right stick
        stick = [
            {"x": 0, "y": 0},
            {"x": 0, "y": -127},
            {"x": 127, "y": -127},
            {"x": 127, "y": 0},
            {"x": 127, "y": 127},
            {"x": -127, "y": 127},
            {"x": -127, "y": 127},
            {"x": -127, "y": 0},
            {"x": -127, "y": -127},
            {"x": 0, "y": 0},
        ]
        for direction in range(0, 10):
            Gamepad.leftXAxis(stick[direction]['x'])
            Gamepad.leftYAxis(stick[direction]['y'])
            time.sleep(0.5)
        for direction in range(0, 10):
            Gamepad.rightXAxis(stick[direction]['x'])
            Gamepad.rightYAxis(stick[direction]['y'])
            time.sleep(0.5)

if __name__ == "__main__":
    main()
