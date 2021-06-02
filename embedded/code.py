# A four-color-mode macro keypad
# by Casey Doran, but based on all the keybow examples by Sandy Macdonald

import math
import board
from keybow2040 import Keybow2040, number_to_xy, hsv_to_rgb
import usb_cdc

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# config

# dict of scancode tuples to send for keys with the default handler
scancodes = {
    12: (Keycode.RIGHT_CONTROL,),  # for push-to-talk
    15: (Keycode.GUI, Keycode.L),  # Lock
}
# dict of colors for keys when in FIXED modes
fixed_hues = {
    3: 0.45,  # sky blue for code change key
    12: 0,  # red for push-to-talk
    15: 0.19  # yellow for lock key
    # 0: 0.0625,  # peach
    # 1: 0.125,  # goldenrod
    # 2: 0.1875,  # yellow-green
    # 3: 0.25,  # green-yellow
    # 4: 0.3125,  # forest green
    # 5: 0.375,  # teal
    # 6: 0.4375,  # cyan
    # 7: 0.5,  # aqua
    # 8: 0.5625,  # royal blue
    # 9: 0.625,  # dodger blue
    # 10: 0.6875,  # medium slate blue
    # 11: 0.75,  # plum
    # 12: 0.8125,  # magenta
    # 13: 0.875,  # orchid
    # 14: 0.9375,  # fuchsia
    # 15: 1.0,  # red
}

# Constants.
FULLBRIGHT = 1
MINBRIGHT = 0.05

# Color modes (not an enum, sigh)
COLOR_MODE_OFF = 0
COLOR_MODE_FIXED_LOW = 1
COLOR_MODE_FIXED_HIGH = 2
COLOR_MODE_RAINBOW_LOW = 3
COLOR_MODE_RAINBOW_HIGH = 4
LAST_COLOR_MODE_TYPE = 5

# Runtime state.
current_color_mode = COLOR_MODE_OFF
is_pressed = {}  # key state
rainbow_hues = {}  # color state
step = 0  # animation state
string_chunks = []  # chunks of a string read from serial

# utility functions
def draw_bw_key(key):
    if is_pressed[key.number]:
        key.set_led(255, 255, 255)
    else:
        key.set_led(0, 0, 0)


def draw_fixed_key(key, value):
    hue = fixed_hues[key.number]
    r, g, b = hsv_to_rgb(hue, 1, value)
    key.set_led(r, g, b)


def draw_rainbow_key(key, value):
    hue = rainbow_hues[key.number]
    r, g, b = hsv_to_rgb(hue, 1, value)
    key.set_led(r, g, b)


def draw_key(key):
    """ Draw one key."""
    if current_color_mode == COLOR_MODE_OFF:
        draw_bw_key(key)
    elif current_color_mode == COLOR_MODE_FIXED_LOW:
        if key.number in fixed_hues:
            value = MINBRIGHT
            if is_pressed[key.number]:
                value = FULLBRIGHT
            draw_fixed_key(key, value)
        else:
            draw_bw_key(key)
    elif current_color_mode == COLOR_MODE_FIXED_HIGH:
        if key.number in fixed_hues:
            value = FULLBRIGHT
            draw_fixed_key(key, value)
        else:
            draw_bw_key(key)
    elif current_color_mode == COLOR_MODE_RAINBOW_LOW:
        value = MINBRIGHT
        if is_pressed[key.number]:
            value = FULLBRIGHT
        draw_rainbow_key(key, value)
    elif current_color_mode == COLOR_MODE_RAINBOW_HIGH:
        draw_rainbow_key(key, FULLBRIGHT)


def draw_all_keys():
    for key in keys:
        draw_key(key)


def pump_rainbow_hues():
    global step
    step += 1
    for key in keys:
        # Convert the key number to an x/y coordinate to calculate the hue
        # in a matrix style-y.
        x, y = number_to_xy(key.number)

        # Calculate the hue.
        hue = (x + y + (step / 20)) / 8
        hue = hue - int(hue)
        hue = hue - math.floor(hue)
        rainbow_hues[key.number] = hue


def increment_color_mode():
    global current_color_mode
    current_color_mode = (current_color_mode + 1) % LAST_COLOR_MODE_TYPE


# implement special actions
def change_light_mode(key):
    increment_color_mode()
    draw_all_keys()


# register of special actions
special_actions = {
    3: change_light_mode,
}

# Set up Keybow electronics
i2c = board.I2C()
keybow = Keybow2040(i2c)
keys = keybow.keys
console = usb_cdc.serials[0]
# Set up the keyboard and layout
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

# global init:
pump_rainbow_hues()  # do once to have valeus for when we are good to run.

# Per-key init
for key in keys:
    # init with key marked as released
    is_pressed[key.number] = False

    # A pressed handler either sends keys or calls a special func
    @keybow.on_press(key)
    def press_handler(key):

        # note current pressed status
        print("key pressed: ", key.number)
        is_pressed[key.number] = True

        # take a special action if one is registered, or send the scancodes and update the key.
        if key.number in special_actions:
            special_actions[key.number](key)
        else:
            if key.number in scancodes:
                codeset = scancodes[key.number]
                keyboard.press(*codeset)
            draw_key(key)

    # A release handler logs the released status
    @keybow.on_release(key)
    def release_handler(key):
        is_pressed[key.number] = False
        if key.number in scancodes:
            codeset = scancodes[key.number]
            keyboard.release(*codeset)
        draw_key(key)


# Main loop.
while True:
    # Always remember to call keybow.update() on every iteration of your loop!
    keybow.update()

    # Check for messages via serial.
    if console.in_waiting > 0:
        msg = console.read(console.in_waiting)
        string_chunks.append(msg)
        if "\n" in msg or "\r" in msg:
            try:
                strippedmsg = b"".join(string_chunks).strip()
                print("Got line:", strippedmsg)
                key = int(strippedmsg)
                is_pressed[key] = not is_pressed[key]
                draw_key(keys[key])
            except:
                pass
            finally:
                string_chunks.clear()

    # Certain color modes need regular action.
    if (
        current_color_mode == COLOR_MODE_RAINBOW_LOW
        or current_color_mode == COLOR_MODE_RAINBOW_HIGH
    ):
        pump_rainbow_hues()
        # Since current hues are wrong, update all the keys with their new hues
        draw_all_keys()
