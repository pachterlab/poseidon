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


class Constants:
    """
    This class contains a set of constants that may be used by
    the applications writer.
    """
    # pin modes
    INPUT = 0x00  # pin set as input
    OUTPUT = 0x01  # pin set as output
    ANALOG = 0x02  # analog pin in analogInput mode
    PWM = 0x03  # digital pin in PWM output mode
    SERVO = 0x04  # digital pin in Servo output mode
    I2C = 0x06  # pin included in I2C setup
    ONEWIRE = 0x07  # possible future feature
    STEPPER = 0x08  # any pin in stepper mode
    TONE = 0x09  # Any pin in TONE mode
    ENCODER = 0x0a
    SONAR = 0x0b  # Any pin in SONAR mode
    PIXY = 0x0c  # Any pin used by Pixy camera
    IGNORE = 0x7f

    # Tone commands
    TONE_TONE = 0  # play a tone
    TONE_NO_TONE = 1  # turn off tone

    # I2C command operation modes
    I2C_WRITE = 0B00000000
    I2C_READ = 0B00001000
    I2C_READ_CONTINUOUSLY = 0B00010000
    I2C_STOP_READING = 0B00011000
    I2C_READ_WRITE_MODE_MASK = 0B00011000
    I2C_10BIT_ADDRESS_MODE_MASK = 0B00100000
    I2C_END_TX_MASK = 0B01000000
    I2C_STOP_TX = 1
    I2C_RESTART_TX = 0

    # callback types
    CB_TYPE_DIRECT = None
    CB_TYPE_ASYNCIO = 1

    # latch states
    LATCH_IGNORE = 0  # this item currently not participating in latching

    # When the next pin value change is received for this pin,
    # if it matches the latch criteria the data will be latched
    LATCH_ARMED = 1

    # data has been latched. Read the data to re-arm the latch
    LATCH_LATCHED = 2

    # latch threshold types
    LATCH_EQ = 0  # data value is equal to the latch threshold value
    LATCH_GT = 1  # data value is greater than the latch threshold value
    LATCH_LT = 2  # data value is less than the latch threshold value
    LATCH_GTE = 3  # data value is >= to the latch threshold value
    LATCH_LTE = 4  # data value is <= to the latch threshold value

    # indices into latch table entry for manual read of latch data
    LATCH_STATE = 0
    LATCHED_THRESHOLD_TYPE = 1

    LATCH_DATA_TARGET = 2
    LATCHED_DATA = 3
    LATCHED_TIME_STAMP = 4
    LATCH_CALLBACK = 5
    LATCH_CALLBACK_TYPE = 6

    # indices for data returned for a latch callback
    LATCH_CALL_BACK_PIN = 0
    LATCH_CALL_BACK_DATA = 1
    LATCH_CALLBACK_TIME_STAMP = 2

