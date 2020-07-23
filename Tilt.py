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

#!/usr/bin/python3
import os
import time
import subprocess

from pydbus import SystemBus

bus = SystemBus()
sensor_proxy = bus.get('net.hadess.SensorProxy')


def get_pointer_devices():
    devices = subprocess.check_output("xinput --list --name-only",
                                      shell=True,
                                      executable='/bin/sh')
    devices = devices.decode('utf-8').split("\n")

    device_list = []
    i = 1
    while "Virtual core keyboard" != devices[i]:  # Every input device from Virtual core keyboard onward isn't valid
        if "USB" not in devices[i]:  # xrandr handles USB mice.
            device_list.append(devices[i])
            i += 1
        else:
            i += 1

    return device_list


def get_pointer_devices_amount():
    # Doesn't return an actual pointer device count, but if the value returned changes, there's a device change
    return len(subprocess.check_output("xinput --list --name-only",
                                       shell=True,
                                       executable='/bin/sh'))


def generate_commands(devices):
    commands_left = ["xrandr -o left"]
    commands_right = ["xrandr -o right"]
    commands_normal = ["xrandr -o normal"]
    commands_inverted = ["xrandr -o inverted"]

    # Transformation matrices for input
    right = '0 1 0 -1 0 1 0 0 1'
    left = '0 -1 1 1 0 0 0 0 1'
    normal = '1 0 0 0 1 0 0 0 1'
    inverted = '-1 0 1 0 -1 1 0 0 1'

    for device in devices:
        # Commands
        commands_normal.append(generate_command(device, normal))
        commands_left.append(generate_command(device, left))
        commands_right.append(generate_command(device, right))
        commands_inverted.append(generate_command(device, inverted))

    return commands_normal, commands_left, commands_right, commands_inverted


def generate_command(device, orientation_):
    return "xinput --set-prop \"" + device + "\" --type=float \"Coordinate Transformation Matrix\" " + orientation_


def execute_commands(commands_):
    for command in commands_:
        print(command)
        subprocess.call(command,
                        shell=True,
                        executable='/bin/sh',
                        stdout=open(os.devnull, 'wb'))


def get_orientation_value(orientation_):
    orientation_value = 0
    if orientation_ == "normal":
        orientation_value = 0
    elif orientation_ == "left-up":
        orientation_value = 1
    elif orientation_ == "right-up":
        orientation_value = 2
    elif orientation_ == "bottom-up":
        orientation_value = 3
    return orientation_value


device_count = get_pointer_devices_amount()
commands = generate_commands(get_pointer_devices())
orientation_previous = ""
while True:
    # Checks if the command lists need to be updated, and does if so.
    if device_count != get_pointer_devices_amount():
        commands = generate_commands(get_pointer_devices())
        orientation_previous = ""

    sensor_proxy.ClaimAccelerometer()
    # You have to wait a moment for the accelerometer to give you data,
    # sometimes works lower than 1 second but not always
    time.sleep(1)
    orientation = str(sensor_proxy.AccelerometerOrientation)
    sensor_proxy.ReleaseAccelerometer()

    # Should only run this part if the computer orientation changes, or a new device is added.
    if orientation_previous != orientation:
        execute_commands(commands[get_orientation_value(orientation)])
        orientation_previous = orientation
