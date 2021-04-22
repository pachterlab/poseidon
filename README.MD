![poseidon_logo](https://user-images.githubusercontent.com/10369156/51078049-4152d900-1664-11e9-9296-1b153aca908b.png)

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)

## poseidon: Open source bioinstrumentation
An easy-to-use, highly customizable, and open source syringe pump and microscope system.

**Documentation**: https://pachterlab.github.io/poseidon/

**Paper**: A. Sina Booeshaghi, Eduardo da Veiga Beltrame, Dylan Bannon, Jase Gehring and Lior Pachter, <a href="https://www.nature.com/articles/s41598-019-48815-9">Principles of open source bioinstrumentation applied to the poseidon syringe pump system</a>, Scientific Reports <b>9</b>, Article number: 12385 (2019).

## The tl;dr

The poseidon syringe pump and microscope system is an open source alternative to commercial systems. It costs less than \$400 and can be assembled in an hour. It uses 3D printed parts and common components that can be easily purchased either from Amazon or other retailers. The microscope and pumps can be used together in microfluidics experiments, or independently for other applications. The pumps and microscope can be run from a Windows, Mac, Linux, or Raspberry Pi computer with an easy to use GUI.

![ortho_edit](https://user-images.githubusercontent.com/10369156/51078589-5a5f8800-166c-11e9-8312-50b374d574d9.jpg)

## What is included?
* Computer Aided Design (CAD) files of the 3D printed components.
* Controller software (Python) and a graphical user interface (GUI) to control the pumps.
* Arduino firmware to send commands to the motors and receive commands from the GUI.
* Bill of materials for sourcing and purchasing materials.
* Detailed assembly instructions of hardware components.
* Single click executable files for Mac, Windows, Linux, and Raspberry Pi systems.

<p align="center">
  <img src="https://user-images.githubusercontent.com/10369156/51273076-a5d1a900-1980-11e9-82a2-6b78c2ead10f.gif">
</p>

## Getting Started
### 3D printing components and purchasing hardware
The 3D printed components can be fabricated on any desktop fused filament fabrication (FFF) 3D printer. They were designed using [Autodesk Fusion 360](http://autodesk.com/fusion360), a proprietary CAD software that offers free academic licenses.

- Fusion360 interactive view of [poseidon microscope CAD](http://a360.co/2krZoEk).
- Fusion360 interactive view of [poseidon pump](https://a360.co/2Ph19kC).
- STL, STEP, IGES, Fusion 360 archive files, and bill of materials are available in the `HARDWARE/` folder.
- Bill of materials with prices and vendor links on a [Google Spreadsheet](https://docs.google.com/spreadsheets/d/1AHBLf0PbtGDgqNbbK6QO31s7ES9_1uCw_NeKWHHPTM4/edit?usp=sharing).

### Build Videos
Syringe Pump: https://www.youtube.com/watch?v=7YSiO6usR1M  
Microscope  : https://www.youtube.com/watch?v=Szg-vjukonA  
Arduino     : https://www.youtube.com/watch?v=Xl02fsRCJ7U  
Raspberry Pi: https://www.youtube.com/watch?v=g3pXNY8snOg  

Running poseidon: https://youtu.be/VmoB_fPc4L4

### Setting up the Arduino 
We use the [Arduino CNC shield](http://wiki.keyestudio.com/index.php/Ks0095_Arduino_CNC_Kit_/_CNC_Shield_V3.0_%2Bkeyestudio_Uno_R3%2B4pcs_a4988_Driver_/_GRBL_Compatible)
to allow for up to three pumps can be controlled from a computer or from the Rapsberry Pi microscope.

The software is configured to run the stepper motors with 200 steps per revolution at 1/32 microstepping, which translates to 6400 steps per rotation. To configure this, it is necessary to add 3 jumpers between the M0, M1 and M2 pins of the Arduino CNC shield. More information about microstepping can be found in the product page for the [DRV8825 Stepper Motor Driver](https://www.pololu.com/product/2133), which is used by the CNC shield. See the build videos for more detail. 

The Arduino should be flashed with the `arduino_serialCOM_v0.1.ino` sketch, available in the `SOFTWARE/` folder.

**Make sure to download and install the [AccelStepper library](https://www.airspayce.com/mikem/arduino/AccelStepper/index.html)**. To install, unzip the zip file to the libraries sub-folder of your sketchbook, if you get stuck here is a [how-to](https://www.arduino.cc/en/guide/libraries).

The pumps are driven by an Arduino board that interprets commands sent via USB and sends the signals to control the stepper motor movement. For directions on how to flash an arduino please refer to the official guide: https://www.arduino.cc/en/Guide/HomePage

### Installing software
The Python scripts are available in the `SOFTWARE/` folder. The GUI was created using [Qt designer](http://doc.qt.io/qt-5/qtdesigner-manual.html), a drag and drop application for organizing buttons that allows the used to easily make modifications. This GUI is used to interface with a Python script that controls both the microscope and Arduino via USB. 

The software you will need to run on your computer in order to control the Arduino is the `poseidon_main.py` script located in the `SOFTWARE/` folder (also included is `poseidon_controller_gui.py` which is needed). 

You have the option of either (1) running from the source code in Python or (2) choosing the appropriate binary file below for your operating system and executing it. Before you run the controller code, MAKE SURE YOU HAVE INSTALLED THE ARDUINO FIRMWARE!!

## Startup Checklist
Before starting the Python controller, make sure
1. The Arduino has the firmware uploaded to it
2. The Arduino is connected via USB to the computer or Rapsberry Pi microscope
3. You have appropriately placed jumpers on the CNC Sheild to allow for microstepping and hardware enabling (discussed in build video).
4. The CNC shield is powered, and that all motors are plugged in to the CNC sheild

## Running the software and Testing the pumps
There are two ways to run the controller. The easiest way is to just double click the executable available below. Simply download the executable, double click it, and begin using it. Navigate to the **Releases** tab at the top to find the following executables.

- Windows
- Mac OS
- Ubuntu (coming soon)
- Raspbian

# Tips/Hints
Things that we have learned along the way that may help with your build.
- Basic tests indicate that pressures up to 4 MPa can be acheived with 1 microstep and a 1 mL syringe.

- Set the current limit on your motor controller to vary the stall torque. Increasing the current to the motor increases the stall torque and increases the max pressure that your syringe pump can run at. [How to set the current limit](https://www.youtube.com/watch?feature=player_embedded&v=89BHS9hfSUk).

- We recommend [changing the password on the Raspberry Pi](https://raspberrypi.stackexchange.com/questions/67181/how-to-change-a-password) for added security.

- The speeds and flow rates of the system are limited by the microstepping and the syringe size used.

<img width="1068" alt="flow_rates" src="https://user-images.githubusercontent.com/10369156/51273546-d49c4f00-1981-11e9-8946-9ec0baf57dbd.png">

---------------------------------------------------

If you want to run the system from the source code then follow the instructions below.
### Windows, Mac, Linux
First make sure you have Python 3 installed on your machine. Then install PyQt5. To install PyQt5 use `brew install pyqt5` or `conda install pyqt` if you are using anaconda. If you are on Linux you can do `sudo apt-get install python3-pyqt5`. Now we need to add a few packages:
```
pip3 install --upgrade -pip
pip3 install pyserial
pip3 install opencv-python
```
On Linux opencv requires extra binaries
```
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev
sudo apt-get install libqtgui4
sudo apt-get install libqt4-qt3support
sudo apt-get install libqt4-test
```
Now you can run 
```
# now the script can be called
python3.5 poseidon_main.py
```
### Raspberry Pi
To run `poseidon_main.py` on a Raspberry Pi with a fresh install of Raspbian, Python 3 with pyqt5 need to be installed, together with a few packages.
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
### Now that you have everything installed, go ahead and test it out!
(1) Select the port that your Arduino is plugged into. If you don't see the right port, press `update port`. 
(2) Set your microstepping
(3) Input appropriate settings
(4) Select `connect to controller`
(5) Select `Send all settings to controller`
(6) Go to the controller tab, select all three checkboxes and press `Jog +`

If the sleds are not moving in the right direction simply rotate the relevant stepper motor plug (that connects to the CNC shield) 180 degrees and plug it back in.


## How does it work, and how to modify it. (Very easy!)
The poseidon system was designed to be customizable. It uses the [Raspberry Pi](https://www.raspberrypi.org/)  and [Arduino](https://www.arduino.cc/) electronics boards, which are supported by a strong ecosystem of open source hardware and software, facilitating the implementation of new functionalities.

The pump driver uses an Arduino with a [CNC shield](https://blog.protoneer.co.nz/arduino-cnc-shield/) to run up to three pumps. Each pump has a stepper motor that drives lead screw which in turn moves a sled that is mounted on linear bearings. The displacement of the sled moves the syringe forward or backward allowing the user to dispel or intake liquid.

The controller station uses a Raspberry Pi with a touchscreen to connect to the Arduino and microscope via USB. Because the microscope and Arduino use USB connections, they can alternatively be connected to a computer instead of a Raspberry Pi. 

To modify the 3D models, users can either use Fusion 360 or any other CAD software. Simply open up the components, located in the `HARDWARE` folder, and get editing! Once you're done, go ahead and print out the parts and assemble them.

Most of the modifications to the code will be done in `poseidon_main.py` and to the GUI. If you want to edit the GUI, first make sure you have installed PyQt Designer (which should have been installed when you downloaded and installed PyQt5, so you can search for it on your computer `Designer.exe` (Windows) or `Designer` in your applications folder (Mac). Open up the `poseidon_controller_gui.ui` in Designer and make whatever modifications you'd like. Then when you are done, you need to convert the modified `.ui` file to a `.py` file. Go to the terminal, navigate to the folder where you have `poseidon_controller_gui.ui` and run the command `pyuic5 poseidon_controller_gui.ui > poseidon_controller_gui.py`.

When you are done editing the `poseidon_main.py` you can recreate the single click executable files by following the instructions below.

### Installing pyinstaller on Windows 7 and making a single executable for the Python controller
 
Using Python 3.7 (installing pyqt5 form pip) or 3.4 (installing pyqt5 from executable) on Windows 10 did not work. 
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
## Safety Considerations
Please review the license before using/developing/distribution poseidon. 

The poseidon syringe pump system uses 3D printed PLA plastic and standard off the shelf components which do not pose a health hazard if handled correctly. Improper handling of plastics however can create hazards when working with organic solvents. Initial tests of the poseidon syringe pump showed excessive bending of the syringe pump body. We mitigated this by reinforcing the body with set screws and a thicker base. To mitigate the possibility of catastrophic failure due to clogging we set the reference voltage on the motor controller such that the motor stalls when the pressure in a 1 mL syringe reaches 4 MPa.

Before using the poseidon system in a wetlab environment, please ensure that you have thoroughly tested its functionality for your use case in a dry lab. Once the poseidon system has been moved into a wetlab, it should not be moved back to a drylab or dry workbench.

If you plan to build on the poseidon system, ensure that you communicate any safety concerns that you may have with your design to potential users and collaborators.

## Authors

The poseidon system was developed by the [Pachter Lab](https://pachterlab.github.io) at Caltech by:
- [Sina Booeshaghi](https://sinabooeshaghi.com/)
- [Eduardo Beltrame](https://github.com/munfred/)
- [Dylan Bannon](https://github.com/dylanbannon/)
- [Jase Gehring](https://scholar.google.com/citations?user=63ZRebIAAAAJ&hl=en)
- [Lior Pachter](https://github.com/lakigigar)


#### Prior work and references

The poseidon project is based on a number of other open source projects and papers.

The pump design was based on the open source syringe pumps published by the [Pearce Research Group](http://www.mse.mtu.edu/~pearce/Index.html):

[Open-Source Syringe Pump Library <br>
Bas Wijnen, Emily J. Hunt, Gerald C. Anzalone, Joshua M. Pearce <br>
PLOS One, 2014. https://doi.org/10.1371/journal.pone.0107216](http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0107216)

With subsequent refinements published on [http://www.appropedia.org/Open-source_syringe_pump](http://www.appropedia.org/Open-source_syringe_pump)

The microscope was based on a design published by the [Satija Lab](http://satijalab.org/):

[Single-Cell Single-cell RNA-seq of rheumatoid arthritis synovial tissue using low-cost microfluidic instrumentation <br>
William Stephenson, Laura T. Donlin, Andrew Butler, Cristina Rozo, Ali Rashidfarrokhi, Susan M. Goodman, Lionel B. Ivashkiv, Vivian P. Bykerk, Dana E. Orange, Robert B. Darnell, Harold P. Swerdlow, Rahul Satija <br>
Nature Communicationsvolume 9, Article number: 791 (2018)](https://www.nature.com/articles/s41467-017-02659-x)

All necessary files are available on [Metafluidics](https://metafluidics.org/devices/minidrops/)
