#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
echo ""
echo "This script changes to AIA mode"
echo "It will do the following:"
echo "- Change git branch"
echo "- Install depencencies"
echo ""
read -p "Do you want to continue? (y/n)" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Nn]$ ]]
then
    exit 0
fi


# Install EPIC
# https://github.com/Jeroen6/epic
echo ""
echo "Installing AIA..."
cd /home/pi/code/epic
./stop-epic.sh
git checkout -b AIA origin/AIA
echo "Installing dependencies..."
sudo apt install python3-opencv
pip3 install -r requirements.txt

echo ""
echo "All finished, rebooting."
./start-epic.sh