"""
 Copyright (c) 2015-2017 Alan Yorinks All rights reserved.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""


import asyncio
import glob
import logging
import sys
import time
import math

import serial

from pymata_aio.constants import Constants
from pymata_aio.pin_data import PinData
from pymata_aio.private_constants import PrivateConstants
from pymata_aio.pymata_serial import PymataSerial
from pymata_aio.pymata_socket import PymataSocket


# noinspection PyCallingNonCallable,PyCallingNonCallable,PyPep8,PyBroadException,PyBroadException
class PymataCore:
    """
    This class exposes and implements the pymata_core asyncio API,
    It includes the public API methods as well as
    a set of private methods. If your application is using asyncio,
    this is the API that you should use.

    After instantiating this class, its "start" method MUST be called to
    perform Arduino pin auto-detection.
    """

    def __init__(self, arduino_wait=2, sleep_tune=0.0001, log_output=False,
                 com_port=None, ip_address=None, ip_port=2000,
                 ip_handshake='*HELLO*'):
        """
        This is the "constructor" method for the PymataCore class.

        If log_output is set to True, a log file called 'pymata_log'

        will be created in the current directory and all pymata_aio output
        will be redirected to the log with no output appearing on the console.


        :param arduino_wait: Amount of time to wait for Arduino to reset.
                             UNO takes 2 seconds, Leonardo can be zero
        :param sleep_tune: This parameter sets the amount of time PyMata core
                           uses to set asyncio.sleep
        :param log_output: If false, all output goes to console, else output
                           redirected to log file.
        :param com_port: Manually selected com port - normally it is
                         auto-detected
        :param ip_address: If using a WiFly module, set its address here
        :param ip_port: Port to used with ip_address
        :param ip_handshake: Connectivity handshake string sent by IP device

        :returns: This method never returns
        """
        # check to make sure that Python interpreter is version 3.5 or greater
        python_version = sys.version_info
        if python_version[0] >= 3:
            if python_version[1] >= 5:
                pass
            else:
                print(
                    "ERROR: Python 3.5 or greater is required for use of this program.")

        self.log_output = log_output
        if log_output:
            logging.basicConfig(filename='./pymata_aio.log', filemode='w',
                                level=logging.DEBUG)

        self.sleep_tune = sleep_tune
        self.arduino_wait = arduino_wait
        self.com_port = com_port
        if ip_address == 'None':
            self.ip_address = None
        else:
            self.ip_address = ip_address
        self.ip_port = int(ip_port)
        self.ip_handshake = ip_handshake

        self.hall_encoder = False

        # this dictionary for mapping incoming Firmata message types to
        # handlers for the messages
        self.command_dictionary = {PrivateConstants.REPORT_VERSION:
                                       self._report_version,
                                   PrivateConstants.REPORT_FIRMWARE:
                                       self._report_firmware,
                                   PrivateConstants.CAPABILITY_RESPONSE:
                                       self._capability_response,
                                   PrivateConstants.ANALOG_MAPPING_RESPONSE:
                                       self._analog_mapping_response,
                                   PrivateConstants.PIN_STATE_RESPONSE:
                                       self._pin_state_response,
                                   PrivateConstants.STRING_DATA:
                                       self._string_data,
                                   PrivateConstants.ANALOG_MESSAGE:
                                       self._analog_message,
                                   PrivateConstants.DIGITAL_MESSAGE:
                                       self._digital_message,
                                   PrivateConstants.I2C_REPLY:
                                       self._i2c_reply,
                                   PrivateConstants.SONAR_DATA:
                                       self._sonar_data,
                                   PrivateConstants.ENCODER_DATA:
                                       self._encoder_data,
                                   PrivateConstants.PIXY_DATA:
                                       self._pixy_data,
                                   PrivateConstants.ACCELSTEPPER_DATA:
                                       self._accelstepper_data}
        
        # report query results are stored in this dictionary
        self.query_reply_data = {PrivateConstants.REPORT_VERSION: '',
                                 PrivateConstants.STRING_DATA: '',
                                 PrivateConstants.REPORT_FIRMWARE: '',
                                 PrivateConstants.CAPABILITY_RESPONSE: None,
                                 PrivateConstants.ANALOG_MAPPING_RESPONSE: None,
                                 PrivateConstants.PIN_STATE_RESPONSE: None}

        # An i2c_map entry consists of a device i2c address as the key, and
        #  the value of the key consists of a dictionary containing 3 entries.
        #  The first entry. 'value' contains the last value reported, and
        # the second, 'callback' contains a reference to a callback function.
        # the third, callback_type contains the callback type selector
        #  (None = Direct, 1 = await)
        # For example:
        # {12345: {'value': 23, 'callback': None, 'callback_type: None}}
        self.i2c_map = {}

        # the active_sonar_map maps the sonar trigger pin number (the key)
        # to the current data value returned
        # if a callback was specified, it is stored in the map as well.
        # an entry in the map consists of:
        #   pin: [callback,, callback_type, [current_data_returned]]
        self.active_sonar_map = {}

        # The latch_map is a dictionary that stores all latches setup by
        # the user.
        # The key is a string defined as follows:
        #   Digital Pin : D + pin number (D12)
        #   Analog  Pin: A + pin number (A3)

        # The value associated with each key is a list comprised of:

        # [latched_state, threshold_type,
        #  threshold_value, latched_data, time_stamp]

        # latched_state: Each list entry contains a latch state,
        #                a threshold type, a threshold value value the data
        #                value at time of latching,  and a date stamp
        #                when latched.
        # A latch state:

        # LATCH_IGNORE = 0   # this item currently not participating in latching
        # LATCH_ARMED = 1    # When the next item value change is received and,
        #                    # if it matches the latch
        #                    # criteria, the data will be latched
        # LATCH_LATCHED = 2  # data has been latched. Read the data to
        #                    # re-arm the latch

        # threshold type:
        #     LATCH_EQ = 0  data value is equal to the latch threshold value
        #     LATCH_GT = 1  data value is greater than the latch
        #                   threshold value
        #     LATCH_LT = 2  data value is less than the latch threshold value
        #     LATCH_GTE = 3  data value is greater than or equal to the
        #                    latch threshold value
        #     LATCH_LTE = 4 # data value is less than or equal to the
        #                     latch threshold value

        # threshold value: target threshold data value

        # latched data value: value of data at time of latching event

        # time stamp: time of latching event

        # analog_latch_table entry = pin: [latched_state, threshold_type,
        #                            threshold_value, latched_data, time_stamp]
        # digital_latch_table_entry = pin: [latched_state, threshold_type,
        #                                   latched_data, time_stamp]

        self.latch_map = {}

        if self.log_output:
            log_string = 'pymata_aio Version ' + \
                         PrivateConstants.PYMATA_VERSION + \
                         ' Copyright (c) 2015-2017 Alan Yorinks All rights reserved.'
            logging.info(log_string)
        else:

            print('{}{}{}'.format('\n', 'pymata_aio Version ' +
                                  PrivateConstants.PYMATA_VERSION,
                                  '\tCopyright (c) 2015-2017 Alan Yorinks All '
                                  'rights reserved.\n'))
            sys.stdout.flush()

        if self.com_port is None and self.ip_address is None:
            self.com_port = self._discover_port()
        elif self.ip_address is not None:
            if self.log_output:
                log_string = 'Using Ip Address/Port: ' + self.ip_address + \
                             ':' + str(ip_port)
                logging.info(log_string)
            else:
                print('Using Ip Address/Port: ' +
                      self.ip_address + ':' + str(self.ip_port))

        self.sleep_tune = sleep_tune

        # a list of PinData objects - one for each pin segregate by pin type
        self.analog_pins = []
        self.digital_pins = []
        self.pixy_blocks = []
        self.loop = None
        self.the_task = None
        self.serial_port = None
        self.socket = None

        # The correct reader and writer methods will be set after
        # the system detects if a serial or socket connection was chosen
        self.read = None
        self.write = None

        self.keep_alive_interval = 0
        self.period = 0
        self.margin = 0

        # set up signal handler for controlC
        self.loop = asyncio.get_event_loop()

    def start(self):
        """
        This method must be called immediately after the class is instantiated.
        It instantiates the serial interface and then performs auto pin
        discovery.
        It is intended for use by pymata3 applications that do not
        use asyncio coroutines directly.

        :returns: No return value.
        """

        # check if user specified a socket transport
        if self.ip_address:
            self.socket = PymataSocket(self.ip_address, self.ip_port, self.loop)
            self.loop.run_until_complete((self.socket.start()))
            # set the read and write handles
            self.read = self.socket.read
            self.write = self.socket.write
            for i in range(0, len(self.ip_handshake)):
                self.loop.run_until_complete((self.read()))
        else:
            try:
                self.serial_port = PymataSerial(self.com_port, 57600,
                                                self.sleep_tune,
                                                self.log_output)
                # set the read and write handles
                self.read = self.serial_port.read
                self.write = self.serial_port.write
            except serial.SerialException:
                if self.log_output:
                    log_string = 'Cannot instantiate serial interface: ' \
                                 + self.com_port
                    logging.exception(log_string)
                else:
                    print(
                        'Cannot instantiate serial interface: ' + self.com_port)
                sys.exit(0)

        # wait for arduino to go through a reset cycle if need be
        time.sleep(self.arduino_wait)

        # register the get_command method with the event loop
        # self.loop = asyncio.get_event_loop()
        self.the_task = self.loop.create_task(self._command_dispatcher())

        # get arduino firmware version and print it
        asyncio.ensure_future(self.get_firmware_version())

        firmware_version = self.loop.run_until_complete(self.get_firmware_version())
        if self.log_output:
            log_string = "\nArduino Firmware ID: " + firmware_version
            logging.exception(log_string)
        else:
            print("\nArduino Firmware ID: " + firmware_version)

        # get an analog pin map
        asyncio.ensure_future(self.get_analog_map())

        # try to get an analog report. if it comes back as none - shutdown
        report = self.loop.run_until_complete(self.get_analog_map())
        if not report:
            if self.log_output:
                log_string = '*** Analog map retrieval timed out. ***'

                logging.exception(log_string)
                log_string = '\nDo you have Arduino connectivity and do you ' \
                             'have a Firmata sketch uploaded to the board?'
                logging.exception(log_string)

            else:
                print('*** Analog map retrieval timed out. ***')
                print('\nDo you have Arduino connectivity and do you have a '
                      'Firmata sketch uploaded to the board?')
            try:
                loop = self.loop
                for t in asyncio.Task.all_tasks(loop):
                    t.cancel()
                loop.run_until_complete(asyncio.sleep(.1))
                loop.close()
                loop.stop()
                sys.exit(0)
            except RuntimeError:
                # this suppresses the Event Loop Is Running message, which may
                # be a bug in python 3
                sys.exit(0)
            except TypeError:
                sys.exit(0)

        # custom assemble the pin lists
        logging.debug("pins: " + str(report))
        for pin in report:
            digital_data = PinData()
            self.digital_pins.append(digital_data)
            if pin != Constants.IGNORE:
                analog_data = PinData()
                self.analog_pins.append(analog_data)

        if self.log_output:
            log_string = 'Auto-discovery complete. Found ' + \
                         str(len(self.digital_pins)) + ' Digital Pins and ' + \
                         str(len(self.analog_pins)) + ' Analog Pins'
            logging.info(log_string)
        else:
            print('{} {} {} {} {}'.format('Auto-discovery complete. Found',
                                          len(self.digital_pins),
                                          'Digital Pins and',
                                          len(self.analog_pins),
                                          'Analog Pins\n\n'))

    async def start_aio(self):
        """
        This method must be called immediately after the class is instantiated.
        It instantiates the serial interface and then performs auto pin
        discovery.
        It is intended for use by applications that directly uses asyncio.

        :returns: No return value.
         """

        # pick the desired transport and then setup read and write to
        # point to the correct method for the transport

        # check if user specified a socket transport
        if self.ip_address:
            self.socket = PymataSocket(self.ip_address, self.ip_port, self.loop)
            await self.socket.start()
            # set the read and write handles
            self.read = self.socket.read
            self.write = self.socket.write
            for i in range(0, len(self.ip_handshake)):
                await self.read()

        else:
            try:
                self.serial_port = PymataSerial(self.com_port, 57600,
                                                self.sleep_tune,
                                                self.log_output)

                # set the read and write handles
                self.read = self.serial_port.read
                self.write = self.serial_port.write

            except serial.SerialException:
                if self.log_output:
                    log_string = 'Cannot instantiate serial interface: ' + \
                                 self.com_port
                    logging.exception(log_string)
                else:
                    print(
                        'Cannot instantiate serial interface: ' + self.com_port)
                sys.exit(0)

        # wait for arduino to go through a reset cycle if need be
        time.sleep(self.arduino_wait)

        # register the get_command method with the event loop
        self.loop = asyncio.get_event_loop()
        self.the_task = self.loop.create_task(self._command_dispatcher())

        # get arduino firmware version and print it
        firmware_version = await self.get_firmware_version()
        if not firmware_version:
            if self.log_output:
                log_string = '*** Firmware Version retrieval timed out. ***'

                logging.exception(log_string)
                log_string = '\nDo you have Arduino connectivity and do you ' \
                             'have a Firmata sketch uploaded to the board?'
                logging.exception(log_string)

            else:
                print('*** Firmware Version retrieval timed out. ***')
                print('\nDo you have Arduino connectivity and do you have a '
                      'Firmata sketch uploaded to the board?')
            try:
                loop = self.loop
                for t in asyncio.Task.all_tasks(loop):
                    t.cancel()
                loop.run_until_complete(asyncio.sleep(.1))
                loop.stop()
                loop.close()
                sys.exit(0)
            except RuntimeError:
                self.the_task.cancel()
                time.sleep(1)
                # this suppresses the Event Loop Is Running message,
                # which may be a bug in python 3.4.3
                sys.exit(0)
            except TypeError:
                sys.exit(0)
        if self.log_output:
            log_string = "\nArduino Firmware ID: " + firmware_version
            logging.exception(log_string)
        else:
            print("\nArduino Firmware ID: " + firmware_version)

        # get an analog pin map
        asyncio.ensure_future(self.get_analog_map())

        # try to get an analog report. if it comes back as none - shutdown
        # report = await self.get_analog_map()
        report = await self.get_analog_map()
        if not report:
            if self.log_output:
                log_string = '*** Analog map retrieval timed out. ***'

                logging.exception(log_string)
                log_string = '\nDo you have Arduino connectivity and do you ' \
                             'have a Firmata sketch uploaded to the board?'
                logging.exception(log_string)

            else:
                print('*** Analog map retrieval timed out. ***')
                print('\nDo you have Arduino connectivity and do you have a '
                      'Firmata sketch uploaded to the board?')
            try:
                loop = self.loop
                for t in asyncio.Task.all_tasks(loop):
                    t.cancel()
                loop.run_until_complete(asyncio.sleep(.1))
                loop.stop()
                loop.close()
                sys.exit(0)
            except RuntimeError:
                self.the_task.cancel()
                time.sleep(1)
                # this suppresses the Event Loop Is Running message,
                # which may be a bug in python 3.4.3
                sys.exit(0)
            except TypeError:
                sys.exit(0)

        # custom assemble the pin lists
        for pin in report:
            digital_data = PinData()
            self.digital_pins.append(digital_data)
            if pin != Constants.IGNORE:
                analog_data = PinData()
                self.analog_pins.append(analog_data)

        if self.log_output:
            log_string = 'Auto-discovery complete. Found ' + \
                         str(len(self.digital_pins)) + ' Digital Pins and ' + \
                         str(len(self.analog_pins)) + ' Analog Pins'
            logging.info(log_string)
        else:
            print('{} {} {} {} {}'.format('Auto-discovery complete. Found',
                                          len(self.digital_pins),
                                          'Digital Pins and',
                                          len(self.analog_pins),
                                          'Analog Pins\n\n'))

    async def analog_read(self, pin):
        """
        Retrieve the last data update for the specified analog pin.

        :param pin: Analog pin number (ex. A2 is specified as 2)
        :returns: Last value reported for the analog pin
        """
        return self.analog_pins[pin].current_value

    async def analog_write(self, pin, value):
        """
        Set the selected pin to the specified value.

        :param pin: PWM pin number
        :param value: Pin value (0 - 0x4000)
        :returns: No return value
        """
        if PrivateConstants.ANALOG_MESSAGE + pin < 0xf0:
            command = [PrivateConstants.ANALOG_MESSAGE + pin, value & 0x7f,
                       (value >> 7) & 0x7f]
            await self._send_command(command)
        else:
            await self.extended_analog(pin, value)

    async def digital_read(self, pin):
        """
        Retrieve the last data update for the specified digital pin.

        :param pin: Digital pin number
        :returns: Last value reported for the digital pin
        """
        return self.digital_pins[pin].current_value

    async def digital_pin_write(self, pin, value):
        """
        Set the specified pin to the specified value directly without port manipulation.

        :param pin: pin number
        :param value: pin value
        :returns: No return value
        """

        command = (PrivateConstants.SET_DIGITAL_PIN_VALUE, pin, value)

        await self._send_command(command)

    async def digital_write(self, pin, value):
        """
        Set the specified pin to the specified value.

        :param pin: pin number
        :param value: pin value
        :returns: No return value
        """
        # The command value is not a fixed value, but needs to be calculated
        # using the pin's port number
        port = pin // 8

        calculated_command = PrivateConstants.DIGITAL_MESSAGE + port
        mask = 1 << (pin % 8)
        # Calculate the value for the pin's position in the port mask
        if value == 1:
            PrivateConstants.DIGITAL_OUTPUT_PORT_PINS[port] |= mask
        else:
            PrivateConstants.DIGITAL_OUTPUT_PORT_PINS[port] &= ~mask

        # Assemble the command
        command = (calculated_command,
                   PrivateConstants.DIGITAL_OUTPUT_PORT_PINS[port] & 0x7f,
                   (PrivateConstants.DIGITAL_OUTPUT_PORT_PINS[port] >> 7) & 0x7f)

        await self._send_command(command)

    async def disable_analog_reporting(self, pin):
        """
        Disables analog reporting for a single analog pin.

        :param pin: Analog pin number. For example for A0, the number is 0.
        :returns: No return value
        """
        command = [PrivateConstants.REPORT_ANALOG + pin,
                   PrivateConstants.REPORTING_DISABLE]
        await self._send_command(command)

    async def disable_digital_reporting(self, pin):
        """
        Disables digital reporting. By turning reporting off for this pin,
        Reporting is disabled for all 8 bits in the "port"

        :param pin: Pin and all pins for this port
        :returns: No return value
        """
        port = pin // 8
        command = [PrivateConstants.REPORT_DIGITAL + port,
                   PrivateConstants.REPORTING_DISABLE]
        await self._send_command(command)

    async def encoder_config(self, pin_a, pin_b, cb=None, cb_type=None,
                             hall_encoder=False):
        """
        This command enables the rotary encoder support and will
        enable encoder reporting.

        This command is not part of StandardFirmata. For 2 pin + ground
        encoders, FirmataPlus is required to be used for 2 pin rotary encoder,
        and for hell effect wheel encoder support, FirmataPlusRB is required.

        Encoder data is retrieved by performing a digital_read from pin a
        (encoder pin_a).

        When using 2 hall effect sensors (e.g. 2 wheel robot)
        specify pin_a for 1st encoder and pin_b for 2nd encoder.

        :param pin_a: Encoder pin 1.
        :param pin_b: Encoder pin 2.
        :param cb: callback function to report encoder changes
        :param cb_type: Constants.CB_TYPE_DIRECT = direct call or
                        Constants.CB_TYPE_ASYNCIO = asyncio coroutine
        :param hall_encoder: wheel hall_encoder - set to
                             True to select hall encoder support support.
        :returns: No return value
        """
        # checked when encoder data is returned
        self.hall_encoder = hall_encoder
        data = [pin_a, pin_b]
        if cb:
            self.digital_pins[pin_a].cb = cb
        if cb_type:
            self.digital_pins[pin_a].cb_type = cb_type

        await self._send_sysex(PrivateConstants.ENCODER_CONFIG, data)

    async def encoder_read(self, pin):
        """
        This method retrieves the latest encoder data value

        :param pin: Encoder Pin
        :returns: encoder data value
        """
        return self.digital_pins[pin].current_value

    async def enable_analog_reporting(self, pin):
        """
        Enables analog reporting. By turning reporting on for a single pin,

        :param pin: Analog pin number. For example for A0, the number is 0.
        :returns: No return value
        """
        command = [PrivateConstants.REPORT_ANALOG + pin,
                   PrivateConstants.REPORTING_ENABLE]
        await self._send_command(command)

    async def enable_digital_reporting(self, pin):
        """
        Enables digital reporting. By turning reporting on for all 8 bits
        in the "port" - this is part of Firmata's protocol specification.

        :param pin: Pin and all pins for this port
        :returns: No return value
            """
        port = pin // 8
        command = [PrivateConstants.REPORT_DIGITAL + port,
                   PrivateConstants.REPORTING_ENABLE]
        await self._send_command(command)

    async def extended_analog(self, pin, data):
        """
        This method will send an extended-data analog write command to the
        selected pin.

        :param pin: 0 - 127
        :param data: 0 - 0xfffff
        :returns: No return value
        """
        analog_data = [pin, data & 0x7f, (data >> 7) & 0x7f, (data >> 14) & 0x7f]
        await self._send_sysex(PrivateConstants.EXTENDED_ANALOG, analog_data)

    async def get_analog_latch_data(self, pin):
        """
        A list is returned containing the latch state for the pin, the
        latched value, and the time stamp
        [latched_state, threshold_type, threshold_value,
         latched_data, time_stamp]

        :param pin: Pin number.
        :returns:  [latched_state, threshold_type, threshold_value,
                    latched_data, time_stamp]
        """
        key = 'A' + str(pin)
        if key in self.latch_map:
            entry = self.latch_map.get(key)
            return entry
        else:
            return None

    async def get_analog_map(self):
        """
        This method requests a Firmata analog map query and returns the results.

        :returns: An analog map response or None if a timeout occurs
        """
        # get the current time to make sure a report is retrieved
        current_time = time.time()

        # if we do not have existing report results, send a Firmata
        # message to request one
        if self.query_reply_data.get(
                PrivateConstants.ANALOG_MAPPING_QUERY) is None:
            await self._send_sysex(PrivateConstants.ANALOG_MAPPING_QUERY, None)
            # wait for the report results to return for 2 seconds
            # if the timer expires, shutdown
            while self.query_reply_data.get(
                    PrivateConstants.ANALOG_MAPPING_RESPONSE) is None:
                elapsed_time = time.time()
                if elapsed_time - current_time > 2:
                    return None
                await asyncio.sleep(self.sleep_tune)
        return self.query_reply_data.get(
            PrivateConstants.ANALOG_MAPPING_RESPONSE)

    async def get_capability_report(self):
        """
        This method requests and returns a Firmata capability query report

        :returns: A capability report in the form of a list
        """
        if self.query_reply_data.get(
                PrivateConstants.CAPABILITY_QUERY) is None:
            await self._send_sysex(PrivateConstants.CAPABILITY_QUERY, None)
            while self.query_reply_data.get(
                    PrivateConstants.CAPABILITY_RESPONSE) is None:
                await asyncio.sleep(self.sleep_tune)
        return self.query_reply_data.get(PrivateConstants.CAPABILITY_RESPONSE)

    async def get_digital_latch_data(self, pin):
        """
        A list is returned containing the latch state for the pin, the
        latched value, and the time stamp
        [pin_num, latch_state, latched_value, time_stamp]

        :param pin: Pin number.
        :returns:  [latched_state, threshold_type, threshold_value,
                   latched_data, time_stamp]
        """
        key = 'D' + str(pin)
        if key in self.latch_map:
            entry = self.latch_map.get(key)
            return entry
        else:
            return None

    async def get_firmware_version(self):
        """
        This method retrieves the Firmata firmware version

        :returns: Firmata firmware version
        """
        current_time = time.time()
        if self.query_reply_data.get(PrivateConstants.REPORT_FIRMWARE) == '':
            await self._send_sysex(PrivateConstants.REPORT_FIRMWARE, None)
            while self.query_reply_data.get(
                    PrivateConstants.REPORT_FIRMWARE) == '':
                elapsed_time = time.time()
                if elapsed_time - current_time > 2:
                    return None
                await asyncio.sleep(self.sleep_tune)
        reply = ''
        for x in self.query_reply_data.get(PrivateConstants.REPORT_FIRMWARE):
            reply_data = ord(x)
            if reply_data:
                reply += chr(reply_data)
        self.query_reply_data[PrivateConstants.REPORT_FIRMWARE] = reply
        return self.query_reply_data.get(PrivateConstants.REPORT_FIRMWARE)

    async def get_protocol_version(self):
        """
        This method returns the major and minor values for the protocol
        version, i.e. 2.4

        :returns: Firmata protocol version
        """
        if self.query_reply_data.get(PrivateConstants.REPORT_VERSION) == '':
            await self._send_command([PrivateConstants.REPORT_VERSION])
            while self.query_reply_data.get(
                    PrivateConstants.REPORT_VERSION) == '':
                await asyncio.sleep(self.sleep_tune)
        return self.query_reply_data.get(PrivateConstants.REPORT_VERSION)

    async def get_pin_state(self, pin):
        """
        This method retrieves a pin state report for the specified pin

        :param pin: Pin of interest
        :returns: pin state report
        """
        pin_list = [pin]
        await self._send_sysex(PrivateConstants.PIN_STATE_QUERY, pin_list)
        while self.query_reply_data.get(
                PrivateConstants.PIN_STATE_RESPONSE) is None:
            await asyncio.sleep(self.sleep_tune)
        pin_state_report = self.query_reply_data.get(
            PrivateConstants.PIN_STATE_RESPONSE)
        self.query_reply_data[PrivateConstants.PIN_STATE_RESPONSE] = None
        return pin_state_report

    # noinspection PyMethodMayBeStatic
    async def get_pymata_version(self):
        """
        This method retrieves the PyMata version number

        :returns: PyMata version number.
        """
        return PrivateConstants.PYMATA_VERSION

    # noinspection PyIncorrectDocstring
    async def i2c_config(self, read_delay_time=0):
        """
        NOTE: THIS METHOD MUST BE CALLED BEFORE ANY I2C REQUEST IS MADE
        This method initializes Firmata for I2c operations.

        :param read_delay_time (in microseconds): an optional parameter,
                                                  default is 0
        :returns: No Return Value
        """
        data = [read_delay_time & 0x7f, (read_delay_time >> 7) & 0x7f]
        await self._send_sysex(PrivateConstants.I2C_CONFIG, data)

    async def i2c_read_data(self, address):
        """
        This method retrieves cached i2c data to support a polling mode.

        :param address: I2C device address
        :returns: Last cached value read
        """
        if address in self.i2c_map:
            map_entry = self.i2c_map.get(address)
            data = map_entry.get('value')
            return data
        else:
            return None

    async def i2c_read_request(self, address, register, number_of_bytes,
                               read_type, cb=None, cb_type=None):
        """
        This method requests the read of an i2c device. Results are retrieved
        by a call to i2c_get_read_data(). or by callback.

        If a callback method is provided, when data is received from the
        device it will be sent to the callback method.
        Some devices require that transmission be restarted
        (e.g. MMA8452Q accelerometer).
        Use Constants.I2C_READ | Constants.I2C_RESTART_TX for those cases.

        :param address: i2c device address
        :param register: register number (can be set to zero)
        :param number_of_bytes: number of bytes expected to be returned
        :param read_type: I2C_READ  or I2C_READ_CONTINUOUSLY. I2C_RESTART_TX
                          may be OR'ed when required
        :param cb: Optional callback function to report i2c data as a
                   result of read command
        :param cb_type: Constants.CB_TYPE_DIRECT = direct call or
                        Constants.CB_TYPE_ASYNCIO = asyncio coroutine
        :returns: No return value.
        """
        if address not in self.i2c_map:
            # self.i2c_map[address] = [None, cb]
            self.i2c_map[address] = {'value': None, 'callback': cb,
                                     'callback_type': cb_type}
        data = [address, read_type, register & 0x7f, (register >> 7) & 0x7f,
                number_of_bytes & 0x7f, (number_of_bytes >> 7) & 0x7f]
        await self._send_sysex(PrivateConstants.I2C_REQUEST, data)

    async def i2c_write_request(self, address, args):
        """
        Write data to an i2c device.

        :param address: i2c device address
        :param args: A variable number of bytes to be sent to the device
                     passed in as a list
        :returns: No return value.
        """
        data = [address, Constants.I2C_WRITE]
        for item in args:
            item_lsb = item & 0x7f
            data.append(item_lsb)
            item_msb = (item >> 7) & 0x7f
            data.append(item_msb)
        await self._send_sysex(PrivateConstants.I2C_REQUEST, data)

    async def keep_alive(self, period=1, margin=.3):
        """
        Periodically send a keep alive message to the Arduino.
        Frequency of keep alive transmission is calculated as follows:
        keep_alive_sent = period - (period * margin)


        :param period: Time period between keepalives. Range is 0-10 seconds. 0 disables the keepalive mechanism.
        :param margin: Safety margin to assure keepalives are sent before period expires. Range is 0.1 to 0.9
        :returns: No return value
        """
        if period < 0:
            period = 0
        if period > 10:
            period = 10
        self.period = period
        if margin < .1:
            margin = .1
        if margin > .9:
            margin = .9
        self.margin = margin
        self.keep_alive_interval = [period & 0x7f, (period >> 7) & 0x7f]
        await self._send_sysex(PrivateConstants.SAMPLING_INTERVAL,
                               self.keep_alive_interval)
        while True:
            if self.period:
                await asyncio.sleep(period - (period - (period * margin)))
                await self._send_sysex(PrivateConstants.KEEP_ALIVE,
                                       self.keep_alive_interval)
            else:
                break

    async def play_tone(self, pin, tone_command, frequency, duration):
        """
        This method will call the Tone library for the selected pin.
        It requires FirmataPlus to be loaded onto the arduino

        If the tone command is set to TONE_TONE, then the specified tone will be played.

        Else, if the tone command is TONE_NO_TONE, then any currently playing tone will be disabled.

        :param pin: Pin number
        :param tone_command: Either TONE_TONE, or TONE_NO_TONE
        :param frequency: Frequency of tone
        :param duration: Duration of tone in milliseconds
        :returns: No return value
        """
        # convert the integer values to bytes
        if tone_command == Constants.TONE_TONE:
            # duration is specified
            if duration:
                data = [tone_command, pin, frequency & 0x7f, (frequency >> 7) & 0x7f,
                        duration & 0x7f, (duration >> 7) & 0x7f]

            else:
                data = [tone_command, pin,
                        frequency & 0x7f, (frequency >> 7) & 0x7f, 0, 0]
        # turn off tone
        else:
            data = [tone_command, pin]
        await self._send_sysex(PrivateConstants.TONE_DATA, data)

    async def send_reset(self):
        """
        Send a Sysex reset command to the arduino

        :returns: No return value.
        """
        try:
            await self._send_command([PrivateConstants.SYSTEM_RESET])
        except RuntimeError:
            exit(0)

    async def servo_config(self, pin, min_pulse=544, max_pulse=2400):
        """
        Configure a pin as a servo pin. Set pulse min, max in ms.
        Use this method (not set_pin_mode) to configure a pin for servo
        operation.

        :param pin: Servo Pin.
        :param min_pulse: Min pulse width in ms.
        :param max_pulse: Max pulse width in ms.
        :returns: No return value
        """
        command = [pin, min_pulse & 0x7f, (min_pulse >> 7) & 0x7f, max_pulse & 0x7f,
                   (max_pulse >> 7) & 0x7f]

        await self._send_sysex(PrivateConstants.SERVO_CONFIG, command)

    async def set_analog_latch(self, pin, threshold_type, threshold_value,
                               cb=None, cb_type=None):
        """
        This method "arms" an analog pin for its data to be latched and saved
        in the latching table
        If a callback method is provided, when latching criteria is achieved,
        the callback function is called with latching data notification.

        Data returned in the callback list has the pin number as the
        first element,

        :param pin: Analog pin number
                    (value following an 'A' designator, i.e. A5 = 5
        :param threshold_type: ANALOG_LATCH_GT | ANALOG_LATCH_LT  |
                               ANALOG_LATCH_GTE | ANALOG_LATCH_LTE
        :param threshold_value: numerical value - between 0 and 1023
        :param cb: callback method
        :param cb_type: Constants.CB_TYPE_DIRECT = direct call or
                        Constants.CB_TYPE_ASYNCIO = asyncio coroutine
        :returns: True if successful, False if parameter data is invalid
        """
        if Constants.LATCH_GT <= threshold_type <= Constants.LATCH_LTE:
            key = 'A' + str(pin)
            if 0 <= threshold_value <= 1023:
                self.latch_map[key] = [Constants.LATCH_ARMED, threshold_type,
                                       threshold_value, 0, 0, cb, cb_type]
                return True
        else:
            return False

    async def set_digital_latch(self, pin, threshold_value, cb=None,
                                cb_type=None):
        """
        This method "arms" a digital pin for its data to be latched and
        saved in the latching table
        If a callback method is provided, when latching criteria is achieved,
        the callback function is called with latching data notification.

        Data returned in the callback list has the pin number as the
        first element,

        :param pin: Digital pin number
        :param threshold_value: 0 or 1
        :param cb: callback function
        :param cb_type: Constants.CB_TYPE_DIRECT = direct call or
                        Constants.CB_TYPE_ASYNCIO = asyncio coroutine
        :returns: True if successful, False if parameter data is invalid
        """
        if 0 <= threshold_value <= 1:
            key = 'D' + str(pin)
            self.latch_map[key] = [Constants.LATCH_ARMED, Constants.LATCH_EQ,
                                   threshold_value, 0, 0, cb, cb_type]
            return True
        else:
            return False

    async def set_pin_mode(self, pin_number, pin_state, callback=None,
                           callback_type=None):
        """
        This method sets the pin mode for the specified pin.
        For Servo, use servo_config() instead.

        :param pin_number: Arduino Pin Number
        :param pin_state: INPUT/OUTPUT/ANALOG/PWM - for SERVO use
                          servo_config()
        :param callback: Optional: A reference to a call back function to be
                         called when pin data value changes
        :param callback_type: Constants.CB_TYPE_DIRECT = direct call or
                        Constants.CB_TYPE_ASYNCIO = asyncio coroutine
        :returns: No return value
        """

        # There is a potential start up race condition when running pymata3.
        # This is a workaround for that race condition
        #
        if not len(self.digital_pins):
            await asyncio.sleep(2)
        if callback:
            if pin_state == Constants.INPUT:
                self.digital_pins[pin_number].cb = callback
                self.digital_pins[pin_number].cb_type = callback_type
            elif pin_state == Constants.ANALOG:
                self.analog_pins[pin_number].cb = callback
                self.analog_pins[pin_number].cb_type = callback_type
            else:
                if self.log_output:
                    log_string = 'set_pin_mode: callback ignored for ' \
                                 'pin state: ' + pin_state
                    logging.info(log_string)
                else:
                    print('{} {}'.format('set_pin_mode: callback ignored for '
                                         'pin state:', pin_state))

        pin_mode = pin_state
        command = [PrivateConstants.SET_PIN_MODE, pin_number, pin_mode]
        await self._send_command(command)
        if pin_state == Constants.ANALOG:
            await self.enable_analog_reporting(pin_number)
        elif pin_state == Constants.INPUT:
            await self.enable_digital_reporting(pin_number)
        else:
            pass

    async def set_sampling_interval(self, interval):
        """
        This method sends the desired sampling interval to Firmata.
        Note: Standard Firmata  will ignore any interval less than
              10 milliseconds

        :param interval: Integer value for desired sampling interval
                         in milliseconds
        :returns: No return value.
        """
        data = [interval & 0x7f, (interval >> 7) & 0x7f]
        await self._send_sysex(PrivateConstants.SAMPLING_INTERVAL, data)

    async def shutdown(self):
        """
        This method attempts an orderly shutdown
        If any exceptions are thrown, just ignore them.

        :returns: No return value
        """

        if self.log_output:
            logging.info('Shutting down ...')
        else:
            print('Shutting down ...')

        await self.send_reset()

        try:
            self.loop.stop()
        except:
            pass
        try:
            self.loop.close()
        except:
            pass
        sys.exit(0)

    async def sleep(self, sleep_time):
        """
        This method is a proxy method for asyncio.sleep

        :param sleep_time: Sleep interval in seconds
        :returns: No return value.
        """
        try:
            await asyncio.sleep(sleep_time)
        except RuntimeError:
            if self.log_output:
                logging.info('sleep exception')
            else:
                print('sleep exception')
            self.shutdown()

    async def sonar_config(self, trigger_pin, echo_pin, cb=None,
                           ping_interval=50, max_distance=200, cb_type=None):
        """
        Configure the pins,ping interval and maximum distance for an HC-SR04
        type device.
        Single pin configuration may be used. To do so, set both the trigger
        and echo pins to the same value.
        Up to a maximum of 6 SONAR devices is supported
        If the maximum is exceeded a message is sent to the console and the
        request is ignored.
        NOTE: data is measured in centimeters

        :param trigger_pin: The pin number of for the trigger (transmitter).
        :param echo_pin: The pin number for the received echo.
        :param cb: optional callback function to report sonar data changes
        :param ping_interval: Minimum interval between pings. Lowest number
                              to use is 33 ms.Max is 127
        :param max_distance: Maximum distance in cm. Max is 200.
        :param cb_type: Constants.CB_TYPE_DIRECT = direct call or
                        Constants.CB_TYPE_ASYNCIO = asyncio coroutine
        :returns: No return value.
        """
        # if there is an entry for the trigger pin in existence, just exit
        if trigger_pin in self.active_sonar_map:
            return

        if max_distance > 200:
            max_distance = 200
        max_distance_lsb = max_distance & 0x7f
        max_distance_msb = (max_distance >> 7) & 0x7f
        data = [trigger_pin, echo_pin, ping_interval, max_distance_lsb,
                max_distance_msb]
        await self.set_pin_mode(trigger_pin, Constants.SONAR, Constants.INPUT)
        await self.set_pin_mode(echo_pin, Constants.SONAR, Constants.INPUT)
        # update the ping data map for this pin
        if len(self.active_sonar_map) > 6:
            if self.log_output:
                logging.exception('sonar_config: maximum number of '
                                  'devices assigned - ignoring request')
            else:
                print('sonar_config: maximum number of devices assigned'
                      ' - ignoring request')
        else:
            self.active_sonar_map[trigger_pin] = [cb, cb_type, 0]

        await self._send_sysex(PrivateConstants.SONAR_CONFIG, data)

    async def sonar_data_retrieve(self, trigger_pin):
        """
        Retrieve Ping (HC-SR04 type) data. The data is presented as a
        dictionary.
        The 'key' is the trigger pin specified in sonar_config()
        and the 'data' is the current measured distance (in centimeters)
        for that pin. If there is no data, the value is set to None.

        :param trigger_pin: key into sonar data map
        :returns: active_sonar_map
        """
        # sonar_pin_entry = self.active_sonar_map[pin]
        sonar_pin_entry = self.active_sonar_map.get(trigger_pin)
        value = sonar_pin_entry[1]
        return value

    async def accelstepper_config(self, motor_number, motor_type, microstepping,
            enable_pin_present, stepper_pins):
        """
        Configure stepper motor prior to operation.
        This is a FirmataPlus feature.

        :param motor_number: identifier for motor [0-9]
        :param motor_type: electronic interface with motor - 1 = driver, 2 = two-wire, 3 = three-wire, 4 = four-wire
        :param microstepping: level of microstepping, denominator only, e.g. 64 = 1/64th microstepping
        :param enable_pin_present: does the motor have an enable pin? [0,1]
        :param stepper_pins: list of pin numbers necessary for driving stepper
        :returns: No return value.
        """
        logging.debug("stepper config info")
        logging.debug("motor_type: " + str(motor_type))
        logging.debug("motor_type after shifting: " + str(motor_type << 4))
        logging.debug("microstepping: " + str(microstepping))
        logging.debug("microstepping base2 shifted: " + str(int(math.log(microstepping,2)) << 1))
        logging.debug("enable_pin_present: " + str(enable_pin_present))
        interface_byte = (motor_type << 4) + \
            ( int(math.log(microstepping,2)) << 1) + enable_pin_present
        logging.debug("interface_byte: " + str(interface_byte))
        data = [PrivateConstants.ACCELSTEPPER_CONFIGURE, motor_number, 
            interface_byte]
        for pin in range(len(stepper_pins)):
            data.append(stepper_pins[pin])
        logging.debug("stepper_config_data: " + str(data))
        await self._send_sysex(PrivateConstants.ACCELSTEPPER_DATA, data)

    async def accelstepper_zero(self, motor_number):
        """
        Set the current position of the stepper motor as the zero point.

        :param motor_number: identifier for motor [0-9]
        :returns: No return value.
        """
        data = [PrivateConstants.ACCELSTEPPER_ZERO, motor_number]
        logging.debug("stepper_zero_data: " + str(data))
        await self._send_sysex(PrivateConstants.ACCELSTEPPER_DATA, data)

    async def accelstepper_step(self, motor_number, number_of_steps):
        """
        Move a stepper motor for the number of steps at the specified speed
        This is a FirmataPlus feature.

        :param motor_number: identifier for motor [0-9]
        :param number_of_steps: 32 bits for number of steps & direction
                                positive (0 sign bit) is forward, negative (1 sign bit) is reverse
                                sign should be MSB
        :returns: No return value.
        """
        data = [PrivateConstants.ACCELSTEPPER_STEP, motor_number, 
                number_of_steps & 0x7f, (number_of_steps >> 7) & 0x7f,
                (number_of_steps >> 14) & 0x7f, (number_of_steps >> 21) & 0x7f,
                (number_of_steps >> 28) & 0x0f]
        logging.debug("stepper_step_data: " + str(data))
        await self._send_sysex(PrivateConstants.ACCELSTEPPER_DATA, data)

    async def accelstepper_set_speed(self, motor_number, speed):
        """
        Set the (max) speed of a stepper motor.
        This is a FirmataPlus feature.

        :param motor_number: identifier for motor [0-9]
        :param speed: 28 bits in accelStepperFirmata's custom float format
            23 bits for a mantissa, 4 for a scientific notation
            exponent, and one for a sign (1 = negative)
        :returns: No return value.
        """
        data = [PrivateConstants.ACCELSTEPPER_SET_SPEED, motor_number, 
                speed & 0x7f, (speed >> 7) & 0x7f,
                (speed >> 14) & 0x7f, (speed >> 21) & 0x7f]
        logging.debug("stepper_ste_speed:" + str(data))
        await self._send_sysex(PrivateConstants.ACCELSTEPPER_DATA, data)

    async def accelstepper_stop(self, motor_number):
        """
        Immediately halt the movement of a stepper motor.
        This is a FirmataPlus feature.

        :param motor_number: identifier for motor [0-9]
        :returns: No return value.
        """
        data = [PrivateConstants.ACCELSTEPPER_STOP, motor_number]
        await self._send_sysex(PrivateConstants.ACCELSTEPPER_DATA, data)

    async def accelstepper_report_position(self, motor_number):
        """
        Report the motor's position, relative to the zero point.

        :param motor_number: identifier for motor [0-9]
        :returns: No return value.
        """
        data = [PrivateConstants.ACCELSTEPPER_REPORT_POSITION, motor_number]
        await self._send_sysex(PrivateConstants.ACCELSTEPPER_DATA, data)

    async def stepper_config(self, steps_per_revolution, stepper_pins):
        """
        Configure stepper motor prior to operation.
        This is a FirmataPlus feature.
        
        :param steps_per_revolution: number of steps per motor revolution
        :param stepper_pins: a list of control pin numbers - either 4 or 2
        :returns: No return value.
        """
        data = [PrivateConstants.STEPPER_CONFIGURE, steps_per_revolution & 0x7f,
            (steps_per_revolution >> 7) & 0x7f]
        for pin in range(len(stepper_pins)):
            data.append(stepper_pins[pin])
        await self._send_sysex(PrivateConstants.STEPPER_DATA, data)
    
    async def stepper_step(self, motor_speed, number_of_steps):
        """
        Move a stepper motor for the number of steps at the specified speed
        This is a FirmataPlus feature.

        :param motor_speed: 21 bits of data to set motor speed
        :param number_of_steps: 14 bits for number of steps & direction
                                positive is forward, negative is reverse
        :returns: No return value.
        """
        if number_of_steps > 0:
            direction = 1
        else:
            direction = 0
        abs_number_of_steps = abs(number_of_steps)
        data = [PrivateConstants.STEPPER_STEP, motor_speed & 0x7f,
                (motor_speed >> 7) & 0x7f, (motor_speed >> 14) & 0x7f,
                abs_number_of_steps & 0x7f, (abs_number_of_steps >> 7) & 0x7f, direction]
        await self._send_sysex(PrivateConstants.STEPPER_DATA, data)

    async def pixy_init(self, max_blocks=5, cb=None, cb_type=None):
        """
        Initialize Pixy and enable Pixy block reporting.
        This is a FirmataPlusRB feature.

        :param cb: callback function to report Pixy blocks
        :param cb_type: Constants.CB_TYPE_DIRECT = direct call or
                        Constants.CB_TYPE_ASYNCIO = asyncio coroutine
        :param max_blocks: Maximum number of Pixy blocks to report when many signatures are found.
        :returns: No return value.
        """
        if cb:
            self.digital_pins[PrivateConstants.PIN_PIXY_MOSI].cb = cb  # Pixy uses SPI.  Pin 11 is MOSI.
        if cb_type:
            self.digital_pins[PrivateConstants.PIN_PIXY_MOSI].cb_type = cb_type
        data = [PrivateConstants.PIXY_INIT, max_blocks & 0x7f]
        await self._send_sysex(PrivateConstants.PIXY_CONFIG, data)

    async def pixy_set_servos(self, s0, s1):
        """
        Sends the setServos Pixy command.
        This method sets the pan/tilt servos that are plugged into Pixy's two servo ports.

        :param s0: value 0 to 1000
        :param s1: value 0 to 1000
        :returns: No return value.
        """
        data = [PrivateConstants.PIXY_SET_SERVOS, s0 & 0x7f, (s0 >> 7) & 0x7f, s1 & 0x7f, (s1 >> 7) & 0x7f]
        await self._send_sysex(PrivateConstants.PIXY_CONFIG, data)

    async def pixy_set_brightness(self, brightness):
        """
        Sends the setBrightness Pixy command.
        This method sets the brightness (exposure) of Pixy's camera.

        :param brightness: range between 0 and 255 with 255 being the brightest setting
        :returns: No return value.
        """
        data = [PrivateConstants.PIXY_SET_BRIGHTNESS, brightness & 0x7f, (brightness >> 7) & 0x7f]
        await self._send_sysex(PrivateConstants.PIXY_CONFIG, data)

    async def pixy_set_led(self, r, g, b):
        """
        Sends the setLed Pixy command.
        This method sets the RGB LED on front of Pixy.

        :param r: red range between 0 and 255
        :param g: green range between 0 and 255
        :param b: blue range between 0 and 255
        :returns: No return value.
        """
        data = [PrivateConstants.PIXY_SET_LED, r & 0x7f, (r >> 7) & 0x7f, g & 0x7f, (g >> 7) & 0x7f, b & 0x7f,
                (b >> 7) & 0x7f]
        await self._send_sysex(PrivateConstants.PIXY_CONFIG, data)

    async def _command_dispatcher(self):
        """
        This is a private method.
        It continually accepts and interprets data coming from Firmata,and then
        dispatches the correct handler to process the data.

        :returns: This method never returns
        """
        # sysex commands are assembled into this list for processing
        sysex = []

        while True:
            try:
                next_command_byte = await self.read()
                # if this is a SYSEX command, then assemble the entire
                # command process it
                if next_command_byte == PrivateConstants.START_SYSEX:
                    while next_command_byte != PrivateConstants.END_SYSEX:
                        await asyncio.sleep(self.sleep_tune)
                        next_command_byte = await self.read()
                        sysex.append(next_command_byte)
                    logging.debug("Incoming:")
                    logging.debug(str(sysex))
                    logging.debug(str(self.command_dictionary[sysex[0]]))
                    await self.command_dictionary[sysex[0]](sysex)
                    sysex = []
                    await asyncio.sleep(self.sleep_tune)
                # if this is an analog message, process it.
                elif 0xE0 <= next_command_byte <= 0xEF:
                    # analog message
                    # assemble the entire analog message in command
                    command = []
                    # get the pin number for the message
                    pin = next_command_byte & 0x0f
                    command.append(pin)
                    # get the next 2 bytes for the command
                    command = await self._wait_for_data(command, 2)
                    logging.debug("Incoming:")
                    logging.debug(str(next_command_byte))
                    logging.debug(str(command))
                    # process the analog message
                    await self._analog_message(command)
                # handle the digital message
                elif 0x90 <= next_command_byte <= 0x9F:
                    command = []
                    pin = next_command_byte & 0x0f
                    command.append(pin)
                    command = await self._wait_for_data(command, 2)
                    logging.debug("Incoming:")
                    logging.debug(str(command))
                    await self._digital_message(command)
                # handle all other messages by looking them up in the
                # command dictionary
                elif next_command_byte in self.command_dictionary:
                    await self.command_dictionary[next_command_byte]()
                    await asyncio.sleep(self.sleep_tune)
                else:
                    # we need to yield back to the loop
                    await asyncio.sleep(self.sleep_tune)
                    continue
            except Exception as ex:
                # A error occurred while transmitting the Firmata message, message arrived invalid.
                if self.log_output:
                    logging.exception(ex)
                else:
                    print(ex)
                await self.shutdown()

                await self.serial_port.close()

                print("An exception occurred on the asyncio event loop while receiving data.  Invalid message.")
                loop = self.loop
                for t in asyncio.Task.all_tasks(loop):
                    t.cancel()
                loop.run_until_complete(asyncio.sleep(.1))
                loop.close()
                loop.stop()
                sys.exit(0)

    '''
    Firmata message handlers
    '''

    async def _analog_mapping_response(self, data):
        """
        This is a private message handler method.
        It is a message handler for the analog mapping response message

        :param data: response data
        :returns: none - but saves the response
        """
        self.query_reply_data[PrivateConstants.ANALOG_MAPPING_RESPONSE] = \
            data[1:-1]

    async def _analog_message(self, data):
        """
        This is a private message handler method.
        It is a message handler for analog messages.

        :param data: message data
        :returns: None - but saves the data in the pins structure
        """
        pin = data[0]
        value = (data[PrivateConstants.MSB] << 7) + data[PrivateConstants.LSB]
        # if self.analog_pins[pin].current_value != value:
        # There seems to be a problem of the board sending info about pins
        # during startup before pymata has time to populate the pin list.
        try:
            self.analog_pins[pin].current_value = value

            # append pin number, pin value, and pin type to return value and return as a list
            message = [pin, value, Constants.ANALOG]

            if self.analog_pins[pin].cb:
                if self.analog_pins[pin].cb_type:
                    await self.analog_pins[pin].cb(message)
                else:
                    loop = self.loop
                    loop.call_soon(self.analog_pins[pin].cb, message)
        except IndexError:
            pass

        # is there a latch entry for this pin?
        key = 'A' + str(pin)
        if key in self.latch_map:
            await self._check_latch_data(key, message[1])

    async def _capability_response(self, data):
        """
        This is a private message handler method.
        It is a message handler for capability report responses.

        :param data: capability report
        :returns: None - but report is saved
        """
        self.query_reply_data[PrivateConstants.CAPABILITY_RESPONSE] = data[1:-1]

    async def _digital_message(self, data):
        """
        This is a private message handler method.
        It is a message handler for Digital Messages.

        :param data: digital message

        :returns: None - but update is saved in pins structure
        """
        port = data[0]
        port_data = (data[PrivateConstants.MSB] << 7) + \
                    data[PrivateConstants.LSB]
        pin = port * 8
        for pin in range(pin, min(pin + 8, len(self.digital_pins))):
            # get pin value
            value = port_data & 0x01

            # set the current value in the pin structure
            self.digital_pins[pin].current_value = value

            # append pin number, pin value, and pin type to return value and return as a list
            message = [pin, value, Constants.INPUT]

            if self.digital_pins[pin].cb:
                if self.digital_pins[pin].cb_type:
                    await self.digital_pins[pin].cb(message)
                else:
                    # self.digital_pins[pin].cb(data)
                    loop = self.loop
                    loop.call_soon(self.digital_pins[pin].cb, message)

                # is there a latch entry for this pin?
                key = 'D' + str(pin)
                if key in self.latch_map:
                    await self._check_latch_data(key, port_data & 0x01)
            port_data >>= 1

    async def _encoder_data(self, data):
        """
        This is a private message handler method.
        It handles encoder data messages.

        :param data: encoder data
        :returns: None - but update is saved in the digital pins structure
        """
        # strip off sysex start and end
        data = data[1:-1]
        pin = data[0]
        if not self.hall_encoder:
            val = int((data[PrivateConstants.MSB] << 7) +
                      data[PrivateConstants.LSB])
            # set value so that it shows positive and negative values
            if val > 8192:
                val -= 16384
            # if this value is different that is what is already in the
            # table store it and check for callback
            if val != self.digital_pins[pin].current_value:
                self.digital_pins[pin].current_value = val
                if self.digital_pins[pin].cb:
                    # self.digital_pins[pin].cb([pin, val])
                    if self.digital_pins[pin].cb_type:
                        await self.digital_pins[pin].cb(val)
                    else:
                        # self.digital_pins[pin].cb(data)
                        loop = self.loop
                        loop.call_soon(self.digital_pins[pin].cb, val)
        else:
            hall_data = [int((data[2] << 7) + data[1]), int((data[5] << 7) +
                                                            data[4])]

            if self.digital_pins[pin].cb_type:
                await self.digital_pins[pin].cb(hall_data)
            else:
                # self.digital_pins[pin].cb(data)
                loop = self.loop
                loop.call_soon(self.digital_pins[pin].cb, hall_data)

    # noinspection PyDictCreation
    async def _pixy_data(self, data):
        """
        This is a private message handler method.
        It handles pixy data messages.

        :param data: pixy data
        :returns: None - but update is saved in the digital pins structure
        """
        if len(self.digital_pins) < PrivateConstants.PIN_PIXY_MOSI:
            # Pixy data sent before board finished pin discovery.
            # print("Pixy data sent before board finished pin discovery.")
            return

        # strip off sysex start and end
        data = data[1:-1]
        num_blocks = data[0]  # First byte is the number of blocks.
        # Prepare the new blocks list and then used it to overwrite the pixy_blocks.
        blocks = []
        # noinspection PyDictCreation
        for i in range(num_blocks):
            block = {}
            block["signature"] = int((data[i * 12 + 2] << 7) + data[i * 12 + 1])
            block["x"] = int((data[i * 12 + 4] << 7) + data[i * 12 + 3])
            block["y"] = int((data[i * 12 + 6] << 7) + data[i * 12 + 5])
            block["width"] = int((data[i * 12 + 8] << 7) + data[i * 12 + 7])
            block["height"] = int((data[i * 12 + 10] << 7) + data[i * 12 + 9])
            block["angle"] = int((data[i * 12 + 12] << 7) + data[i * 12 + 11])
            blocks.append(block)
        self.pixy_blocks = blocks
        if self.digital_pins[PrivateConstants.PIN_PIXY_MOSI].cb:
            if self.digital_pins[PrivateConstants.PIN_PIXY_MOSI].cb_type:
                await self.digital_pins[PrivateConstants.PIN_PIXY_MOSI].cb(blocks)
            else:
                loop = self.loop
                loop.call_soon(self.digital_pins[PrivateConstants.PIN_PIXY_MOSI].cb, blocks)

    async def _accelstepper_data(self, data):
        """
        This is a private message handler method.
        It handles accelStepper data messages.

        :param data: accelStepper data
        """
        # strip off ACCELSTEPPER_DATA start and SYSEX end
        data = data[1:-1]
        # Check next byte to determine type of message
        if int(data[0]) == 0x0b:
            # move complete message
            position = data[1] + (data[2] << 7) + (data[3] << 14) + \
                    (data[4] << 21) + ( (data[5] & 0x07) << 28 )
            sign_bit = data[5] & 0x08
            if sign_bit:
                position = position * -1
            print("Position: " + str(position))
        elif int(data[0]) == 0x06:
            # response to position request
            position = data[1] + (data[2] << 7) + (data[3] << 14) + \
                    (data[4] << 21) + ( (data[5] & 0x07) << 28 )
            sign_bit = data[5] & 0x08
            if sign_bit:
                position = position * -1
            print("Position: " + str(position))

    async def _i2c_reply(self, data):
        """
        This is a private message handler method.
        It handles replies to i2c_read requests. It stores the data
        for each i2c device address in a dictionary called i2c_map.
        The data may be retrieved via a polling call to i2c_get_read_data().
        It a callback was specified in pymata.i2c_read, the raw data is sent
        through the callback

        :param data: raw data returned from i2c device
        """
        # remove the start and end sysex commands from the data
        data = data[1:-1]
        reply_data = []
        # reassemble the data from the firmata 2 byte format
        address = (data[0] & 0x7f) + (data[1] << 7)

        # if we have an entry in the i2c_map, proceed
        if address in self.i2c_map:
            # get 2 bytes, combine them and append to reply data list
            for i in range(0, len(data), 2):
                combined_data = (data[i] & 0x7f) + (data[i + 1] << 7)
                reply_data.append(combined_data)

            # place the data in the i2c map without storing the address byte or
            #  register byte (returned data only)
            map_entry = self.i2c_map.get(address)
            map_entry['value'] = reply_data[2:]
            self.i2c_map[address] = map_entry
            cb = map_entry.get('callback')
            cb_type = map_entry.get('callback_type')
            if cb:
                # send everything, including address and register bytes back
                # to caller
                if cb_type:
                    await cb(reply_data)
                else:
                    loop = self.loop
                    loop.call_soon(cb, reply_data)
                await asyncio.sleep(self.sleep_tune)

    async def _pin_state_response(self, data):
        """
        This is a private message handler method.
        It handles pin state query response messages.

        :param data: Pin state message
        :returns: None - but response is saved
        """
        self.query_reply_data[PrivateConstants.PIN_STATE_RESPONSE] = data[1:-1]

    async def _report_firmware(self, sysex_data):
        """
        This is a private message handler method.
        This method handles the sysex 'report firmware' command sent by
        Firmata (0x79).
        It assembles the firmware version by concatenating the major and
         minor version number components and
        the firmware identifier into a string.
        e.g. "2.3 StandardFirmata.ino"

        :param sysex_data: Sysex data sent from Firmata
        :returns: None
        """
        # first byte after command is major number
        major = sysex_data[1]
        version_string = str(major)

        # next byte is minor number
        minor = sysex_data[2]

        # append a dot to major number
        version_string += '.'

        # append minor number
        version_string += str(minor)
        # add a space after the major and minor numbers
        version_string += ' '

        # slice the identifier - from the first byte after the minor
        #  number up until, but not including the END_SYSEX byte

        name = sysex_data[3:-1]

        # convert the identifier to printable text and add each character
        # to the version string
        for e in name:
            version_string += chr(e)
        
        # store the value
        self.query_reply_data[PrivateConstants.REPORT_FIRMWARE] = version_string

    async def _report_version(self):
        """
        This is a private message handler method.
        This method reads the following 2 bytes after the report version
        command (0xF9 - non sysex).
        The first byte is the major number and the second byte is the
        minor number.

        :returns: None
        """
        # get next two bytes
        major = await self.read()
        version_string = str(major)
        minor = await self.read()
        version_string += '.'
        version_string += str(minor)
        self.query_reply_data[PrivateConstants.REPORT_VERSION] = version_string

    async def _sonar_data(self, data):
        """
        This method handles the incoming sonar data message and stores
        the data in the response table.

        :param data: Message data from Firmata
        :returns: No return value.
        """

        # strip off sysex start and end
        data = data[1:-1]
        pin_number = data[0]
        val = int((data[PrivateConstants.MSB] << 7) +
                  data[PrivateConstants.LSB])
        reply_data = []

        sonar_pin_entry = self.active_sonar_map[pin_number]

        if sonar_pin_entry[0] is not None:
            # check if value changed since last reading
            if sonar_pin_entry[2] != val:
                sonar_pin_entry[2] = val
                self.active_sonar_map[pin_number] = sonar_pin_entry
                # Do a callback if one is specified in the table
                if sonar_pin_entry[0]:
                    # if this is an asyncio callback type
                    reply_data.append(pin_number)
                    reply_data.append(val)
                    if sonar_pin_entry[1]:
                        await sonar_pin_entry[0](reply_data)
                    else:
                        # sonar_pin_entry[0]([pin_number, val])
                        loop = self.loop
                        loop.call_soon(sonar_pin_entry[0], reply_data)
        # update the data in the table with latest value
        else:
            sonar_pin_entry[1] = val
            self.active_sonar_map[pin_number] = sonar_pin_entry

        await asyncio.sleep(self.sleep_tune)

    async def _string_data(self, data):
        """
        This is a private message handler method.
        It is the message handler for String data messages that will be
        printed to the console.
        :param data:  message
        :returns: None - message is sent to console
        """
        reply = ''
        data = data[1:-1]
        for x in data:
            reply_data = x
            if reply_data:
                reply += chr(reply_data)
        if self.log_output:
            logging.info(reply)
        else:
            print(reply)

    '''
    utilities
    '''

    async def _check_latch_data(self, key, data):
        """
        This is a private utility method.
        When a data change message is received this method checks to see if
        latching needs to be processed

        :param key: encoded pin number
        :param data: data change
        :returns: None
        """
        process = False
        latching_entry = self.latch_map.get(key)
        if latching_entry[Constants.LATCH_STATE] == Constants.LATCH_ARMED:
            # Has the latching criteria been met
            if latching_entry[Constants.LATCHED_THRESHOLD_TYPE] == \
                    Constants.LATCH_EQ:
                if data == latching_entry[Constants.LATCH_DATA_TARGET]:
                    process = True
            elif latching_entry[Constants.LATCHED_THRESHOLD_TYPE] == \
                    Constants.LATCH_GT:
                if data > latching_entry[Constants.LATCH_DATA_TARGET]:
                    process = True
            elif latching_entry[Constants.LATCHED_THRESHOLD_TYPE] == \
                    Constants.LATCH_GTE:
                if data >= latching_entry[Constants.LATCH_DATA_TARGET]:
                    process = True
            elif latching_entry[Constants.LATCHED_THRESHOLD_TYPE] == \
                    Constants.LATCH_LT:
                if data < latching_entry[Constants.LATCH_DATA_TARGET]:
                    process = True
            elif latching_entry[Constants.LATCHED_THRESHOLD_TYPE] == \
                    Constants.LATCH_LTE:
                if data <= latching_entry[Constants.LATCH_DATA_TARGET]:
                    process = True
            if process:
                latching_entry[Constants.LATCHED_DATA] = data
                await self._process_latching(key, latching_entry)

    # noinspection PyMethodMayBeStatic
    def _discover_port(self):
        """
        This is a private utility method.
        This method attempts to discover the com port that the arduino
        is connected to.

        :returns: Detected Comport
        """
        # if MAC get list of ports
        if sys.platform.startswith('darwin'):
            locations = glob.glob('/dev/tty.[usb*]*')
            locations = glob.glob('/dev/tty.[wchusb*]*') + locations
            locations.append('end')
        # for everyone else, here is a list of possible ports
        else:
            locations = ['dev/ttyACM0', '/dev/ttyACM0', '/dev/ttyACM1',
                         '/dev/ttyACM2', '/dev/ttyACM3', '/dev/ttyACM4',
                         '/dev/ttyACM5', '/dev/ttyUSB0', '/dev/ttyUSB1',
                         '/dev/ttyUSB2', '/dev/ttyUSB3', '/dev/ttyUSB4',
                         '/dev/ttyUSB5', '/dev/ttyUSB6', '/dev/ttyUSB7',
                         '/dev/ttyUSB8', '/dev/ttyUSB9',
                         '/dev/ttyUSB10',
                         '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2',
                         '/dev/tty.usbserial', '/dev/tty.usbmodem', 'com2',
                         'com3', 'com4', 'com5', 'com6', 'com7', 'com8',
                         'com9', 'com10', 'com11', 'com12', 'com13',
                         'com14', 'com15', 'com16', 'com17', 'com18',
                         'com19', 'com20', 'com21', 'com1', 'end'
                         ]

        detected = None
        for device in locations:
            try:
                serialport = serial.Serial(device, 57600, timeout=0)
                detected = device
                serialport.close()
                break
            except serial.SerialException:
                if device == 'end':
                    if self.log_output:
                        logging.exception(
                            'Unable to find Serial Port, Please plug in '
                            'cable or check cable connections.')
                    else:
                        print('Unable to find Serial Port, Please plug in '
                              'cable or check cable connections.')
                    detected = None
                    exit()
        if self.log_output:
            log_string = 'Using COM Port: ' + detected
            logging.info(log_string)
        else:
            print('{}{}\n'.format('Using COM Port:', detected))
        return detected

    # noinspection PyMethodMayBeStatic
    def _format_capability_report(self, data):
        """
        This is a private utility method.
        This method formats a capability report if the user wishes to
        send it to the console.
        If log_output = True, no output is generated

        :param data: Capability report
        :returns: None
        """

        if self.log_output:
            return

        else:
            pin_modes = {0: 'Digital_Input', 1: 'Digital_Output',
                         2: 'Analog', 3: 'PWM', 4: 'Servo',
                         5: 'Shift', 6: 'I2C', 7: 'One Wire',
                         8: 'Stepper', 9: 'Encoder'}
            x = 0
            pin = 0

            print('\nCapability Report')
            print('-----------------\n')
            while x < len(data):
                # get index of next end marker
                print('{} {}{}'.format('Pin', str(pin), ':'))
                while data[x] != 127:
                    mode_str = ""
                    pin_mode = pin_modes.get(data[x])
                    mode_str += str(pin_mode)
                    x += 1
                    bits = data[x]
                    print('{:>5}{}{} {}'.format('  ', mode_str, ':', bits))
                    x += 1
                x += 1
                pin += 1

    async def _process_latching(self, key, latching_entry):
        """
        This is a private utility method.
        This method process latching events and either returns them via
        callback or stores them in the latch map

        :param key: Encoded pin
        :param latching_entry: a latch table entry
        :returns: Callback or store data in latch map
        """
        if latching_entry[Constants.LATCH_CALLBACK]:
            # auto clear entry and execute the callback
            if latching_entry[Constants.LATCH_CALLBACK_TYPE]:
                await latching_entry[Constants.LATCH_CALLBACK] \
                    ([key, latching_entry[Constants.LATCHED_DATA], time.time()])
            # noinspection PyPep8
            else:
                latching_entry[Constants.LATCH_CALLBACK] \
                    ([key, latching_entry[Constants.LATCHED_DATA], time.time()])
            self.latch_map[key] = [0, 0, 0, 0, 0, None]
        else:
            updated_latch_entry = latching_entry
            updated_latch_entry[Constants.LATCH_STATE] = \
                Constants.LATCH_LATCHED
            updated_latch_entry[Constants.LATCHED_DATA] = \
                latching_entry[Constants.LATCHED_DATA]
            # time stamp it
            updated_latch_entry[Constants.LATCHED_TIME_STAMP] = time.time()
            self.latch_map[key] = updated_latch_entry

    async def _send_command(self, command):
        """
        This is a private utility method.
        The method sends a non-sysex command to Firmata.

        :param command:  command data
        :returns: length of data sent
        """
        send_message = ""

        for i in command:
            send_message += chr(i)
        result = None
        
        logging.debug("Outgoing: ")
        for data in send_message:
            logging.debug(hex(ord(data)))
            try:
                result = await self.write(data)
            except():
                if self.log_output:
                    logging.exception('cannot send command')
                else:
                    print('cannot send command')
        return result

    async def _send_sysex(self, sysex_command, sysex_data=None):
        """
        This is a private utility method.
        This method sends a sysex command to Firmata.

        :param sysex_command: sysex command
        :param sysex_data: data for command
        :returns : No return value.
        """
        if not sysex_data:
            sysex_data = []

        # convert the message command and data to characters
        sysex_message = chr(PrivateConstants.START_SYSEX)
        sysex_message += chr(sysex_command)
        if len(sysex_data):
            for d in sysex_data:
                sysex_message += chr(d)
        sysex_message += chr(PrivateConstants.END_SYSEX)

        logging.debug("Outgoing: ")
        for data in sysex_message:
            logging.debug(hex(ord(data)))
            await self.write(data)

    async def _wait_for_data(self, current_command, number_of_bytes):
        """
        This is a private utility method.
        This method accumulates the requested number of bytes and
        then returns the full command

        :param current_command:  command id
        :param number_of_bytes:  how many bytes to wait for
        :returns: command
        """
        while number_of_bytes:
            next_command_byte = await self.read()
            current_command.append(next_command_byte)
            number_of_bytes -= 1
        return current_command
