#!/usb/bin/python3
"""
32B Demo
Test Gamepad_32B class by pressing and releasing all buttons then moving
the Gamepad in all directions.
"""

import time
import sys
sys.path.append('../')
from module.gamepad_32B import Gamepad_32B

def main():
    """ test Gamepad_32B class """

    Gamepad = Gamepad_32B()
    Gamepad.begin('/dev/hidg0')

    while True:
        # Press and hold every button
        for button in range(0, 32):
            Gamepad.press(button)
            time.sleep(0.1)
        time.sleep(1)
        # Release all buttons
        Gamepad.releaseAll()
        time.sleep(1)
        # Press all buttons at the same time
        Gamepad.buttons(0xffffffff)
        time.sleep(1)
        # Release all buttons
        Gamepad.releaseAll()
        time.sleep(1)

        # Move the stick clockwise
        stick = [
            {"x":   0, "y":   0},
            {"x":   0, "y": -127},
            {"x": 127, "y": -127},
            {"x": 127, "y":   0},
            {"x": 127, "y": 127},
            {"x":   0, "y": 127},
            {"x":-127, "y": 127},
            {"x":-127, "y":   0},
            {"x":-127, "y":-127},
            {"x":   0, "y":   0},
        ]
        for direction in range(0, 10):
            Gamepad.xAxis(stick[direction]['x'])
            Gamepad.yAxis(stick[direction]['y'])
            time.sleep(0.5)

if __name__ == "__main__":
    main()
