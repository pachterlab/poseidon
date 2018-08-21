# Poseidon project - open source bioinstrumentation

The poseidon syringe pumps and microscope is a customizable open source alternative to commercial systems that costs less than $500 and can be assembled in an hour. It uses 3D printed parts and common components that can be easily purchased from Amazon or other retailers. The microscope and pumps can be used together in microfluidics experiments, but the pumps can also be connected to a computer and used independently for other experiments.


## Open source syringe pumps and Raspberry Pi microscope
![mvimg_20180111_222424](https://user-images.githubusercontent.com/12504176/34991157-69e99c68-fa7d-11e7-8a77-660660820391.jpg)

## All the parts for 3 pumps and a microscope cost under $400
![mvimg_20180111_211022](https://user-images.githubusercontent.com/12504176/34991323-0a6b41aa-fa7e-11e7-8e57-fbb78b54cc67.jpg)


# Setup Information

The poseidon system was designed to be customizable. It uses the [Raspberry Pi](https://www.raspberrypi.org/)  and [Arduino](https://www.arduino.cc/) electronics boards, which are supported by a strong ecosystem of open source hardware and software, facilitating the implementation of new functionalities.

The pump driver uses an Arduino with a [CNC shield](https://blog.protoneer.co.nz/arduino-cnc-shield/) to run up to three pumps. Each pump has a stepper motor that drives lead screw which in turn moves a sled that is mounted on linear bearings. The displacement of the sled moves the syringe forward or backward allowing the user to dispel or intake liquid.

The controller station uses Raspberry Pi with a touchscreen to connect to the Arduino and microscope via USB. Because the microscope and Arduino use USB connections, the they can alternatively be connected to any computer instead of a Raspberry Pi. 

The following components developed for the poseidon system are made available:
1. Computer Aided Design (CAD) files of the 3D printed components
2. Pump controller software and Graphical User Interface (GUI) to control the Arduino
3. Arduino firmware used to drive the motors

The 3D printed components can be fabricated on any desktop fused filament fabrication (FFF) 3D printer. They were designed using [Autodesk Fusion 360](http://autodesk.com/fusion360), a proprietary CAD software that offers free academic licenses. To modify the 3D models the user can either use Fusion 360 or any other CAD software. 

The GUI was created using [Qt designer](http://doc.qt.io/qt-5/qtdesigner-manual.html), a drag and drop application for organizing buttons that allows the used to easily make modifications. This GUI is used to interface with a Python script that controls both the microscope and Arduino via USB. 

The pumps are driven by an Arduino board that interprets commands sent via USB and sends the proper signal to control the stepper motor movement. The user can take advantage of this by developing custom movement patterns using the Arduino functions.

## Arduino software information

The Arduino should be running some version of Configurable Firmata. A version is included in this repository at `software/arduino_firmware/ConfigurableFirmata`.

To upload an optimized version of this firmware to your Arduino, first copy this repository to your computer. Then, open up the file `software/arduino_firmware/ConfigurableFirmata/ConfigurableFirmata.ino` using the Arduino IDE, version 1.8.0 or greater. (Available at [https://www.arduino.cc/en/Main/Software](https://www.arduino.cc/en/Main/Software).) Finally, click the 'verify' and 'upload' buttons in the IDE, in that order. If no errors appear in the IDE console window, then the optimized verion of Configurable Firmata has been uploaded to your Arduino! Driving your pumps now is just a matter of plugging everything in!


## Arduino hardware information

We use the [Arduino CNC shield](http://wiki.keyestudio.com/index.php/Ks0095_Arduino_CNC_Kit_/_CNC_Shield_V3.0_%2Bkeyestudio_Uno_R3%2B4pcs_a4988_Driver_/_GRBL_Compatible)
to allow for up to three pumps can be controlled from a computer or from the Rapsberry Pi microscope.

The software is configured to run the stepper motors with 200 steps per revolution at 1/4 microstepping, which translates to 800 steps per rotation. To configure this, it is necessary to add a jumper between the MODE1 pins of the Arduino CNC shield, as shown in the picture below. More information about microstepping can be found in the product page for the [DRV8825 Stepper Motor Driver](https://www.pololu.com/product/2133), which is used by the CNC shield. 

![microsteppingpng](https://user-images.githubusercontent.com/12504176/34992088-d2e04ca0-fa80-11e7-9dde-99b1894fbe5c.PNG)

Here is how the board looks with the stepper motors connected:

![full_board](https://user-images.githubusercontent.com/12504176/35099661-b8e55262-fc0d-11e7-86df-f2927111ce1a.PNG)


## Software information

The software you will need to run on your compuer in order to control the Arduino is located in the `software` folder. You have the option of either running the source code in Python or choosing the appropriate binary file for your operating system and executing that.


## Assembly instructions for the Poseidon syringe pumps

Detailed written instructions are on the way. In the meantime you can [click here for a walkthrough video](https://photos.app.goo.gl/xIplnxrbvsixwfU03).


## Startup Tips
Before stating the Python controller, make sure the Arduino is connected via USB to the computer or Rapsberry Pi microscope, that the CNC shield is powered, and that the 3 motors are plugged in. Test to see that they are moving in the correct direction when expelling, if not simply rotate the relevant stepper motor connectors 180 degrees and plug them back in.


