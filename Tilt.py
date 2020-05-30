import os
import time
import subprocess

from pydbus import SystemBus

bus = SystemBus()
sensor_proxy = bus.get('net.hadess.SensorProxy')

# Transformation matrices for input
__RIGHT__ = '0 1 0 -1 0 1 0 0 1'
__LEFT__ = '0 -1 1 1 0 0 0 0 1'
__NORMAL__ = '1 0 0 0 1 0 0 0 1'
__INVERTED__ = '-1 0 1 0 -1 1 0 0 1'

# TODO: Figure out how to slap xinput data into here instead of hardcoding. Currently doesn't work for USB mice, nor portable.
__DEVICE_LIST__ = ['SYNA2B31:00 06CB:7F8B Touchpad', 'Wacom HID 5113 Finger touch', 'Wacom HID 5113 Pen stylus',
                   'Wacom HID 5113 Pen eraser', 'SYNA2B31:00 06CB:7F8B Mouse']

__COMMANDS_LEFT__ = ["xrandr -o left"]
__COMMANDS_RIGHT__ = ["xrandr -o right"]
__COMMANDS_NORMAL__ = ["xrandr -o normal"]
__COMMANDS_INVERTED__ = ["xrandr -o inverted"]

# Pre-fills the lists of commands to activate for each orientation
for device in __DEVICE_LIST__:
    __COMMANDS_NORMAL__.append("xinput --set-prop \"" + device +
                               "\" --type=float \"Coordinate Transformation Matrix\" " + __NORMAL__)
    __COMMANDS_LEFT__.append("xinput --set-prop \"" + device +
                             "\" --type=float \"Coordinate Transformation Matrix\" " + __LEFT__)
    __COMMANDS_RIGHT__.append("xinput --set-prop \"" + device +
                              "\" --type=float \"Coordinate Transformation Matrix\" " + __RIGHT__)
    __COMMANDS_INVERTED__.append("xinput --set-prop \"" + device +
                                 "\" --type=float \"Coordinate Transformation Matrix\" " + __INVERTED__)

while True:
    sensor_proxy.ClaimAccelerometer()
    time.sleep(1)  # you have to wait a moment for the accelerometer to give you data
    orientation = str(sensor_proxy.AccelerometerOrientation)
    sensor_proxy.ReleaseAccelerometer()
    commands = []

    if orientation == "normal":
        commands = __COMMANDS_NORMAL__
    elif orientation == "left-up":
        commands = __COMMANDS_LEFT__
    elif orientation == "right-up":
        commands = __COMMANDS_RIGHT__
    elif orientation == "bottom-up":
        commands = __COMMANDS_INVERTED__

    for command in commands:
        subprocess.call(command,
                        shell=True,
                        executable='/bin/bash',
                        stdout=open(os.devnull, 'wb'))
