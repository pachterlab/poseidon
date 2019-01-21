---
layout: page
title: "Software"
group: navigation
---

{% include JB/setup %}

The poseidon GUI was created using [Qt designer](http://doc.qt.io/qt-5/qtdesigner-manual.html), a drag and drop application for organizing buttons that allows the used to easily make modifications. This GUI is used to interface with a Python script that controls both the microscope and Arduino via USB. 

The pumps are driven by an Arduino board that interprets commands sent via USB and sends the proper signal to control the stepper motor movement. The user can take advantage of this by developing custom movement patterns using the Arduino functions.

![poseidon_gui](https://user-images.githubusercontent.com/12504176/51095267-6f214600-1768-11e9-83d6-207cb360bdec.png)


## Getting started 

 **Running your pump for the first time (VIDEO):** https://youtu.be/VmoB_fPc4L4


To run the poseidon GUI controller you have the option of either running from the source code in Python or choosing the appropriate binary file from the [poseidon releases page](https://github.com/pachterlab/poseidon/releases) and executing it. 

The Python scripts are available in the repository [`SOFTWARE` folder](https://github.com/pachterlab/poseidon/tree/release/SOFTWARE). The two Python scripts needed are `poseidon_main.py` and `poseidon_controller_gui.py`.

Before you can run the GUI controller, the Arduino should be flashed with the [`arduino_serialCOM_v0.1.ino` sketch](https://github.com/pachterlab/poseidon/tree/release/SOFTWARE/arduino_serialCOM_v0.1), available the `SOFTWARE` folder.

For directions on how to flash an arduino please refer to the official guide: [https://www.arduino.cc/en/Guide/HomePage](https://www.arduino.cc/en/Guide/HomePage)


### Startup Checklist
Before starting the Python controller, make sure
1. The Arduino has the firmware uploaded to it
2. The Arduino is connected via USB to the computer or Rapsberry Pi microscope
3. You have appropriately placed jumpers on the CNC Sheild to allow for microstepping and hardware enabling, as shown in the [arduino CNC shield build video](https://pachterlab.github.io/poseidon/hardware).
4. The CNC shield is powered, and that all motors are plugged in to the CNC sheild

A schematic of how the system parts connect is shown below.

![poseidon_setup](https://user-images.githubusercontent.com/12504176/51095573-9d078a00-176a-11e9-9fa8-dbe915b4b94e.png)



#### License

poseidon is distributed under the [BSD 2-Clause License](https://github.com/pachterlab/poseidon/blob/release/LICENSE)

