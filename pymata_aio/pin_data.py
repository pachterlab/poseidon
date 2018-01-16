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


class PinData:
    """
    Each analog and digital input pin is described by an instance of
    this class. It contains both the last data value received and a potential
    callback reference and the callback method type.
    The callback method type default is a non-asyncio call,
    but can be optionally be set to use yield from when required.
    """

    def __init__(self):
        # current data value
        self._current_value = 0
        # callback reference
        self._cb = None
        # call back to be executed with "await" or direct call
        # direct call is the default
        self._cb_type = None

    @property
    def current_value(self):
        return self._current_value

    @current_value.setter
    def current_value(self, value):
        self._current_value = value

    @property
    def cb(self):
        return self._cb

    @cb.setter
    def cb(self, value):
        self._cb = value

    @property
    def cb_type(self):
        return self._cb_type

    @cb_type.setter
    def cb_type(self, value):
        self._cb_type = value

