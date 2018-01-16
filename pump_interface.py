#!/usr/bin/python3

# pump_interface.py
# A PyQt5-based interface for running the open-source
# microfluidic pumps.

import sys
#import logging
import time
#import picamera
from pymata_aio.pymata3 import PyMata3

from PyQt5.QtCore import Qt, pyqtSlot, QPoint, QTimer
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QGridLayout,
                             QSpinBox, QComboBox, QPushButton, QTabWidget,
                             QDoubleSpinBox)


class Pump_interface(QWidget):

    def __init__(self):
        super().__init__()

        self.initHardwareConstants()
        self.initBoard()
        self.initUIrefreshLoop()
        #self.camera = picamera.PiCamera()
        self.initUI()
        self.initGlobalVariables()

    def initHardwareConstants(self):
        self.steps_per_rev = 6400
        self.mm_per_rev = 0.8
        self.syringe_mm_per_ml_dict = {}
        self.syringe_mm_per_ml_dict["3mL"] = 17.0
        self.syringe_mm_per_ml_dict["10mL"] = 6.0
        self.syringe_mm_per_ml_dict["60mL"] = 1.5

    def initBoard(self):
        self.board = PyMata3( log_output=True, arduino_wait=5)
        # initializing X stepper with device number 0
        self.board.get_pin_state(2)
        self.board.accelstepper_config( 0, 1, 1, 0, [2,5])
        self.board.get_pin_state(2)
        # initializing Y stepper with device number 1
        self.board.accelstepper_config( 1, 1, 1, 0, [3,6])
        # initializing Z stepper with device number 2
        self.board.accelstepper_config( 2, 1, 1, 0, [4,7])

    def initUIrefreshLoop(self):
        self.ui_refresh_timer = QTimer()
        self.ui_refresh_timer.timeout.connect(self.ui_refresh)
        self.ui_refresh_timer.start(700)

    def initGlobalVariables(self):
        # Motor state variables
        # ["running", "paused", "stopped"]
        self.pump_one_state = "stopped"
        self.pump_two_state = "stopped"
        self.pump_three_state = "stopped"
        self.pump_one_total_steps = 0.00
        self.pump_two_total_steps = 0.00
        self.pump_three_total_steps = 0.00
        self.pump_one_final_speed = 0.00
        self.pump_two_final_speed = 0.00
        self.pump_three_final_speed = 0.00
        self.pump_one_total_distance = 0.00
        self.pump_two_total_distance = 0.00
        self.pump_three_total_distance = 0.00
        self.pump_one_total_distance_units = 0.00
        self.pump_two_total_distance_units = 0.00
        self.pump_three_total_distance_units = 0.00
        self.pump_one_total_time = 0.00
        self.pump_two_total_time = 0.00
        self.pump_three_total_time = 0.00
        self.pump_one_start_time = 0.00
        self.pump_two_start_time = 0.00
        self.pump_three_start_time = 0.00
        self.pump_one_time_running_fraction = 0.00
        self.pump_two_time_running_fraction = 0.00
        self.pump_three_time_running_fraction = 0.00
        self.pump_one_last_timestamp = 0.00
        self.pump_two_last_timestamp = 0.00
        self.pump_three_last_timestamp = 0.00

    def initUI(self):
        self.create_widgets()
        self.style_widgets()
        self.attach_widget_callbacks()
        self.place_widgets()

    def create_widgets(self):
        ## Pumps Tab -- titles
        self.title_speed_label = QLabel("Speed", self)
        self.title_speed_label.setAlignment(Qt.AlignHCenter)
        self.title_distance_label = QLabel("Distance", self)
        self.title_distance_label.setAlignment(Qt.AlignHCenter)
        self.title_direction_label = QLabel("Direction", self)
        self.title_direction_label.setAlignment(Qt.AlignHCenter)
        self.title_syringe_label = QLabel("Syringe", self)
        self.title_syringe_label.setAlignment(Qt.AlignHCenter)
        self.title_speed_readout_label = QLabel("Current Speed", self)
        self.title_speed_readout_label.setAlignment(Qt.AlignHCenter)
        self.title_distance_traveled_label = QLabel(
                "Distance Traveled", self)
        self.title_distance_traveled_label.setAlignment(Qt.AlignHCenter)
        self.title_distance_set_label = QLabel("Distance Set", self)
        self.title_distance_set_label.setAlignment(Qt.AlignHCenter)
        self.title_distance_remaining_label = QLabel(
                "Distance Remaining", self)
        self.title_distance_remaining_label.setAlignment(Qt.AlignHCenter)
        
        ## Pumps Tab -- Pump-specific
        self.pump_one_label = QLabel("Pump One", self)
        self.pump_two_label = QLabel("Pump Two", self)
        self.pump_three_label = QLabel("Pump Three", self)

        self.pump_one_speed = QDoubleSpinBox(self)
        self.pump_two_speed = QDoubleSpinBox(self)
        self.pump_three_speed = QDoubleSpinBox(self)
        
        self.pump_one_speed_units = QComboBox(self)
        self.pump_one_speed_units.addItem('mm/s')
        self.pump_one_speed_units.addItem('mL/hr')
        self.pump_two_speed_units = QComboBox(self)
        self.pump_two_speed_units.addItem('mm/s')
        self.pump_two_speed_units.addItem('mL/hr')
        self.pump_three_speed_units = QComboBox(self)
        self.pump_three_speed_units.addItem('mm/s')
        self.pump_three_speed_units.addItem('mL/hr')

        self.pump_one_distance = QDoubleSpinBox(self)
        self.pump_one_distance.setSpecialValueText(u'    \u221e')
        self.pump_two_distance = QDoubleSpinBox(self)
        self.pump_two_distance.setSpecialValueText(u'    \u221e')
        self.pump_three_distance = QDoubleSpinBox(self)
        self.pump_three_distance.setSpecialValueText(u'    \u221e')

        self.pump_one_distance_units = QComboBox(self)
        self.pump_one_distance_units.addItem('mm')
        self.pump_one_distance_units.addItem('mL')
        self.pump_two_distance_units = QComboBox(self)
        self.pump_two_distance_units.addItem('mm')
        self.pump_two_distance_units.addItem('mL')
        self.pump_three_distance_units = QComboBox(self)
        self.pump_three_distance_units.addItem('mm')
        self.pump_three_distance_units.addItem('mL')
        
        self.pump_one_direction = QComboBox(self)
        self.pump_one_direction.addItem('expel')
        self.pump_one_direction.addItem('intake')
        self.pump_two_direction = QComboBox(self)
        self.pump_two_direction.addItem('expel')
        self.pump_two_direction.addItem('intake')
        self.pump_three_direction = QComboBox(self)
        self.pump_three_direction.addItem('expel')
        self.pump_three_direction.addItem('intake')
        
        self.pump_one_syringe = QComboBox(self)
        self.pump_one_syringe.addItem('3mL')
        self.pump_one_syringe.addItem('10mL')
        self.pump_one_syringe.addItem('60mL')
        self.pump_two_syringe = QComboBox(self)
        self.pump_two_syringe.addItem('3mL')
        self.pump_two_syringe.addItem('10mL')
        self.pump_two_syringe.addItem('60mL')
        self.pump_three_syringe = QComboBox(self)
        self.pump_three_syringe.addItem('3mL')
        self.pump_three_syringe.addItem('10mL')
        self.pump_three_syringe.addItem('60mL')

        #self.pump_one_run = run_button('Run')
        self.pump_one_run = QPushButton('Run', self)
        self.pump_two_run = QPushButton('Run', self)
        self.pump_three_run = QPushButton('Run', self)

        self.pump_one_stop = QPushButton('Stop', self)
        self.pump_two_stop = QPushButton('Stop', self)
        self.pump_three_stop = QPushButton('Stop', self)

        self.pump_one_speed_readout = QLabel("0.00", self)
        self.pump_two_speed_readout = QLabel("0.00", self)
        self.pump_three_speed_readout = QLabel("0.00", self)        
        self.pump_one_speed_units_readout = QLabel("", self)
        self.pump_two_speed_units_readout = QLabel("", self)
        self.pump_three_speed_units_readout = QLabel("", self)
       
        self.pump_one_distance_traveled = QLabel("0.00", self)
        self.pump_two_distance_traveled = QLabel("0.00", self)
        self.pump_three_distance_traveled = QLabel("0.00", self)        
        self.pump_one_distance_traveled_units = QLabel("", self)
        self.pump_two_distance_traveled_units = QLabel("", self)
        self.pump_three_distance_traveled_units = QLabel("", self)
       
        self.pump_one_distance_set = QLabel("0.00", self)
        self.pump_two_distance_set = QLabel("0.00", self)
        self.pump_three_distance_set = QLabel("0.00", self)        
        self.pump_one_distance_set_units = QLabel("", self)
        self.pump_two_distance_set_units = QLabel("", self)
        self.pump_three_distance_set_units = QLabel("", self)
       
        self.pump_one_distance_remaining = QLabel("0.00", self)
        self.pump_two_distance_remaining = QLabel("0.00", self)
        self.pump_three_distance_remaining = QLabel("0.00", self)        
        self.pump_one_distance_remaining_units = QLabel("", self)
        self.pump_two_distance_remaining_units = QLabel("", self)
        self.pump_three_distance_remaining_units = QLabel("", self)

        self.run_all_pumps = QPushButton('Run All Pumps', self)
        self.stop_all_pumps = QPushButton('Stop All Pumps', self)
        
        ## Mixers Tab
        #self.start_mixer_one = QPushButton('Start Mixer 1', self)
        #self.start_mixer_two = QPushButton('Start Mixer 2', self)
        
        ## Camera Tab
        self.view_camera = QPushButton('View Camera', self)


    def style_widgets(self):
        self.run_button_style_string = """
            .QPushButton {
                background-color: #33cc33;
            }
        """
        self.pause_button_style_string = """
            .QPushButton {
                background-color: #0000ff;
            }
        """
        self.stop_button_style_string = """
            .QPushButton {
                background-color: #ff0000;
            }
        """
        self.pump_one_run.setStyleSheet(self.run_button_style_string)
        self.pump_two_run.setStyleSheet(self.run_button_style_string)
        self.pump_three_run.setStyleSheet(self.run_button_style_string)
        self.pump_one_stop.setStyleSheet(self.stop_button_style_string)
        self.pump_two_stop.setStyleSheet(self.stop_button_style_string)
        self.pump_three_stop.setStyleSheet(self.stop_button_style_string)
        self.run_all_pumps.setStyleSheet(self.run_button_style_string)
        self.stop_all_pumps.setStyleSheet(self.stop_button_style_string)

        # Set some necessary names
        self.pump_one_run.setObjectName('pump_one_run')
        self.pump_two_run.setObjectName('pump_two_run')
        self.pump_three_run.setObjectName('pump_three_run')
        self.pump_one_stop.setObjectName('pump_one_stop')
        self.pump_two_stop.setObjectName('pump_two_stop')
        self.pump_three_stop.setObjectName('pump_three_stop')


    def attach_widget_callbacks(self):
        self.pump_one_run.clicked.connect( self.run_button_click )
        self.pump_two_run.clicked.connect( self.run_button_click )
        self.pump_three_run.clicked.connect( self.run_button_click )
        self.run_all_pumps.clicked.connect( self.run_all_pumps_button_click )

        self.pump_one_stop.clicked.connect( self.stop_button_click )
        self.pump_two_stop.clicked.connect( self.stop_button_click )
        self.pump_three_stop.clicked.connect( self.stop_button_click )
        self.stop_all_pumps.clicked.connect( self.stop_all_pumps_button_click )

        self.view_camera.clicked.connect( self.camera_preview )

    def place_widgets(self):

        ## Tabs
        self.tabs = QTabWidget(self)
        self.tab1 = QWidget(self)
        #self.tab2 = QWidget(self)
        self.tab3 = QWidget(self)
        self.tabs.addTab(self.tab1, "Pumps")
        #self.tabs.addTab(self.tab2, "Mixers")
        self.tabs.addTab(self.tab3, "Camera")

        ## Tab 1 Layout
        self.tab1_grid = QGridLayout()
        self.tab1_grid.setSpacing(10)

        self.tab1_grid.addWidget(self.title_speed_label, 1, 1, 1, 2)
        self.tab1_grid.addWidget(self.title_distance_label, 1, 3, 1, 2)
        self.tab1_grid.addWidget(self.title_direction_label, 1, 5)
        self.tab1_grid.addWidget(self.title_syringe_label, 1, 6)
        self.tab1_grid.addWidget(self.title_speed_readout_label, 1, 9, 1, 2)
        self.tab1_grid.addWidget(self.title_distance_traveled_label, 
                1, 11, 1, 2)
        self.tab1_grid.addWidget(self.title_distance_set_label, 1, 13, 1, 2)
        self.tab1_grid.addWidget(self.title_distance_remaining_label, 
                1, 15, 1, 2)

        self.tab1_grid.addWidget(self.pump_one_label, 2, 0)
        self.tab1_grid.addWidget(self.pump_two_label, 3, 0)
        self.tab1_grid.addWidget(self.pump_three_label, 4, 0)
        self.tab1_grid.addWidget(self.pump_one_speed, 2, 1)
        self.tab1_grid.addWidget(self.pump_two_speed, 3, 1)
        self.tab1_grid.addWidget(self.pump_three_speed, 4, 1)
        self.tab1_grid.addWidget(self.pump_one_speed_units, 2, 2)
        self.tab1_grid.addWidget(self.pump_two_speed_units, 3, 2)
        self.tab1_grid.addWidget(self.pump_three_speed_units, 4, 2)
        self.tab1_grid.addWidget(self.pump_one_distance, 2, 3)
        self.tab1_grid.addWidget(self.pump_two_distance, 3, 3)
        self.tab1_grid.addWidget(self.pump_three_distance, 4, 3)
        self.tab1_grid.addWidget(self.pump_one_distance_units, 2, 4)
        self.tab1_grid.addWidget(self.pump_two_distance_units, 3, 4)
        self.tab1_grid.addWidget(self.pump_three_distance_units, 4, 4)
        self.tab1_grid.addWidget(self.pump_one_direction, 2, 5)
        self.tab1_grid.addWidget(self.pump_two_direction, 3, 5)
        self.tab1_grid.addWidget(self.pump_three_direction, 4, 5)
        self.tab1_grid.addWidget(self.pump_one_syringe, 2, 6)
        self.tab1_grid.addWidget(self.pump_two_syringe, 3, 6)
        self.tab1_grid.addWidget(self.pump_three_syringe, 4, 6)
        self.tab1_grid.addWidget(self.pump_one_run, 2, 7)
        self.tab1_grid.addWidget(self.pump_two_run, 3, 7)
        self.tab1_grid.addWidget(self.pump_three_run, 4, 7)
        self.tab1_grid.addWidget(self.pump_one_stop, 2, 8)
        self.tab1_grid.addWidget(self.pump_two_stop, 3, 8)
        self.tab1_grid.addWidget(self.pump_three_stop, 4, 8)
        self.tab1_grid.addWidget(self.pump_one_speed_readout, 2, 9)
        self.tab1_grid.addWidget(self.pump_two_speed_readout, 3, 9)
        self.tab1_grid.addWidget(self.pump_three_speed_readout, 4, 9)
        self.tab1_grid.addWidget(self.pump_one_speed_units_readout, 2, 10)
        self.tab1_grid.addWidget(self.pump_two_speed_units_readout, 3, 10)
        self.tab1_grid.addWidget(self.pump_three_speed_units_readout, 4, 10)
        self.tab1_grid.addWidget(self.pump_one_distance_traveled, 2, 11)
        self.tab1_grid.addWidget(self.pump_two_distance_traveled, 3, 11)
        self.tab1_grid.addWidget(self.pump_three_distance_traveled, 4, 11)
        self.tab1_grid.addWidget(self.pump_one_distance_traveled_units, 2, 12)
        self.tab1_grid.addWidget(self.pump_two_distance_traveled_units, 3, 12)
        self.tab1_grid.addWidget(self.pump_three_distance_traveled_units, 
                4, 12)
        self.tab1_grid.addWidget(self.pump_one_distance_set, 2, 13)
        self.tab1_grid.addWidget(self.pump_two_distance_set, 3, 13)
        self.tab1_grid.addWidget(self.pump_three_distance_set, 4, 13)
        self.tab1_grid.addWidget(self.pump_one_distance_set_units, 2, 14)
        self.tab1_grid.addWidget(self.pump_two_distance_set_units, 3, 14)
        self.tab1_grid.addWidget(self.pump_three_distance_set_units, 4, 14)
        self.tab1_grid.addWidget(self.pump_one_distance_remaining, 2, 15)
        self.tab1_grid.addWidget(self.pump_two_distance_remaining, 3, 15)
        self.tab1_grid.addWidget(self.pump_three_distance_remaining, 4, 15)
        self.tab1_grid.addWidget(self.pump_one_distance_remaining_units, 
                2, 16)
        self.tab1_grid.addWidget(self.pump_two_distance_remaining_units, 
                3, 16)
        self.tab1_grid.addWidget(self.pump_three_distance_remaining_units, 
                4, 16)

        self.tab1_grid.addWidget(self.run_all_pumps, 5, 6, 1, 2)
        self.tab1_grid.addWidget(self.stop_all_pumps, 5, 8, 1, 2)
        
        ## Tab 2 Layout
        #self.tab2_grid = QGridLayout()
        #self.tab2_grid.setSpacing(10)
        #self.tab2_grid.addWidget(self.start_mixer_one, 1, 0, 1, 2)
        #self.tab2_grid.addWidget(self.start_mixer_two, 1, 2, 1, 2)
        
        ## Tab 3 Layout
        self.tab3_grid = QGridLayout()
        self.tab3_grid.setSpacing(10)
        self.tab3_grid.addWidget(self.view_camera, 1, 0, 1, 2)
        
        
        #self.setLayout(grid)
        self.tab1.setLayout(self.tab1_grid)
        #self.tab2.setLayout(self.tab2_grid)
        self.tab3.setLayout(self.tab3_grid)
        self.tab_layout = QGridLayout(self)
        self.tab_layout.addWidget(self.tabs)

        self.setGeometry(300,300,300,300)
        self.setWindowTitle("Poseidon Pumps")
        self.show()

    # Click functions
    
    def run_button_click(self):
        clicked_button = self.sender()
        button_name = clicked_button.objectName()
        if button_name=="pump_one_run":
            if self.pump_one_state=="stopped":
                pump_one_running = self.run_pump(button_name)
                if pump_one_running==0:
                    self.pump_one_state = "running"
            elif self.pump_one_state=="running":
                self.pause_pump(button_name)
                self.pump_one_state = "paused"
            elif self.pump_one_state=="paused":
                self.unpause_pump(button_name)
                self.pump_one_state = "running"
        elif button_name=="pump_two_run":
            if self.pump_two_state=="stopped":
                pump_two_running = self.run_pump(button_name)
                if pump_two_running==0:
                    self.pump_two_state = "running"
            elif self.pump_two_state=="running":
                self.pause_pump(button_name)
                self.pump_two_state = "paused"
            elif self.pump_two_state=="paused":
                self.unpause_pump(button_name)
                self.pump_two_state = "running"
        elif button_name=="pump_three_run":
            if self.pump_three_state=="stopped":
                pump_three_running = self.run_pump(button_name)
                if pump_three_running==0:
                    self.pump_three_state = "running"
            elif self.pump_three_state=="running":
                self.pause_pump(button_name)
                self.pump_three_state = "paused"
            elif self.pump_three_state=="paused":
                self.unpause_pump(button_name)
                self.pump_three_state = "running"
        self.run_all_pumps_consistency_check()
   
    def stop_button_click(self):
        button_name = self.sender().objectName()
        self.stop_pump(button_name)
        if button_name=="pump_one_stop":
            self.pump_one_state = "stopped"
        if button_name=="pump_two_stop":
            self.pump_two_state = "stopped"
        if button_name=="pump_three_stop":
            self.pump_three_state = "stopped"
        self.run_all_pumps_consistency_check()

    def run_all_pumps_button_click(self):
        clicked_button = self.sender()
        button_name = clicked_button.objectName()
        if self.pump_one_state=="running" or \
            self.pump_two_state=="running" or \
            self.pump_three_state=="running":
            if self.pump_one_state=="running":
                self.pause_pump("pump_one_run")
                self.pump_one_state = "paused"
            if self.pump_two_state=="running":
                self.pause_pump("pump_two_run")
                self.pump_two_state = "paused"
            if self.pump_three_state=="running":
                self.pause_pump("pump_three_run")
                self.pump_three_state = "paused"
            clicked_button.setStyleSheet(self.run_button_style_string)
            clicked_button.setText('Resume Paused Pumps')
        elif self.pump_one_state=="paused" or \
            self.pump_two_state=="paused" or \
            self.pump_three_state=="paused":
            if self.pump_one_state=="paused":
                self.unpause_pump("pump_one_run")
                self.pump_one_state = "running"
            if self.pump_two_state=="paused":
                self.unpause_pump("pump_two_run")
                self.pump_two_state = "running"
            if self.pump_three_state=="paused":
                self.unpause_pump("pump_three_run")
                self.pump_three_state = "running"
            clicked_button.setStyleSheet(self.pause_button_style_string)
            clicked_button.setText('Pause Running Pumps')
        else:
            pump_one_running = self.run_pump("pump_one_run")
            if pump_one_running==0:
                self.pump_one_state = "running"
            pump_two_running = self.run_pump("pump_two_run")
            if pump_two_running==0:
                self.pump_two_state = "running"
            pump_three_running = self.run_pump("pump_three_run")
            if pump_three_running==0:
                self.pump_three_state = "running"
        self.run_all_pumps_consistency_check()

    def stop_all_pumps_button_click(self):
        self.stop_pump("pump_one_stop")
        self.pump_one_state = "stopped"
        self.stop_pump("pump_two_stop")
        self.pump_two_state = "stopped"
        self.stop_pump("pump_three_stop")
        self.pump_three_state = "stopped"
        self.run_all_pumps_consistency_check()

    # Helper functions for click functions

    def pause_pump(self, button_name):
        if button_name == 'pump_one_run':
            self.board.accelstepper_stop(0)
            self.pump_one_run.setStyleSheet(self.run_button_style_string)
            self.pump_one_run.setText('Resume')
        if button_name == 'pump_two_run':
            self.board.accelstepper_stop(1)
            self.pump_two_run.setStyleSheet(self.run_button_style_string)
            self.pump_two_run.setText('Resume')
        if button_name == 'pump_three_run':
            self.board.accelstepper_stop(2)
            self.pump_three_run.setStyleSheet(self.run_button_style_string)
            self.pump_three_run.setText('Resume')

    def unpause_pump(self, button_name):
        current_time = time.time()
        if button_name == 'pump_one_run':
            pause_length = current_time - self.pump_one_last_timestamp
            self.pump_one_start_time = self.pump_one_start_time + pause_length
            remaining_steps = (1 - self.pump_one_time_running_fraction) * self.pump_one_total_steps
            self.board.accelstepper_set_speed(0, self.pump_one_final_speed)
            self.board.accelstepper_step(0, remaining_steps, "forward")
            self.pump_one_run.setStyleSheet(self.pause_button_style_string)
            self.pump_one_run.setText('Pause')
        if button_name == 'pump_two_run':
            pause_length = current_time - self.pump_two_last_timestamp
            self.pump_two_start_time = self.pump_two_start_time + pause_length
            remaining_steps = (1 - self.pump_two_time_running_fraction) * self.pump_two_total_steps
            self.board.accelstepper_set_speed(1, self.pump_two_final_speed)
            self.board.accelstepper_step(1, remaining_steps, "forward")
            self.pump_two_run.setStyleSheet(self.pause_button_style_string)
            self.pump_two_run.setText('Pause')
        if button_name == 'pump_three_run':
            pause_length = current_time - self.pump_three_last_timestamp
            self.pump_three_start_time = self.pump_three_start_time + pause_length
            remaining_steps = (1 - self.pump_three_time_running_fraction) * self.pump_three_total_steps
            self.board.accelstepper_set_speed(2, self.pump_three_final_speed)
            self.board.accelstepper_step(2, remaining_steps, "forward")
            self.pump_three_run.setStyleSheet(self.pause_button_style_string)
            self.pump_three_run.setText('Pause')

    def run_pump(self, button_name):
        motor_speed = self.compute_speed(button_name)
        if motor_speed > 0:
            direction = self.get_direction(button_name)
            steps = self.get_steps(button_name)
            self.assignGlobals(button_name, steps)
            #print("motor: " + str(button_name) + "   speed: " + str(motor_speed))
            if button_name == 'pump_one_run':
                self.board.accelstepper_zero(0)
                self.board.accelstepper_set_speed(0, motor_speed)
                self.board.accelstepper_step(0, steps, direction)
                self.pump_one_run.setStyleSheet(self.pause_button_style_string)
                self.pump_one_run.setText('Pause')
            elif button_name == 'pump_two_run':
                self.board.accelstepper_zero(1)
                self.board.accelstepper_set_speed(1, motor_speed)
                self.board.accelstepper_step(1, steps, direction)
                self.pump_two_run.setStyleSheet(self.pause_button_style_string)
                self.pump_two_run.setText('Pause')
            elif button_name == 'pump_three_run':
                self.board.accelstepper_zero(2)
                self.board.accelstepper_set_speed(2, motor_speed)
                self.board.accelstepper_step(2, steps, direction)
                self.pump_three_run.setStyleSheet(self.pause_button_style_string)
                self.pump_three_run.setText('Pause')
            self.display_speed(button_name)
            return 0
        return 1

    def assignGlobals(self, button_name, steps):
        speed_value = self.get_speed_value(button_name)
        speed_units = self.get_speed_units(button_name)
        if button_name=="pump_one_run":
            self.pump_one_total_steps = steps
            self.pump_one_total_distance = self.pump_one_distance.value()
            self.pump_one_total_distance_units = self.pump_one_distance_units.currentText()
            if self.pump_one_total_distance_units=="mm":
                self.pump_one_total_time = self.pump_one_total_distance / speed_value
            elif self.pump_one_total_distance_units=="mL":
                self.pump_one_total_time = (self.pump_one_total_distance / speed_value) * 3600
            self.pump_one_start_time = time.time()
            if self.pump_one_total_distance>0:
                self.pump_one_distance_remaining.setText("{0:.2f}".format(self.pump_one_total_distance))
                self.pump_one_distance_remaining_units.setText(str(self.pump_one_total_distance_units))
                self.pump_one_distance_traveled.setText("0.00")
                self.pump_one_distance_traveled_units.setText(str(self.pump_one_total_distance_units))
            else:
                self.pump_one_distance_remaining.setText("")
                self.pump_one_distance_traveled.setText("")
        elif button_name=="pump_two_run":
            self.pump_two_total_steps = steps
            self.pump_two_total_distance = self.pump_two_distance.value()
            self.pump_two_total_distance_units = self.pump_two_distance_units.currentText()
            if self.pump_two_total_distance_units=="mm":
                self.pump_two_total_time = self.pump_two_total_distance / speed_value
            elif self.pump_two_total_distance_units=="mL":
                self.pump_two_total_time = (self.pump_two_total_distance / speed_value) * 3600
            self.pump_two_start_time = time.time()
            if self.pump_two_total_distance>0:
                self.pump_two_distance_remaining.setText("{0:.2f}".format(self.pump_two_total_distance))
                self.pump_two_distance_remaining_units.setText(str(self.pump_two_total_distance_units))
                self.pump_two_distance_traveled.setText("0.00")
                self.pump_two_distance_traveled_units.setText(str(self.pump_two_total_distance_units))
            else:
                self.pump_two_distance_remaining.setText("")
                self.pump_two_distance_traveled.setText("")
        elif button_name=="pump_three_run":
            self.pump_three_total_steps = steps
            self.pump_three_total_distance = self.pump_three_distance.value()
            self.pump_three_total_distance_units = self.pump_three_distance_units.currentText()
            if self.pump_three_total_distance_units=="mm":
                self.pump_three_total_time = self.pump_three_total_distance / speed_value
            elif self.pump_three_total_distance_units=="mL":
                self.pump_three_total_time = (self.pump_three_total_distance / speed_value) * 3600
            self.pump_three_start_time = time.time()
            if self.pump_three_total_distance>0:
                self.pump_three_distance_remaining.setText("{0:.2f}".format(self.pump_three_total_distance))
                self.pump_three_distance_remaining_units.setText(str(self.pump_three_total_distance_units))
                self.pump_three_distance_traveled.setText("0.00")
                self.pump_three_distance_traveled_units.setText(str(self.pump_three_total_distance_units))
            else:
                self.pump_three_distance_remaining.setText("")
                self.pump_three_distance_traveled.setText("")
            
    def get_steps(self, button_name):
        if button_name=="pump_one_run":
            distance = self.pump_one_distance.value()
            distance_units = self.pump_one_distance_units.currentText()
            if distance==0:
                self.pump_one_distance_set.setText(u'\u221e')
                #self.pump_one_distance_set_units.setText(str(distance_units))
            else:
                self.pump_one_distance_set.setText("{0:.2f}".format(distance))
                self.pump_one_distance_set_units.setText(str(distance_units))
        elif button_name=="pump_two_run":
            distance = self.pump_two_distance.value()
            distance_units = self.pump_two_distance_units.currentText()
            if distance==0:
                self.pump_two_distance_set.setText(u'\u221e')
                #self.pump_two_distance_set_units.setText(str(distance_units))
            else:
                self.pump_two_distance_set.setText("{0:.2f}".format(distance))
                self.pump_two_distance_set_units.setText(str(distance_units))
        elif button_name=="pump_three_run":
            distance = self.pump_three_distance.value()
            distance_units = self.pump_three_distance_units.currentText()
            if distance==0:
                self.pump_three_distance_set.setText(u'\u221e')
                #self.pump_three_distance_set_units.setText(str(distance_units))
            else:
                self.pump_three_distance_set.setText("{0:.2f}".format(distance))
                self.pump_three_distance_set_units.setText(str(distance_units))
        if distance==0: # to the user, this appears to be infinity
            steps = 2147483647 # The largest number the firmware can hold
        else:
            if distance_units=="mm":
                steps = distance * (1 / self.mm_per_rev) * self.steps_per_rev 
            elif distance_units=="mL":
                syringe_name = self.get_syringe_name(button_name)
                mm_per_ml = self.syringe_mm_per_ml_dict[syringe_name]  #float
                steps = distance * mm_per_ml * (1 / self.mm_per_rev) * \
                        self.steps_per_rev
        return steps

    def get_direction(self, button_name):
        if button_name=="pump_one_run":
            raw_direction = self.pump_one_direction.currentText()
        if button_name=="pump_two_run":
            raw_direction = self.pump_two_direction.currentText()
        if button_name=="pump_three_run":
            raw_direction = self.pump_three_direction.currentText()
        final_direction = self.recompute_direction(raw_direction)
        return final_direction

    def recompute_direction(self, raw_direction):
        if raw_direction=="expel":
            final_direction = "forward"
        elif raw_direction=="intake":
            final_direction = "backward"
        return final_direction

    def display_speed(self, button_name):
        speed_value = self.get_speed_value(button_name)
        speed_units = self.get_speed_units(button_name)
        if button_name == 'pump_one_run':
            self.pump_one_speed_readout.setText("{0:.2f}".format(speed_value))
            self.pump_one_speed_units_readout.setText(str(speed_units))
        elif button_name == 'pump_two_run':
            self.pump_two_speed_readout.setText("{0:.2f}".format(speed_value))
            self.pump_two_speed_units_readout.setText(str(speed_units))
        elif button_name == 'pump_three_run':
            self.pump_three_speed_readout.setText("{0:.2f}".format(speed_value))
            self.pump_three_speed_units_readout.setText(str(speed_units))

    def compute_speed(self, button_name):
        """
        The output value from this function should be in units of steps/s.
        I'm going to assume that the motor being driven has 200 steps/rev 
        and is running with 1/32 microstepping (so, effectively, 6400 
        steps/rev).
        """
        speed_value = self.get_speed_value(button_name)
        speed_units = self.get_speed_units(button_name)
        # need to convert from native units to steps/s
        if speed_units=="mm/s":
            final_speed = (speed_value / self.mm_per_rev) * self.steps_per_rev
        elif speed_units=="mL/hr":
            syringe_name = self.get_syringe_name(button_name)
            mm_per_ml = self.syringe_mm_per_ml_dict[syringe_name]  #float
            final_speed = speed_value * mm_per_ml * (1 / self.mm_per_rev) * \
                    self.steps_per_rev * (1/3600)
        if button_name=="pump_one_run":
            self.pump_one_final_speed = final_speed
        elif button_name=="pump_two_run":
            self.pump_two_final_speed = final_speed
        elif button_name=="pump_three_run":
            self.pump_three_final_speed = final_speed
        return final_speed

    def get_speed_value(self, button_name):
        if button_name=="pump_one_run":
            speed_value = self.pump_one_speed.value()
        elif button_name=="pump_two_run":
            speed_value = self.pump_two_speed.value()
        elif button_name=="pump_three_run":
            speed_value = self.pump_three_speed.value()
        return speed_value

    def get_speed_units(self, button_name):
        if button_name=="pump_one_run":
            speed_units = self.pump_one_speed_units.currentText()
        elif button_name=="pump_two_run":
            speed_units = self.pump_two_speed_units.currentText()
        elif button_name=="pump_three_run":
            speed_units = self.pump_three_speed_units.currentText()
        return speed_units

    def get_syringe_name(self, button_name):
        if button_name=="pump_one_run":
            syringe_name = self.pump_one_syringe.currentText()
        elif button_name=="pump_two_run":
            syringe_name = self.pump_two_syringe.currentText()
        elif button_name=="pump_three_run":
            syringe_name = self.pump_three_syringe.currentText()
        return syringe_name

    def run_all_pumps_consistency_check(self):
        if self.pump_one_state=="running" or \
            self.pump_two_state=="running" or \
            self.pump_three_state=="running":
            self.run_all_pumps.setStyleSheet(self.pause_button_style_string)
            self.run_all_pumps.setText('Pause Running Pumps')
        elif self.pump_one_state=="paused" or \
            self.pump_two_state=="paused" or \
            self.pump_three_state=="paused":
            self.run_all_pumps.setStyleSheet(self.run_button_style_string)
            self.run_all_pumps.setText('Resume Paused Pumps')
        else:
            self.run_all_pumps.setStyleSheet(self.run_button_style_string)
            self.run_all_pumps.setText('Run All Pumps')

    def stop_pump(self, button_name):
        if button_name == 'pump_one_stop':
            self.pump_one_distance_set.setText("0.00")
            self.pump_one_distance_remaining.setText("0.00")
            self.pump_one_distance_traveled.setText("{0:.2f}".format(self.pump_one_total_distance))
            self.board.accelstepper_stop(0)
            self.pump_one_speed_readout.setText("0.00")
            self.pump_one_speed_units_readout.setText("")
            self.pump_one_run.setStyleSheet(self.run_button_style_string)
            self.pump_one_run.setText('Run')
        elif button_name == 'pump_two_stop':
            self.pump_two_distance_set.setText("0.00")
            self.pump_two_distance_remaining.setText("0.00")
            self.pump_two_distance_traveled.setText("{0:.2f}".format(self.pump_two_total_distance))
            self.board.accelstepper_stop(1)
            self.pump_two_speed_readout.setText("0.00")
            self.pump_two_speed_units_readout.setText("")
            self.pump_two_run.setStyleSheet(self.run_button_style_string)
            self.pump_two_run.setText('Run')
        elif button_name == 'pump_three_stop':
            self.pump_three_distance_set.setText("0.00")
            self.pump_three_distance_remaining.setText("0.00")
            self.pump_three_distance_traveled.setText("{0:.2f}".format(self.pump_three_total_distance))
            self.board.accelstepper_stop(2)
            self.pump_three_speed_readout.setText("0.00")
            self.pump_three_speed_units_readout.setText("")
            self.pump_three_run.setStyleSheet(self.run_button_style_string)
            self.pump_three_run.setText('Run')

    # Helper functions for UI

    def ui_refresh(self):
        current_time = time.time()
        if self.pump_one_state=="running" and self.pump_one_total_distance>0:
            self.pump_one_last_timestamp = current_time
            self.pump_one_time_running_fraction = (current_time - self.pump_one_start_time) / self.pump_one_total_time
            if self.pump_one_time_running_fraction < 1:
                self.pump_one_distance_remaining.setText("{0:.2f}".format( (1 - self.pump_one_time_running_fraction) * self.pump_one_total_distance))
                self.pump_one_distance_traveled.setText("{0:.2f}".format(self.pump_one_time_running_fraction * self.pump_one_total_distance))
            else:
                self.pump_one_speed_readout.setText("")
                self.pump_one_speed_units_readout.setText("")
                self.pump_one_distance_remaining.setText("0.00")
                self.pump_one_distance_traveled.setText("{0:.2f}".format(self.pump_one_total_distance))
                self.stop_pump("pump_one_run")
                self.pump_one_state = "stopped"
                self.pump_one_run.setStyleSheet(self.run_button_style_string)
                self.pump_one_run.setText('Run')
                self.run_all_pumps_consistency_check()
        if self.pump_two_state=="running" and self.pump_two_total_distance>0:
            print("pump_two_total_distance: " + str(self.pump_two_total_distance))
            self.pump_two_last_timestamp = current_time
            self.pump_two_time_running_fraction = (current_time - self.pump_two_start_time) / self.pump_two_total_time
            if self.pump_two_time_running_fraction < 1:
                self.pump_two_distance_remaining.setText("{0:.2f}".format( (1 - self.pump_two_time_running_fraction) * self.pump_two_total_distance))
                self.pump_two_distance_traveled.setText("{0:.2f}".format(self.pump_two_time_running_fraction * self.pump_two_total_distance))
            else:
                self.pump_two_speed_readout.setText("")
                self.pump_two_speed_units_readout.setText("")
                self.pump_two_distance_remaining.setText("0.00")
                self.pump_two_distance_traveled.setText("{0:.2f}".format(self.pump_two_total_distance))
                self.stop_pump("pump_two_run")
                self.pump_two_state = "stopped"
                self.pump_two_run.setStyleSheet(self.run_button_style_string)
                self.pump_two_run.setText('Run')
                self.run_all_pumps_consistency_check()
        if self.pump_three_state=="running" and self.pump_three_total_distance>0:
            self.pump_three_last_timestamp = current_time
            self.pump_three_time_running_fraction = (current_time - self.pump_three_start_time) / self.pump_three_total_time
            if self.pump_three_time_running_fraction < 1:
                self.pump_three_distance_remaining.setText("{0:.2f}".format( (1 - self.pump_three_time_running_fraction) * self.pump_three_total_distance))
                self.pump_three_distance_traveled.setText("{0:.2f}".format(self.pump_three_time_running_fraction * self.pump_three_total_distance))
            else:
                self.pump_three_speed_readout.setText("")
                self.pump_three_speed_units_readout.setText("")
                self.pump_three_distance_remaining.setText("0.00")
                self.pump_three_distance_traveled.setText("{0:.2f}".format(self.pump_three_total_distance))
                self.stop_pump("pump_three_run")
                self.pump_three_state = "stopped"
                self.pump_three_run.setStyleSheet(self.run_button_style_string)
                self.pump_three_run.setText('Run')
                self.run_all_pumps_consistency_check()

    def camera_preview(self):
        # get size and location of widget, and place the picamera overlay 
        # directly on top of it
        renderer_height = self.view_camera.height()
        renderer_width = self.view_camera.width()
        local_x = self.view_camera.x()
        local_y = self.view_camera.y()
        local_point = QPoint(local_x, local_y)
        renderer_x = self.view_camera.mapToGlobal(local_point).x()
        renderer_y = self.view_camera.mapToGlobal(local_point).y()
        #renderer_tuple = (renderer_x, renderer_y, renderer_width, renderer_height)
        renderer_tuple = ( int(renderer_x), int(renderer_y * 0.70), renderer_width, renderer_height*10)
        self.camera.resolution = ( 1024, 768) 
        #self.camera.resolution = ( renderer_width, renderer_height) 
        print( str(renderer_x) + "," + str(renderer_y) + "," + str(renderer_width) + "," + str(renderer_height) )
        #self.camera.start_preview( fullscreen=False,
        #    window=(300, 600, renderer_x, renderer_y))
        self.preview_window = self.camera.start_preview( fullscreen=False )
        self.preview_window._set_window( renderer_tuple )
        time.sleep(2)
        self.camera.stop_preview()


if __name__=='__main__':
    app = QApplication(sys.argv)
    pump_control = Pump_interface()
    sys.exit(app.exec_())
