import os
import time
import subprocess

from pydbus import SystemBus

bus = SystemBus()
sensor_proxy = bus.get('net.hadess.SensorProxy')

# Transformation matrices for input
_right = '0 1 0 -1 0 1 0 0 1'
_left = '0 -1 1 1 0 0 0 0 1'
_normal = '1 0 0 0 1 0 0 0 1'
_inverted = '-1 0 1 0 -1 1 0 0 1'


def get_pointer_devices():
    devices = subprocess.check_output("xinput --list --name-only",
                                      shell=True,
                                      executable='/bin/sh')

    devices = devices.decode('utf-8').split("\n")
    device_list_ = []

    i = 1
    while "Virtual core keyboard" != devices[i]:
        device_list_.append(devices[i])
        i += 1

    return device_list_


def generate_commands(devices):
    commands_left = ["xrandr -o left"]
    commands_right = ["xrandr -o right"]
    commands_normal = ["xrandr -o normal"]
    commands_inverted = ["xrandr -o inverted"]

    for device in devices:
        # Commands
        commands_normal.append("xinput --set-prop \"" + device +
                               "\" --type=float \"Coordinate Transformation Matrix\" " + _normal)
        commands_left.append("xinput --set-prop \"" + device +
                             "\" --type=float \"Coordinate Transformation Matrix\" " + _left)
        commands_right.append("xinput --set-prop \"" + device +
                              "\" --type=float \"Coordinate Transformation Matrix\" " + _right)
        commands_inverted.append("xinput --set-prop \"" + device +
                                 "\" --type=float \"Coordinate Transformation Matrix\" " + _inverted)

    return commands_normal, commands_left, commands_right, commands_inverted


# Returns true if a new device is found
def check_new_devices(current_device_list):
    devices = get_pointer_devices()
    if len(devices) != len(current_device_list):
        return True, devices
    else:
        return False, []


device_list = get_pointer_devices()

_commands = generate_commands(device_list)
_commands_normal = _commands[0]
_commands_left = _commands[1]
_commands_right = _commands[2]
_commands_inverted = _commands[3]

while True:
    # Checks if the command lists need to be updated
    device_test = check_new_devices(device_list)
    if device_test[0]:
        device_list = device_test[1]
        _commands = generate_commands(device_list)
        _commands_normal = _commands[0]
        _commands_left = _commands[1]
        _commands_right = _commands[2]
        _commands_inverted = _commands[3]

    sensor_proxy.ClaimAccelerometer()
    time.sleep(1)  # you have to wait a moment for the accelerometer to give you data
    orientation = str(sensor_proxy.AccelerometerOrientation)
    sensor_proxy.ReleaseAccelerometer()
    commands = []

    if orientation == "normal":
        commands = _commands_normal
    elif orientation == "left-up":
        commands = _commands_left
    elif orientation == "right-up":
        commands = _commands_right
    elif orientation == "bottom-up":
        commands = _commands_inverted

    for command in commands:
        subprocess.call(command,
                        shell=True,
                        executable='/bin/bash',
                        stdout=open(os.devnull, 'wb'))
