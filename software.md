---
layout: page
title: "Software"
group: navigation
---

{% include JB/setup %}
## Source Code

Source code is available at [https://github.com/pachterlab/poseidon](https://github.com/pachterlab/poseidon)


## Binaries
The pump control software GUI has binaries available for Windows, Linux, MacOS and Raspbian

[Download Linux Binary 42MB](https://github.com/pachterlab/poseidon/raw/master/software/binaries/pump_interface_linux_v0.025)

[Download Windows Binary 17MB](https://github.com/pachterlab/poseidon/raw/master/software/binaries/pump_interface_windows_v0.025.exe)

[Download Raspbian Binary 37MB](https://github.com/pachterlab/poseidon/raw/master/software/binaries/pump_interface_raspi_v0.025)

[Download MacOS Binary 42MB](www.replacethislink.com)


## Arudino Firmware
To communicate with the Arduino and control the CNC shield stepper motor drivers, we must first flash the Arduino with [Configurable Firmata](https://www.github.com/firmata/ConfigurableFirmata).

We have had success following their instructions for installing the ConfigurableFirmata library and using their [example sketch](https://www.github.com/firmata/ConfigurableFirmata/examples/ConfigurableFirmata/Configurablefirmata.ino) for our Arduinos.


#### License

poseidon is distributed under the GPL v3.0 License.
