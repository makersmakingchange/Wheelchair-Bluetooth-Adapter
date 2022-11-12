#!/usr/bin/python3

import sys
import asyncio  
import time    
import evdev        # sudo apt install python3-evdev
from enum import IntEnum
from module.gamepad_16B import Gamepad_16B

Gamepad = Gamepad_16B()
Gamepad.begin('/dev/hidg0')

DEBUG_MODE = True

mice_x_in = 0
mice_y_in = 0

gamepad_x_out = 0
gamepad_y_out = 0

"""
USB HID gamepads may optionally expose digital buttons through the HID
interface.  
"""

class SIXTEEN_BUTTON(IntEnum):
    BOne = 0
    BTwo = 1
    BThree = 2
    BFour = 3
    BFive = 4
    BSix = 5
    BSeven = 6
    BEight = 7
    BNine = 8
    BTen = 9
    BEleven = 10
    BTwelve = 11
    BThirteen = 12
    BFourteen = 13
    BFifteen  = 14
    BSixteen = 15

    
class GAMEPAD_XY(IntEnum):
    MinInputValue = -16
    MaxInputValue = 16
    MinOutputValue = -127
    MaxOutputValue = 127
    DeadZoneValue = 1
    OperationMode = 0  # 0: Don't Keep position after each mice move, 1: Keep position after each mice move
    ReactionTimeValue = 10  #10 ms

# Map keyboard keys or mouse buttons to gamepad buttons.
EVENT2ACTION = {
    'BUTTONS': {
        str(evdev.ecodes.BTN_LEFT): SIXTEEN_BUTTON.BOne,
        str(evdev.ecodes.BTN_RIGHT): SIXTEEN_BUTTON.BTwo,
        str(evdev.ecodes.BTN_MIDDLE): SIXTEEN_BUTTON.BThree,
        str(evdev.ecodes.BTN_SIDE): SIXTEEN_BUTTON.BFour,
        str(evdev.ecodes.BTN_EXTRA): SIXTEEN_BUTTON.BFive,
        str(evdev.ecodes.KEY_1): SIXTEEN_BUTTON.BOne,
        str(evdev.ecodes.KEY_2): SIXTEEN_BUTTON.BTwo,
        str(evdev.ecodes.KEY_3): SIXTEEN_BUTTON.BThree,
        str(evdev.ecodes.KEY_4): SIXTEEN_BUTTON.BFour,
        str(evdev.ecodes.KEY_5): SIXTEEN_BUTTON.BFive,
        str(evdev.ecodes.KEY_6): SIXTEEN_BUTTON.BSix,       
        str(evdev.ecodes.KEY_7): SIXTEEN_BUTTON.BSeven,
        str(evdev.ecodes.KEY_8): SIXTEEN_BUTTON.BEight,
        str(evdev.ecodes.KEY_9): SIXTEEN_BUTTON.BNine,
        str(evdev.ecodes.KEY_R): SIXTEEN_BUTTON.BTen,
        str(evdev.ecodes.KEY_T): SIXTEEN_BUTTON.BEleven,
        str(evdev.ecodes.KEY_Y): SIXTEEN_BUTTON.BTwelve,       
        str(evdev.ecodes.KEY_U): SIXTEEN_BUTTON.BThirteen,
        str(evdev.ecodes.KEY_I): SIXTEEN_BUTTON.BFourteen,
        str(evdev.ecodes.KEY_O): SIXTEEN_BUTTON.BFifteen,
        str(evdev.ecodes.KEY_P): SIXTEEN_BUTTON.BSixteen
    }, 
    'DIRECTIONS': {
        str(evdev.ecodes.KEY_UP): {"x":   0, "y": -127},
        str(evdev.ecodes.KEY_RIGHT): {"x":   127, "y": 0},
        str(evdev.ecodes.KEY_DOWN): {"x":   0, "y": 127},
        str(evdev.ecodes.KEY_LEFT): {"x":   -127, "y": 0},
        str(evdev.ecodes.KEY_W): {"x":   0, "y": -127},
        str(evdev.ecodes.KEY_D): {"x":   127, "y": 0},
        str(evdev.ecodes.KEY_S): {"x":   0, "y": 127},
        str(evdev.ecodes.KEY_A): {"x":   -127, "y": 0}
    },
    'OTHERS': {
        str(evdev.ecodes.REL_WHEEL): SIXTEEN_BUTTON.BSix    
    }
}


async def handle_events(device):
    global mice_x_in
    global mice_y_in
    global gamepad_x_out
    global gamepad_y_out
    # Grab exclusive access means the shell and/or GUI no longer receives the input events
    with device.grab_context():
        async for event in device.async_read_loop():
            if event.code == evdev.ecodes.KEY_PAUSE:
                sys.exit(0)
            if str(event.code) in EVENT2ACTION.get('BUTTONS'):
                gamepad_button = EVENT2ACTION.get('BUTTONS')[str(event.code)]
                if event.value == 1:
                    if DEBUG_MODE: 
                        print('Key or button press', 'gamepad button press', gamepad_button)
                    Gamepad.press(gamepad_button)
                    time.sleep(0.05)
                elif event.value == 0:
                    if DEBUG_MODE: 
                        print('Key or button release', 'gamepad button release', gamepad_button)
                    Gamepad.release(gamepad_button)
            elif str(event.code) in EVENT2ACTION.get('DIRECTIONS'):
                gamepad_move = EVENT2ACTION.get('DIRECTIONS')[str(event.code)]
                if event.value == 1:
                    if DEBUG_MODE: 
                        print('Direction Key press', 'gamepad axis move', gamepad_move)
                    Gamepad.xAxis(gamepad_move['x'])
                    Gamepad.yAxis(gamepad_move['y'])
                    time.sleep(0.05)
                elif event.value == 0:
                    if DEBUG_MODE: 
                        print('Direction Key release', 'gamepad axis release', gamepad_move)
                    Gamepad.xAxis(0)
                    Gamepad.yAxis(0)
            else:
                """ Map mouse motion to thumbstick motion """
                if event.code == evdev.ecodes.REL_X and int(GAMEPAD_XY.OperationMode)== 0 and event.value != 0:
                    mice_x_in = event.value
                    gamepad_x_out = map_joystick(mice_x_in,int(GAMEPAD_XY.DeadZoneValue),int(GAMEPAD_XY.MinInputValue),int(GAMEPAD_XY.MaxInputValue),int(GAMEPAD_XY.MinOutputValue),int(GAMEPAD_XY.MaxOutputValue))
                    if DEBUG_MODE: 
                        print('REL_X', event.value , 'gamepad x axis out', gamepad_x_out)
                    Gamepad.xAxis(gamepad_x_out)
                if event.code == evdev.ecodes.REL_X and int(GAMEPAD_XY.OperationMode) == 1:
                    mice_x_in = event.value + mice_x_in
                    gamepad_x_out = map_joystick(mice_x_in,int(GAMEPAD_XY.DeadZoneValue),int(GAMEPAD_XY.MinInputValue),int(GAMEPAD_XY.MaxInputValue),int(GAMEPAD_XY.MinOutputValue),int(GAMEPAD_XY.MaxOutputValue))
                    if DEBUG_MODE: 
                        print('REL_X', event.value , 'gamepad x axis out', gamepad_x_out)
                    Gamepad.xAxis(gamepad_x_out)
                elif event.code == evdev.ecodes.REL_Y and int(GAMEPAD_XY.OperationMode)== 0 and event.value != 0:
                    mice_y_in = event.value
                    gamepad_y_out = map_joystick(mice_y_in,int(GAMEPAD_XY.DeadZoneValue),int(GAMEPAD_XY.MinInputValue),int(GAMEPAD_XY.MaxInputValue),int(GAMEPAD_XY.MinOutputValue),int(GAMEPAD_XY.MaxOutputValue))
                    if DEBUG_MODE: 
                        print('REL_Y', event.value , 'gamepad y axis out', gamepad_y_out)
                    Gamepad.yAxis(gamepad_y_out)
                elif event.code == evdev.ecodes.REL_Y and int(GAMEPAD_XY.OperationMode)== 1:
                    mice_y_in = event.value + mice_y_in
                    gamepad_y_out = map_joystick(mice_y_in,int(GAMEPAD_XY.DeadZoneValue),int(GAMEPAD_XY.MinInputValue),int(GAMEPAD_XY.MaxInputValue),int(GAMEPAD_XY.MinOutputValue),int(GAMEPAD_XY.MaxOutputValue))
                    if DEBUG_MODE: 
                        print('REL_Y', event.value , 'gamepad y axis out', gamepad_y_out)
                    Gamepad.yAxis(gamepad_y_out)
                elif event.code == evdev.ecodes.REL_WHEEL:
                    gamepad_button = EVENT2ACTION.get('OTHERS')[str(event.code)]
                    if event.value == 1:
                        Gamepad.press(gamepad_button)
                    elif event.value == -1:
                        Gamepad.release(gamepad_button)
                    if DEBUG_MODE: 
                        print('REL_WHEEL', event.value)
                elif event.code == evdev.ecodes.REL_HWHEEL:
                    if DEBUG_MODE: 
                        print('REL_HWHEEL', event.value)
                elif event.code == evdev.ecodes.ABS_X and event.value != 0:
                    if DEBUG_MODE: 
                        print('ABS_X', event.value)
                elif event.code == evdev.ecodes.ABS_Y and event.value != 0:
                    if DEBUG_MODE: 
                        print('ABS_Y', event.value)
                else:
                    time.sleep(reaction_time)
                    info = device.read_one()
                    if(info == None):
                        if gamepad_x_out != 0:
                           Gamepad.xAxis(0)
                        if gamepad_y_out != 0:
                           Gamepad.yAxis(0)
                    else:
                        device.write_event(info)
                    if DEBUG_MODE: 
                        print('Gamepad centering')
                    
def map_joystick(value, deadzone_value, input_value_min, input_value_max, output_value_min, output_value_max):
    # Figure out the range 
    input_span = input_value_max - input_value_min
    output_span = output_value_max - output_value_min

    # Convert the input range into a 0 to 1 range (float value)   
    if (value>=-deadzone_value and value<=deadzone_value):
        value_scaled = 0.5
    elif (value<input_value_min):
        value_scaled = 0.0
    elif (value>input_value_max):
        value_scaled = 1.0
    else:
        value_scaled = float(value - input_value_min) / float(input_span)
    
    # Convert the 0-1 range into a value in the output range
    if value_scaled<=0:
        return output_value_min
    elif value_scaled>=1:
        return output_value_max
    else:
        return int(output_value_min + (value_scaled * output_span))


def main():
    global reaction_time
    reaction_time = float(GAMEPAD_XY.ReactionTimeValue/1000)
    """ Trigger Gamepad with USB or BT mouse and keyboard  """
    # Examine all input devices and find keyboards and mice.
    while len(evdev.list_devices()) == 0:
        if DEBUG_MODE: 
            print("Waiting for keyboard or mice")
        time.sleep(1)
    # Process all keyboard and mouse input events.
    for devpath in evdev.list_devices():
        device = evdev.InputDevice(devpath)
        print(device)
        print(device.path, device.name, device.phys)
        print(device.capabilities(verbose=True))
        if evdev.ecodes.EV_KEY in device.capabilities():
            print('Has EV_KEY')
            print(device.capabilities()[evdev.ecodes.EV_KEY])
            if evdev.ecodes.KEY_A in device.capabilities()[evdev.ecodes.EV_KEY]:
                print('Keyboard', device)
                asyncio.ensure_future(handle_events(device))
            elif evdev.ecodes.BTN_MOUSE in device.capabilities()[evdev.ecodes.EV_KEY]:
                print('Mouse', device)
                asyncio.ensure_future(handle_events(device))

    loop = asyncio.get_event_loop()
    loop.run_forever()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Gamepad.end()
        time.sleep(0.1)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
