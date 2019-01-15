---
layout: page
title: "About"
group: navigation
---

{% include JB/setup %}

###  __poseidon__ project: open source bioinstrumentation

The Poseidon syringe pump and microscope system is an open source alternative to commercial systems. that [costs less than $400](https://docs.google.com/spreadsheets/d/e/2PACX-1vSvQ-_a3mc86q8SK5kn30WIgRPjqy6SA3FfCof95V2DZ1-tXybiHstTbmEUGz1TtDjSifnlR6G8LoQv/pubhtml) and can be assembled in an hour. It uses 3D printed parts and common components that can be easily purchased either from Amazon or other retailers. The microscope and pumps can be used together in microfluidics experiments, or independently for other applications. The pumps and microscope can be run from a Windows, Mac, Linux, or Raspberry Pi computer with an easy to use GUI.

#### What is included?
* Computer Aided Design (CAD) files of the 3D printed components.
* Controller software (Python) and a graphical user interface (GUI) to control the pumps.
* Arduino firmware to send commands to the motors and receive commands from the GUI.
* Bill of materials for sourcing and purchasing materials.
* Detailed assembly instructions of hardware compnents.
* Single click executable files for Mac, Windows, Linux, and Raspberry Pi systems.

All files are available at the poseidon GitHub repository: [https://github.com/pachterlab/poseidon](https://github.com/pachterlab/poseidon)

![about](https://user-images.githubusercontent.com/12504176/35100297-31df303c-fc10-11e7-871c-133837e9449c.PNG)


#### Overview 

The poseidon system was designed to be customizable. It uses the [Raspberry Pi](https://www.raspberrypi.org/)  and [Arduino](https://www.arduino.cc/) electronics boards, which are supported by a strong ecosystem of open source hardware and software, facilitating the implementation of new functionalities.

The pump driver uses an Arduino with a [CNC shield](https://blog.protoneer.co.nz/arduino-cnc-shield/) to run up to three pumps. Each pump has a stepper motor that drives lead screw which in turn moves a sled that is mounted on linear bearings. The displacement of the sled moves the syringe forward or backward allowing the user to dispel or intake liquid.

The microscope controller station uses Raspberry Pi with a touchscreen to connect to the Arduino and microscope via USB. Because the microscope and Arduino use USB connections, the they can alternatively be connected to any computer instead of a Raspberry Pi. 

![cam_pump_ortho](https://user-images.githubusercontent.com/12504176/44077943-22281bac-9f5a-11e8-8e48-0c1936c4b787.png)

#### Hardware and software components developed for the poseidon system 

1. Computer Aided Design (CAD) files for the [pumps](https://a360.co/2B9KUDZ) and [microscope controller station](https://a360.co/2P7rClx)
2. Pump controller software and Graphical User Interface (GUI) to control the Arduino
3. Arduino firmware used to drive the motors

The 3D printed components can be fabricated on any desktop fused filament fabrication (FFF) 3D printer. They were designed using [Autodesk Fusion 360](http://autodesk.com/fusion360), a proprietary CAD software that offers free academic licenses. To modify the 3D models the user can either use Fusion 360 or any other CAD software. 

The GUI was created using [Qt designer](http://doc.qt.io/qt-5/qtdesigner-manual.html), a drag and drop application for organizing buttons that allows the used to easily make modifications. This GUI is used to interface with a Python script that controls both the microscope and Arduino via USB. 

The pumps are driven by an Arduino board that interprets commands sent via USB and sends the proper signal to control the stepper motor movement. The user can take advantage of this by developing custom movement patterns using the Arduino functions.

<iframe src="https://myhub.autodesk360.com/ue29183a6/shares/public/SH7f1edQT22b515c761e2c8d8d3b6a07c5ab?mode=embed" width="640" height="480" allowfullscreen="true" webkitallowfullscreen="true" mozallowfullscreen="true"  frameborder="0"></iframe>

<iframe src="https://myhub.autodesk360.com/ue29183a6/shares/public/SH7f1edQT22b515c761ebfc710668fe6075c?mode=embed" width="640" height="480" allowfullscreen="true" webkitallowfullscreen="true" mozallowfullscreen="true"  frameborder="0"></iframe>

#### Authors

The poseidon system was developed at the [Pachter Lab](https://pachterlab.github.io) at Caltech by:
- [Sina Booeshaghi](https://www.sinabooeshaghi.com/)
- [Dylan Bannon](https://github.com/dylanbannon/)
- [Eduardo Beltrame](https://github.com/munfred/)
- [Jase Gehring](https://scholar.google.com/citations?user=63ZRebIAAAAJ&hl=en)
- [Lior Pachter](https://github.com/lakigigar)

#### Prior work and references

As with everything in life, the Poseidon project was not developed in a vacuum. 

The pumps design was based on the open source syringe pumps published by the [Pearce Research Group](http://www.mse.mtu.edu/~pearce/Index.html):

[Open-Source Syringe Pump Library <br>
Bas Wijnen, Emily J. Hunt, Gerald C. Anzalone, Joshua M. Pearce <br>
PLOS One, 2014. https://doi.org/10.1371/journal.pone.0107216](http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0107216)

With subsequent refinements published on [http://www.appropedia.org/Open-source_syringe_pump](http://www.appropedia.org/Open-source_syringe_pump)

The microscope was based on a design published by the [Satija Lab](http://satijalab.org/):

[Single-Cell Single-cell RNA-seq of rheumatoid arthritis synovial tissue using low-cost microfluidic instrumentation <br>
William Stephenson, Laura T. Donlin, Andrew Butler, Cristina Rozo, Ali Rashidfarrokhi, Susan M. Goodman, Lionel B. Ivashkiv, Vivian P. Bykerk, Dana E. Orange, Robert B. Darnell, Harold P. Swerdlow, Rahul Satija <br>
Nature Communicationsvolume 9, Article number: 791 (2018)](https://www.nature.com/articles/s41467-017-02659-x)

All necessary files for inDrops assembly are avaialble on [Metafluidics](https://metafluidics.org/devices/minidrops/)

#### License

poseidon is distributed under the [BSD 2-Clause License](https://github.com/pachterlab/poseidon/blob/release/LICENSE)
