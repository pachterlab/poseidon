#!/usr/bin/python3

# pump_interface.py
# A PyQt5-based interface for running the open-source
# microfluidic pumps.

import pdb
import sys
from pymata_aio_test import Pymata3_board

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QGridLayout,
                             QSpinBox, QComboBox, QPushButton, QTabWidget)


class Pump_interface(QWidget):

    def __init__(self):
        super().__init__()

        self.board = Pymata3_board()
        self.initUI()

    
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

        self.pump_one_speed = QSpinBox(self)
        self.pump_two_speed = QSpinBox(self)
        self.pump_three_speed = QSpinBox(self)
        
        self.pump_one_speed_units = QComboBox(self)
        self.pump_one_speed_units.addItem('mm/s')
        self.pump_one_speed_units.addItem('mL/hr')
        self.pump_two_speed_units = QComboBox(self)
        self.pump_two_speed_units.addItem('mm/s')
        self.pump_two_speed_units.addItem('mL/hr')
        self.pump_three_speed_units = QComboBox(self)
        self.pump_three_speed_units.addItem('mm/s')
        self.pump_three_speed_units.addItem('mL/hr')

        self.pump_one_distance = QSpinBox(self)
        self.pump_two_distance = QSpinBox(self)
        self.pump_three_distance = QSpinBox(self)

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
        self.start_mixer_one = QPushButton('Start Mixer 1', self)
        self.start_mixer_two = QPushButton('Start Mixer 2', self)
        
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

    def place_widgets(self):

        ## Tabs
        self.tabs = QTabWidget(self)
        self.tab1 = QWidget(self)
        self.tab2 = QWidget(self)
        self.tab3 = QWidget(self)
        self.tabs.addTab(self.tab1, "Pumps")
        self.tabs.addTab(self.tab2, "Mixers")
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
        self.tab2_grid = QGridLayout()
        self.tab2_grid.setSpacing(10)
        self.tab2_grid.addWidget(self.start_mixer_one, 1, 0, 1, 2)
        self.tab2_grid.addWidget(self.start_mixer_two, 1, 2, 1, 2)
        
        ## Tab 3 Layout
        self.tab3_grid = QGridLayout()
        self.tab3_grid.setSpacing(10)
        self.tab3_grid.addWidget(self.view_camera, 1, 0, 1, 2)
        
        
        #self.setLayout(grid)
        self.tab1.setLayout(self.tab1_grid)
        self.tab2.setLayout(self.tab2_grid)
        self.tab3.setLayout(self.tab3_grid)
        self.tab_layout = QGridLayout(self)
        self.tab_layout.addWidget(self.tabs)

        self.setGeometry(300,300,300,300)
        self.setWindowTitle("Poseidon Pumps")
        self.show()

    def run_button_click(self):
        clicked_button = self.sender()
        if clicked_button.styleSheet() == self.run_button_style_string:
            if clicked_button.objectName() == 'pump_one_run':
                self.board.run_pump()
            clicked_button.setStyleSheet(self.pause_button_style_string)
            clicked_button.setText('Pause')
        elif clicked_button.styleSheet() == self.pause_button_style_string:
            clicked_button.setStyleSheet(self.run_button_style_string)
            clicked_button.setText('Run')
        self.run_all_pumps_consistency_check()

    def run_all_pumps_consistency_check(self):
        if self.pump_one_run.styleSheet() == self.run_button_style_string and \
            self.pump_two_run.styleSheet() == self.run_button_style_string and \
            self.pump_three_run.styleSheet() == self.run_button_style_string:
            self.run_all_pumps.setStyleSheet(self.run_button_style_string)
            self.run_all_pumps.setText('Run All Pumps')
        elif self.pump_one_run.styleSheet() == self.pause_button_style_string and \
            self.pump_two_run.styleSheet() == self.pause_button_style_string and \
            self.pump_three_run.styleSheet() == self.pause_button_style_string:
            self.run_all_pumps.setStyleSheet(self.pause_button_style_string)
            self.run_all_pumps.setText('Pause All Pumps')

    def run_all_pumps_button_click(self):
        clicked_button = self.sender()
        if clicked_button.styleSheet() == self.run_button_style_string:
            clicked_button.setStyleSheet(self.pause_button_style_string)
            clicked_button.setText('Pause All Pumps')
            if self.pump_one_run.styleSheet() != self.pause_button_style_string:
                self.pump_one_run.setStyleSheet(self.pause_button_style_string)
                self.pump_one_run.setText('Pause')
            if self.pump_two_run.styleSheet() != self.pause_button_style_string:
                self.pump_two_run.setStyleSheet(self.pause_button_style_string)
                self.pump_two_run.setText('Pause')
            if self.pump_three_run.styleSheet() != self.pause_button_style_string:
                self.pump_three_run.setStyleSheet(self.pause_button_style_string)
                self.pump_three_run.setText('Pause')
        elif clicked_button.styleSheet() == self.pause_button_style_string:
            clicked_button.setStyleSheet(self.run_button_style_string)
            clicked_button.setText('Run All Pumps')
            if self.pump_one_run.styleSheet() != self.run_button_style_string:
                self.pump_one_run.setStyleSheet(self.run_button_style_string)
                self.pump_one_run.setText('Run')
            if self.pump_two_run.styleSheet() != self.run_button_style_string:
                self.pump_two_run.setStyleSheet(self.run_button_style_string)
                self.pump_two_run.setText('Run')
            if self.pump_three_run.styleSheet() != self.run_button_style_string:
                self.pump_three_run.setStyleSheet(self.run_button_style_string)
                self.pump_three_run.setText('Run')

    def stop_button_click(self):
        clicked_button_name = self.sender().objectName()
        if clicked_button_name == 'pump_one_stop':
            if self.pump_one_run.styleSheet() == self.pause_button_style_string:
                self.pump_one_run.setStyleSheet(self.run_button_style_string)
                self.pump_one_run.setText('Run')
        elif clicked_button_name == 'pump_two_stop':
            if self.pump_two_run.styleSheet() == self.pause_button_style_string:
                self.pump_two_run.setStyleSheet(self.run_button_style_string)
                self.pump_two_run.setText('Run')
        elif clicked_button_name == 'pump_three_stop':
            if self.pump_three_run.styleSheet() == self.pause_button_style_string:
                self.pump_three_run.setStyleSheet(self.run_button_style_string)
                self.pump_three_run.setText('Run')
        self.run_all_pumps_consistency_check()


if __name__=='__main__':
    app = QApplication(sys.argv)
    pump_control = Pump_interface()
    sys.exit(app.exec_())

