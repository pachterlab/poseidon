---
layout: page
title: "Hardware"
group: navigation
---

{% include JB/setup %}
### Open source syringe pumps and Raspberry Pi microscope
![mvimg_20180111_222424](https://user-images.githubusercontent.com/12504176/34991157-69e99c68-fa7d-11e7-8a77-660660820391.jpg)

### All the parts for 3 pumps and a microscope [cost under $400](https://docs.google.com/spreadsheets/d/e/2PACX-1vSY0apQMOMEC040cuPamMla8yvhqwZEs39H3IEm0rRVuf6EW1HUUKMYhD6gZyLmJnDAxj-zRwVM9L6G/pubhtml)
![mvimg_20180111_211022](https://user-images.githubusercontent.com/12504176/34991323-0a6b41aa-fa7e-11e7-8e57-fbb78b54cc67.jpg)

### Assembly instructions for the Poseidon syringe pumps

Detailed written instructions are on the way, in the meantime you can [click here for a walkthrough video](https://photos.app.goo.gl/xIplnxrbvsixwfU03)

### Instructions for the pumps Arduino hardware

We use the [Arduino CNC shield](http://wiki.keyestudio.com/index.php/Ks0095_Arduino_CNC_Kit_/_CNC_Shield_V3.0_%2Bkeyestudio_Uno_R3%2B4pcs_a4988_Driver_/_GRBL_Compatible)
to allow for up to three pumps can be controlled from a computer or from the Rapsberry Pi microscope.

The software is configured to run the stepper motors with 200 steps per revolution at 1/4 microstepping, which translates to 800 steps per rotation. To configure this, it is necessary to add a jumper between the MODE1 pins of the Arduino CNC shield, as shown in the picture below. More information about microstepping can be found in the product page for the [DRV8825 Stepper Motor Driver](https://www.pololu.com/product/2133), which is used by the CNC shield. 

![microsteppingpng](https://user-images.githubusercontent.com/12504176/34992088-d2e04ca0-fa80-11e7-9dde-99b1894fbe5c.PNG)

Here is how the board looks with the stepper motors connected:

![full_board](https://user-images.githubusercontent.com/12504176/35099661-b8e55262-fc0d-11e7-86df-f2927111ce1a.PNG)


### Assembly of the Raspberry Pi and screen 
<iframe width="560" height="315" src="https://www.youtube.com/embed/g3pXNY8snOg" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
 

#### License

poseidon is distributed under the GPL v3.0 License.
