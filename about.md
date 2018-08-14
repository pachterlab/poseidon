---
layout: page
title: "About"
group: navigation
---

{% include JB/setup %}

# __poseidon__ project: open source bioinstrumentation

The poseidon syringe pumps and microscope is a customizable open source alternative to commercial systems that costs less than $500 and can be assembled in an hour. It uses 3D printed parts and common components that can be easily purchased from Amazon or other retailers. The microscope and pumps can be used together in microfluidics experiments, but the pumps can also be connected to a computer and used independently for other experiments.

All source code, 3D model files, bill of materials, and instructions are available at the poseidon GitHub repository: [https://github.com/pachterlab/poseidon](https://github.com/pachterlab/poseidon)

![about](https://user-images.githubusercontent.com/12504176/35100297-31df303c-fc10-11e7-871c-133837e9449c.PNG)

The poseidon system was designed to be customizable. It uses the [Raspberry Pi](https://www.raspberrypi.org/)  and [Arduino](https://www.arduino.cc/) electronics boards, which are supported by a strong ecosystem of open source hardware and software, facilitating the implementation of new functionalities.

The pump driver uses an Arduino with a [CNC shield](https://blog.protoneer.co.nz/arduino-cnc-shield/) to run up to three pumps. Each pump has a stepper motor that drives lead screw which in turn moves a sled that is mounted on linear bearings. The displacement of the sled moves the syringe forward or backward allowing the user to dispel or intake liquid.

The microscope controller station uses Raspberry Pi with a touchscreen to connect to the Arduino and microscope via USB. Because the microscope and Arduino use USB connections, the they can alternatively be connected to any computer instead of a Raspberry Pi. 

![cam_pump_ortho](https://user-images.githubusercontent.com/12504176/44077943-22281bac-9f5a-11e8-8e48-0c1936c4b787.png)

## Hardware and software components developed for the poseidon system 

1. Computer Aided Design (CAD) files for the [pumps](https://a360.co/2B9KUDZ) and [microscope controller station](https://a360.co/2P7rClx)
2. Pump controller software and Graphical User Interface (GUI) to control the Arduino
3. Arduino firmware used to drive the motors

The 3D printed components can be fabricated on any desktop fused filament fabrication (FFF) 3D printer. They were designed using [Autodesk Fusion 360](http://autodesk.com/fusion360), a proprietary CAD software that offers free academic licenses. To modify the 3D models the user can either use Fusion 360 or any other CAD software. 

The GUI was created using [Qt designer](http://doc.qt.io/qt-5/qtdesigner-manual.html), a drag and drop application for organizing buttons that allows the used to easily make modifications. This GUI is used to interface with a Python script that controls both the microscope and Arduino via USB. 

The pumps are driven by an Arduino board that interprets commands sent via USB and sends the proper signal to control the stepper motor movement. The user can take advantage of this by developing custom movement patterns using the Arduino functions.


## Prior work and references

As with everything in life, the Poseidon project was not developed in a vacuum. 

The pumps design was based of the open source syringe pumps published by the [Pearce Research Group](http://www.mse.mtu.edu/~pearce/Index.html):

[Open-Source Syringe Pump Library <br>
Bas Wijnen, Emily J. Hunt, Gerald C. Anzalone, Joshua M. Pearce <br>
PLOS One, 2014. https://doi.org/10.1371/journal.pone.0107216](http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0107216)

With subsequent refinementspublished on [http://www.appropedia.org/Open-source_syringe_pump](http://www.appropedia.org/Open-source_syringe_pump)


The microscope was inspired on a design published by the [Satija Lab](http://satijalab.org/):

[Single-Cell RNA-Seq Of Rheumatoid Arthritis Synovial Tissue Using Low Cost Microfluidic Instrumentation <br>
William Stephenson, Laura T. Donlin, Andrew Butler, Cristina Rozo, Ali Rashidfarrokhi, Susan M. Goodman, Lionel B. Ivashkiv, Vivian P. Bykerk, Dana E. Orange, Robert B. Darnell, Harold P. Swerdlow, Rahul Satija <br>
bioRxiv, 2017](http://www.appropedia.org/Open-source_syringe_pump)

[All necessary files were made avaialble on Metafluidics](https://metafluidics.org/devices/minidrops/)
