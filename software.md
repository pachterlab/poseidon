---
layout: page
title: "Software"
group: navigation
---

{% include JB/setup %}


![poseidon_gui](https://user-images.githubusercontent.com/12504176/44837086-7565ba00-abed-11e8-9f49-90933ecdb3e8.png)

### Source Code

Source code, bill of materials and 3D model files are available at [https://github.com/pachterlab/poseidon](https://github.com/pachterlab/poseidon).

The GUI was created using [Qt designer](http://doc.qt.io/qt-5/qtdesigner-manual.html), a drag and drop application for organizing buttons that allows the used to easily make modifications. This GUI is used to interface with a Python script that controls both the microscope and Arduino via USB. 

The software you will need to run on your computer in order to control the Arduino is the `poseidon_main.py` script located in the `software` folder. (it also needs the `poseidon_controller_gui.py`). You have the option of either running from the source code in Python or choosing the appropriate binary file below for your operating system and executing that. You still need to flash the arduino as described in the next section.

##### Binaries
- [Windows](https://github.com/pachterlab/poseidon/releases/download/v1.0.0/poseidon_main_v1.0.0_windows_executable_2018-08-29.exe) 
- [Mac OS](https://github.com/pachterlab/poseidon/releases/download/v1.0.0/poseidon_main_v1.0.0_mac_executable_2018-08-29)
- [Ubuntu] (coming soon)
- [Raspbian](https://github.com/pachterlab/poseidon/releases/download/v1.0.0/poseidon_main_v1.0.0_raspbian_executable_2018-08-29)


### Arduino Firmware
The Arduino should be flashed with the `arduino_serialCOM_v0.1.ino` sketch, available the software folder.

The pumps are driven by an Arduino board that interprets commands sent via USB and sends the proper signal to control the stepper motor movement. The user can take advantage of this by developing custom movement patterns using the Arduino functions.

For directions on how to flash an arduino please refer to the official guide: [https://www.arduino.cc/en/Guide/HomePage](https://www.arduino.cc/en/Guide/HomePage)


#### License

poseidon is distributed under the [BSD 2-Clause License[(https://github.com/pachterlab/poseidon/blob/release/LICENSE)

