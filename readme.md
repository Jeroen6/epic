
# DSCOVR:EPIC Image Viewer

![EPIC](./doc/img/epic_1b_20230219134053.jpg)

This script looks for new [images from the Earth Polychromatic Imaging Camera](https://epic.gsfc.nasa.gov/) on NASA's [Deep Space Climate Observatory](https://www.nesdis.noaa.gov/current-satellite-missions/currently-flying/dscovr-deep-space-climate-observatory) satellite, and displays them on screen.

This is designed for a [2.1" Hyperpixel Round Touch display from Pimoroni](https://shop.pimoroni.com/products/hyperpixel-round), with a [Raspberry Pi Zero W](https://www.raspberrypi.com/products/raspberry-pi-zero-w/).

It displays each image for 20s then moves to the next one.

It currently checks the [EPIC "Blue Marble" API](https://epic.gsfc.nasa.gov/about/api) for new images every 120 mins, but I think they only upload new images once a day, so it probably doesn't need to be this often.

This is programmed using Python3 and PyGame.

## Other features
Some other features have been added:

- The rotation between images is with fade
- Touching the screen jumps to the next image
- Holding the mousebutton or screen >5 seconds exits the application
- It is more api friendly downloading only images is doesn't already have
- It caches images because the api sometimes offers less. guaranteeing a beatiful picture even without internet or api downtime.
- It automatically crops the downloaded image to the right size.  
*Because the DSCOVR is in an [Lissajous orbit](https://en.wikipedia.org/wiki/Lissajous_orbit) around L1 the size of the earth in the photos is variable. Code has been added to use the metadata from the api to calculate how much the crop should be.*

## Raspberry Pi Setup (lazy method)
This procedure works regardless of your host OS.

1. Create a bare Raspberry Pi (Legacy) [Debian Buster][1] image.
	- Make sure to tell the Raspberry pi imager tool to also setup WiFi en SSH.
1. Download and put the `./install/install-all.sh` script on the boot partition the imager just made for you on the SD card.
1. Bring the Raspberry Pi live and login over SSH: `ssh pi@192.168....`
1. Copy the install script to your user directory: `cp /boot/install-all.sh ./`
1. Run it `./install-all.sh`
	- if it complains about rights, `chmod +x ./install-all.sh`
1. Follow on screen instructions and *wait*... It will:
	- setup the USB-Console (the console available on the GPIO ports, over the OTG port)
	- download and install the display drivers.
	- download and install EPIC with python requirements.
	- place two scripts on the desktop you can run via the touchscreen.
	- download and install [comitup][2], a tool to be able to provision new wifi 
	networks using your phones wifi and browser.
		- This last step will hang your SSH session,, because the networking is re-arranged in the rpi, **just wait**, until the unit reboots. It should in a few minutes.
1. Setup the WiFi (again, sorry) via the AP it now makes named `EPIC-###`.
1. Done!

> If installation of comitup fails for some reason, recreate the image and do the installation in two parts, `./install-epic.sh` first over SSH. Then `./install-comitup.sh` but this time while logged in via the USB-Console.

## Raspberry Pi Setup manually
Use these instructions to only setup the EPIC program. Follow the instructions of the display on the page from Pimoroni.

1. Use the terminal or log in as pi via ssh.
1. Create the directory `mkdir ~pi/code/epic/`
1. Go into the directory `cd ~pi/code/epic/`
1. Copy the code from this repository in
	* `git clone https://github.com/Jeroen6/epic.git .` (the dot is intentional)
1. make sure `start-epic.sh` is executable (`chmod +x start-epic.sh`)
1. Copy the autostart file `cp epic.desktop ~pi/.config/autostart/`  
	* The autostart folder may not exist yet `mkdir ~pi/.config/autostart/`
1. Install any python requirements `pip3 install -r requirements.txt`
1. Test you can run it `./start-epic.sh`
	* If that doesn't work, test you can run it directly `python3 -u epic.py`
	* If it still doesn't work check the output for errors, and google them.
1. If the test works, kill it with CTRL+C
1. Reboot and hope it runs automatically `sudo reboot`
1. You may want to put a copy of `start-epic.sh` on the desktop (in the middle) to restart it via the touchscreen if it crashed.

## Updates
If there are, and you want to, update the EPIC python program do the following:

1. Login over USB-Console of SSH.
2. Go to `cd ~/code/epic`
3. Stop the program. `./stop-epic.sh`
4. Update `git pull`
5. Start it `./start-epic.sh &`

To update the raspberry pi os itself (or comitup) run:

	sudo apt update
	sudo apt upgrade

There will be many packages to update, not all are relevant. The installation script does not remove any unused programs.

[1]:https://downloads.raspberrypi.org/raspios_oldstable_armhf/images/
[2]:https://github.com/davesteele/comitup