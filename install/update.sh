#!/usr/bin/env bash

echo "Updating BlueStick Software..."
cd /usr/local/etc
cd BlueStick
git fetch https://github.com/milador/BlueStick
echo "BlueStick software successfully updated..."
sleep 3
sudo reboot
