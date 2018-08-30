# Poseidon project - open source bioinstrumentation

The poseidon syringe pumps and microscope is a customizable open source alternative to commercial systems that costs less than $400 and can be assembled in an hour. It uses 3D printed parts and common components that can be easily purchased either from Amazon or other retailers. The microscope and pumps can be used together in microfluidics experiments, but the pumps can also be connected to a computer and used independently for other experiments.


### Open source syringe pumps and Raspberry Pi microscope
![mvimg_20180111_222424](https://user-images.githubusercontent.com/12504176/34991157-69e99c68-fa7d-11e7-8a77-660660820391.jpg)

# Overview

The poseidon system was designed to be customizable. It uses the [Raspberry Pi](https://www.raspberrypi.org/)  and [Arduino](https://www.arduino.cc/) electronics boards, which are supported by a strong ecosystem of open source hardware and software, facilitating the implementation of new functionalities.

The pump driver uses an Arduino with a [CNC shield](https://blog.protoneer.co.nz/arduino-cnc-shield/) to run up to three pumps. Each pump has a stepper motor that drives lead screw which in turn moves a sled that is mounted on linear bearings. The displacement of the sled moves the syringe forward or backward allowing the user to dispel or intake liquid.

The controller station uses Raspberry Pi with a touchscreen to connect to the Arduino and microscope via USB. Because the microscope and Arduino use USB connections, the they can alternatively be connected to any computer instead of a Raspberry Pi. 

## Components of the poseidon system

### Computer Aided Design (CAD) files of the 3D printed components

The 3D printed components can be fabricated on any desktop fused filament fabrication (FFF) 3D printer. They were designed using [Autodesk Fusion 360](http://autodesk.com/fusion360), a proprietary CAD software that offers free academic licenses. To modify the 3D models the user can either use Fusion 360 or any other CAD software. 

- STL files, Fusion 360 archive files and bill of materials are available on the hardware folder.
- Fusion360 interactive view of [poseidon microscope CAD](http://a360.co/2krZoEk)
- Fusion360 interactive view of [poseidon pump](https://a360.co/2Ph19kC).
- Bill of materials with prices and vendor links on a [Google Spreadheet](https://docs.google.com/spreadsheets/d/e/2PACX-1vSvQ-_a3mc86q8SK5kn30WIgRPjqy6SA3FfCof95V2DZ1-tXybiHstTbmEUGz1TtDjSifnlR6G8LoQv/pubhtml)

### Python pump controller software and Graphical User Interface (GUI) to control the Arduino

The Python scripts are available on the software folder.

The GUI was created using [Qt designer](http://doc.qt.io/qt-5/qtdesigner-manual.html), a drag and drop application for organizing buttons that allows the used to easily make modifications. This GUI is used to interface with a Python script that controls both the microscope and Arduino via USB. 

The software you will need to run on your compuer in order to control the Arduino is located in the `software` folder. You have the option of either running the source code in Python or choosing the appropriate binary file for your operating system and executing that.

** Download of binary files: **
- [Windows](link) 
- [Mac OS](link)
- [Ubuntu](link)
- [Raspbian](link)

### Arduino firmware used to drive the motors, 
The Arduino should be flashed with the `arduino_serialCOM_v0.1.ino` sketch, available the software folder.

The pumps are driven by an Arduino board that interprets commands sent via USB and sends the proper signal to control the stepper motor movement. The user can take advantage of this by developing custom movement patterns using the Arduino functions.

For directions on how to flash an arduino please refer to the official guide: https://www.arduino.cc/en/Guide/HomePage

# Detailed instructions

### Running the `poseidon_main.py` Python script on Raspbian

To run `poseidon_main.py` in a Raspberry Pi with a fresh install of Raspbian, Python 3 with pyqt5 need to be installed, together with a few packages.
```
sudo apt-get install python3-pyqt5

# now need to use python3.5 gui.py to invoke the python3 that has pyqt5!
pip3 install --upgrade -pip
pip3 install pyserial
pip3 install opencv-python

# opencv requires a some extra binaries 
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev
sudo apt-get install libqtgui4
sudo apt-get install libqt4-qt3support
sudo apt-get install libqt4-test

# now the script can be called
python3.5 poseidon_main.py
```

### Installing pyinstaller on Windows 7 and making a single executable for the Python controller

To create a single .exe file we use 
Using Python 3.7 (installing pyqt5 form pip) or 3.4 (isntalling pyqt5 from executable) on Windows 10 did not work. 
Python 3.7 yields terrible dependency errors from pyinstaller and with Python 3.4 after making the executable pyqt complains apparently because of windows 10. The solution was to use a machine with Windows 7. 

After installing Python 3.5.4 (https://www.python.org/downloads/release/python-354/), using the `Windows x86-64 executable installer`, these dependencies should install without problems:
```
python -m pip install pyqt5
python -m pip install pyserial
python -m pip install opencv-python
```
To compile a binary you should write `PyInstaller`, instead of `pyinstaller`...
```
python -m PyInstaller --version
python -m PyInstaller poseidon_main.py
```
Just doing `python -m PyInstaller gui.py` with Python 3.5 on windows 7 threw up some errors, the following line solved the issue.
Described here: https://stackoverflow.com/questions/51324754/python-3-6-x-pyinstaller-gives-error-no-module-named-pyqt5-sip
```
python -m PyInstaller -F poseidon_main.py --hidden-import PyQt5.sip
```


## Arduino hardware setup information

We use the [Arduino CNC shield](http://wiki.keyestudio.com/index.php/Ks0095_Arduino_CNC_Kit_/_CNC_Shield_V3.0_%2Bkeyestudio_Uno_R3%2B4pcs_a4988_Driver_/_GRBL_Compatible)
to allow for up to three pumps can be controlled from a computer or from the Rapsberry Pi microscope.

The software is configured to run the stepper motors with 200 steps per revolution at 1/8 microstepping, which translates to 800 steps per rotation. To configure this, it is necessary to add a jumper between the MODE1 pins of the Arduino CNC shield, as shown in the picture below. More information about microstepping can be found in the product page for the [DRV8825 Stepper Motor Driver](https://www.pololu.com/product/2133), which is used by the CNC shield. 

![microsteppingpng](https://user-images.githubusercontent.com/12504176/34992088-d2e04ca0-fa80-11e7-9dde-99b1894fbe5c.PNG)

Here is how the board looks with the stepper motors connected:

![full_board](https://user-images.githubusercontent.com/12504176/35099661-b8e55262-fc0d-11e7-86df-f2927111ce1a.PNG)



## Assembly instructions for the Poseidon syringe pumps

Detailed written instructions are on the way. In the meantime you can [click here for a walkthrough video](https://photos.app.goo.gl/xIplnxrbvsixwfU03).


## Startup Tips
Before stating the Python controller, make sure the Arduino is connected via USB to the computer or Rapsberry Pi microscope, that the CNC shield is powered, and that the 3 motors are plugged in. Test to see that they are moving in the correct direction when expelling, if not simply rotate the relevant stepper motor connectors 180 degrees and plug them back in.


