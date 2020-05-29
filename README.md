# XFCE-Sensor-Control
A simple Python script to make up for XFCE lacking innate tilt and brightness controls. Uses iio-sensor-proxy.

Written specifically for the Lenovo Yoga 920. Currently would require changing __DEVICE_LIST__ to include the output received from calling xinput listed under Virtual core pointer.

Utilizes iio-sensor-proxy, xinput, and xrandr.
