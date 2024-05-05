import serial
import subprocess
import sys

GREEN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0m'
WARNING = '\033[93m'


if len(sys.argv) < 2:
    print(f"{WARNING}Usage: python script.py <port>{RESET}")
    print(f"{WARNING}You can find the port by running 'ls /dev/tty.*'{RESET}")
    print(f"{WARNING}Mac example: python flash.py /dev/tty.usbmodem14101{RESET}")
    sys.exit(1)

PORT = sys.argv[1]

# use nrfutil to flash the firmware
cmd = [
    "./adafruit-nrfutil",
    "--verbose",
    "dfu",
    "serial",
    "-pkg",
    "./XIAO-ARDUINO-BLE.ino.zip",
    "-p",
    PORT,
    "-b",
    "115200",
    "--singlebank"
]

try:
    # Send the touch reset signal
    ser = serial.Serial(PORT, 1200)
    ser.write(b'\x00' * 16)
    ser.close()

    process = subprocess.run(cmd, check=True)
    if process.returncode == 0:
        print(f"{GREEN}Compass updated successfully.{RESET}")
    else:
        print(f"{RED}Compass update failed.{RESET}")
except Exception as e:
    print(f"{RED}Compass update failed with error:")
    print(e)
    print(RESET)
    print("This is most likely due to an incorrect port. Please check the port, but also don't hesitate to contact us - we can help!")
