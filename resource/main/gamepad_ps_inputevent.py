#!/usb/bin/python3

import sys
import asyncio
import time  
import evdev
from enum import IntEnum
from module.gamepad_MF import Gamepad_MF
import yaml

with open("./config/config_ps.yml", "r") as configfile:
    config = yaml.load(configfile, Loader=yaml.FullLoader)
    
Gamepad = Gamepad_MF()
Gamepad.begin('/dev/hidg0')

class PS_BUTTON(IntEnum):
  SQUARE =           0
  CROSS =            1
  CIRCLE =           2
  TRIANGLE =         3
  L1 =               4
  R1 =               5
  L2 =               6
  R2 =               7
  SHARE =            8
  OPTIONS =          9
  L3 =               10
  R3 =               11
  LOGO =             12
  TPAD =             13

mice_x_in = 0
mice_y_in = 0

gamepad_x_out = 0
gamepad_y_out = 0

reaction_time = 0.0

mapEnableDebug = config['MAP_DEBUG']
mapXY = config['MAP_XY']
mapMouse = config['MAP_MOUSE']
mapKeyboard = config['MAP_KEYBOARD']
mapOthers = config['MAP_OTHERS']

inputMinValue = mapXY['INPUT_MIN']
inputMaxValue = mapXY['INPUT_MAX']
deadZoneValue = mapXY['INPUT_DEADZONE']
outputMinValue = mapXY['OUTPUT_MIN']
outputMaxValue = mapXY['OUTPUT_MAX']
operationMode = mapXY['OPERATION_MODE']
reactionTimeValue = mapXY['REACTION_TIME']

# Map keyboard keys or mouse buttons to gamepad buttons.
EVENT2ACTION = {
    'BUTTONS': {
        str(evdev.ecodes.BTN_LEFT):   PS_BUTTON[mapMouse['BTN_LEFT']],
        str(evdev.ecodes.BTN_RIGHT):  PS_BUTTON[mapMouse['BTN_RIGHT']],
        str(evdev.ecodes.BTN_MIDDLE): PS_BUTTON[mapMouse['BTN_MIDDLE']],
        str(evdev.ecodes.BTN_SIDE):   PS_BUTTON[mapMouse['BTN_SIDE']],
        str(evdev.ecodes.BTN_EXTRA):  PS_BUTTON[mapMouse['BTN_EXTRA']],
        str(evdev.ecodes.KEY_A):      PS_BUTTON[mapKeyboard['KEY_A']],
        str(evdev.ecodes.KEY_B):      PS_BUTTON[mapKeyboard['KEY_B']],
        str(evdev.ecodes.KEY_X):      PS_BUTTON[mapKeyboard['KEY_X']],
        str(evdev.ecodes.KEY_Y):      PS_BUTTON[mapKeyboard['KEY_Y']],
        str(evdev.ecodes.KEY_1):      PS_BUTTON[mapKeyboard['KEY_1']],
        str(evdev.ecodes.KEY_2):      PS_BUTTON[mapKeyboard['KEY_2']],
        str(evdev.ecodes.KEY_3):      PS_BUTTON[mapKeyboard['KEY_3']],
        str(evdev.ecodes.KEY_4):      PS_BUTTON[mapKeyboard['KEY_4']],
        str(evdev.ecodes.KEY_5):      PS_BUTTON[mapKeyboard['KEY_5']],
        str(evdev.ecodes.KEY_6):      PS_BUTTON[mapKeyboard['KEY_6']],
        str(evdev.ecodes.KEY_7):      PS_BUTTON[mapKeyboard['KEY_7']],
        str(evdev.ecodes.KEY_8):      PS_BUTTON[mapKeyboard['KEY_8']]
    }, 
    'DIRECTIONS': {
        str(evdev.ecodes.KEY_UP): {"x": mapKeyboard['KEY_UP']['X'], "y": mapKeyboard['KEY_UP']['Y']},
        str(evdev.ecodes.KEY_RIGHT): {"x": mapKeyboard['KEY_RIGHT']['X'], "y": mapKeyboard['KEY_RIGHT']['Y']},
        str(evdev.ecodes.KEY_DOWN): {"x": mapKeyboard['KEY_DOWN']['X'], "y": mapKeyboard['KEY_DOWN']['Y']},
        str(evdev.ecodes.KEY_LEFT): {"x": mapKeyboard['KEY_LEFT']['X'], "y": mapKeyboard['KEY_LEFT']['Y']}
    },
    'OTHERS': {
        str(evdev.ecodes.REL_WHEEL): PS_BUTTON[mapOthers['REL_WHEEL']]
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
                    if mapEnableDebug: 
                        print('Key or button press', 'gamepad button press', gamepad_button)
                    Gamepad.press(gamepad_button)
                    time.sleep(0.05)
                elif event.value == 0:
                    if mapEnableDebug: 
                        print('Key or button release', 'gamepad button release', gamepad_button)
                    Gamepad.release(gamepad_button)
            elif str(event.code) in EVENT2ACTION.get('DIRECTIONS'):
                gamepad_move = EVENT2ACTION.get('DIRECTIONS')[str(event.code)]
                if event.value == 1:
                    if mapEnableDebug: 
                        print('Direction Key press', 'gamepad left axis move', gamepad_move)
                    Gamepad.leftXAxis(gamepad_move['x'])
                    Gamepad.leftYAxis(gamepad_move['y'])
                    time.sleep(0.05)
                elif event.value == 0:
                    if mapEnableDebug: 
                        print('Direction Key release', 'gamepad left axis release', gamepad_move)
                    Gamepad.leftXAxis(0)
                    Gamepad.leftYAxis(0)
            else:
                """ Map mouse motion to thumbstick motion """
                if event.code == evdev.ecodes.REL_X and int(operationMode)== 0 and event.value != 0:
                    mice_x_in = event.value
                    gamepad_x_out = map_joystick(mice_x_in,int(deadZoneValue),int(inputMinValue),int(inputMaxValue),int(outputMinValue),int(outputMaxValue))
                    if mapEnableDebug: 
                        print('REL_X', event.value , 'gamepad left x axis out', gamepad_x_out)
                    Gamepad.leftXAxis(gamepad_x_out)
                if event.code == evdev.ecodes.REL_X and int(operationMode) == 1:
                    mice_x_in = event.value + mice_x_in
                    gamepad_x_out = map_joystick(mice_x_in,int(deadZoneValue),int(inputMinValue),int(inputMaxValue),int(outputMinValue),int(outputMaxValue))
                    if mapEnableDebug: 
                        print('REL_X', event.value , 'gamepad left x axis out', gamepad_x_out)
                    Gamepad.leftXAxis(gamepad_x_out)
                elif event.code == evdev.ecodes.REL_Y and int(operationMode)== 0 and event.value != 0:
                    mice_y_in = event.value
                    gamepad_y_out = map_joystick(mice_y_in,int(deadZoneValue),int(inputMinValue),int(inputMaxValue),int(outputMinValue),int(outputMaxValue))
                    if mapEnableDebug: 
                        print('REL_Y', event.value , 'gamepad left y axis out', gamepad_y_out)
                    Gamepad.leftYAxis(gamepad_y_out)
                elif event.code == evdev.ecodes.REL_Y and int(operationMode)== 1:
                    mice_y_in = event.value + mice_y_in
                    gamepad_y_out = map_joystick(mice_y_in,int(deadZoneValue),int(inputMinValue),int(inputMaxValue),int(outputMinValue),int(outputMaxValue))
                    if mapEnableDebug: 
                        print('REL_Y', event.value , 'gamepad left y axis out', gamepad_y_out)
                    Gamepad.leftYAxis(gamepad_y_out)
                elif event.code == evdev.ecodes.REL_WHEEL:
                    gamepad_button = EVENT2ACTION.get('OTHERS')[str(event.code)]
                    if event.value == 1:
                        Gamepad.press(gamepad_button)
                    elif event.value == -1:
                        Gamepad.release(gamepad_button)
                    if mapEnableDebug: 
                        print('REL_WHEEL', event.value)
                elif event.code == evdev.ecodes.REL_HWHEEL:
                    if mapEnableDebug: 
                        print('REL_HWHEEL', event.value)
                elif event.code == evdev.ecodes.ABS_X and event.value != 0:
                    if mapEnableDebug: 
                        print('ABS_X', event.value)
                elif event.code == evdev.ecodes.ABS_Y and event.value != 0:
                    if mapEnableDebug: 
                        print('ABS_Y', event.value)
                else:
                    time.sleep(reaction_time)
                    info = device.read_one()
                    if(info == None):
                        if gamepad_x_out != 0:
                           Gamepad.leftXAxis(0)
                        if gamepad_y_out != 0:
                           Gamepad.leftYAxis(0)
                    else:
                        device.write_event(info)
                    if mapEnableDebug: 
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


# Examine all input devices and find keyboards and mice.
# Process all keyboard and mouse input events.
def main():
    global reaction_time
    reaction_time = float(reactionTimeValue/1000)
    """ Trigger NS gamepad with USB or BT mouse and keyboard  """
    # Examine all input devices and find keyboards and mice.
    while len(evdev.list_devices()) == 0:
        if mapEnableDebug: 
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
