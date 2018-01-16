import signal
import sys
import time

from PyMata.pymata import PyMata

def signal_handler(sig, frm):
    print('You pressed Ctrl+C!!!!')
    if firmata is not None:
        firmata.reset()
    sys.exit(0)

if __name__=='__main__':
    firmata = PyMata("/dev/ttyUSB0")

    signal.signal(signal.SIGINT, signal_handler)

    firmata.reset()

    firmata.stepper_config(6400, [2, 5])

    time.sleep(.5)

    firmata.stepper_request_library_version()

    time.sleep(.5)

    print("Stepper Library Version", )
    print(firmata.get_stepper_version())

    firmata.stepper_step(20, 6400)
    firmata.stepper_step(20, 6400)

    firmata.close()