# -*- coding: utf-8 -*-
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
import sys
import logging

import serial


# noinspection PyStatementEffect,PyUnresolvedReferences,PyUnresolvedReferences
class PymataSerial:
    """
    This class encapsulates management of the serial port that communicates
    with the Arduino Firmata
    It provides a 'futures' interface to make Pyserial compatible with asyncio
    """

    def __init__(self, com_port='/dev/ttyACM0', speed=57600, sleep_tune=.001,
                 log_output=False):
        """
        This is the constructor for the aio serial handler

        :param com_port: Com port designator
        :param speed: baud rate
        :return: None
        """
        self.log_output = log_output
        if self.log_output:
            logging.info('Initializing Arduino - Please wait...')
        else:
            print('Initializing Arduino - Please wait...', end=" ")
        sys.stdout.flush()
        self.my_serial = serial.Serial(com_port, speed, timeout=1,
                                       writeTimeout=1)

        self.com_port = com_port
        self.sleep_tune = sleep_tune

    def get_serial(self):
        """
        This method returns a reference to the serial port in case the
        user wants to call pyserial methods directly

        :return: pyserial instance
        """
        return self.my_serial

    async def write(self, data):
        """
        This is an asyncio adapted version of pyserial write. It provides a
        non-blocking  write and returns the number of bytes written upon
        completion

        :param data: Data to be written
        :return: Number of bytes written
        """
        # the secret sauce - it is in your future
        future = asyncio.Future()
        result = None
        try:
            result = self.my_serial.write(bytes([ord(data)]))
        except serial.SerialException:
            # self.my_serial.close()
            # noinspection PyBroadException
            try:
                await self.close()
                future.cancel()
                if self.log_output:
                    logging.exception('Write exception')
                else:
                    print('Write exception')

                loop = asyncio.get_event_loop()
                for t in asyncio.Task.all_tasks(loop):
                    t.cancel()
                loop.run_until_complete(asyncio.sleep(.1))
                loop.stop()
                loop.close()
                self.my_serial.close()
                sys.exit(0)
            except:  # swallow any additional exceptions during shutdown
                pass

        if result:
            future.set_result(result)
            while True:
                if not future.done():
                    # spin our asyncio wheels until future completes
                    await asyncio.sleep(self.sleep_tune)

                else:
                    return future.result()

    async def readline(self):
        """
        This is an asyncio adapted version of pyserial read.
        It provides a non-blocking read and returns a line of data read.

        :return: A line of data
        """
        future = asyncio.Future()
        data_available = False
        while True:
            if not data_available:
                if not self.my_serial.inWaiting():
                    await asyncio.sleep(self.sleep_tune)
                else:
                    data_available = True
                    data = self.my_serial.readline()
                    future.set_result(data)
            else:
                if not future.done():
                    await asyncio.sleep(self.sleep_tune)
                else:
                    return future.result()

    async def read(self):
        """
        This is an asyncio adapted version of pyserial read
        that provides non-blocking read.

        :return: One character
        """

        # create an asyncio Future
        future = asyncio.Future()

        # create a flag to indicate when data becomes available
        data_available = False

        # wait for a character to become available and read from
        # the serial port
        while True:
            if not data_available:
                # test to see if a character is waiting to be read.
                # if not, relinquish control back to the event loop through the
                # short sleep
                if not self.my_serial.inWaiting():
                    await asyncio.sleep(self.sleep_tune)
                # data is available.
                # set the flag to true so that the future can "wait" until the
                # read is completed.
                else:
                    data_available = True
                    data = self.my_serial.read()
                    # set future result to make the character available
                    future.set_result(ord(data))
            else:
                # wait for the future to complete
                if not future.done():
                    await asyncio.sleep(self.sleep_tune)
                else:
                    # future is done, so return the character
                    return future.result()

    async def close(self):
        """
        Close the serial port
        """
        # future = asyncio.Future()
        self.my_serial.close()

    async def open(self):
        """
        Open the serial port
        """
        # future = asyncio.Future()
        self.my_serial.open()

    async def set_dtr(self, state):
        """
        Set DTR state
        :param state: DTR state
        """
        self.my_serial.setDTR(state)
