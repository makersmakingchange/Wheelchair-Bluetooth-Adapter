#!/usr/bin/env bash

echo "Uninstaling BlueStick Software..."


#Step 1: Load the USB gadget drivers
sudo sed -i '/dtoverlay=dwc2/d' /boot/config.txt
sudo sed -i '/dwc2/d' /etc/modules
sudo sed -i '/libcomposite/d' /etc/modules
echo "Step 1: Successfully unloaded the USB gadget drivers."

#Step 2: Uninstall USB gamepad gadget and remove it from boot
cd /usr/bin/
sudo rm -r 8_buttons_gamepad_usb 16_buttons_gamepad_usb 32_buttons_gamepad_usb ns_gamepad_usb ps_gamepad_usb xac_gamepad_usb
sudo sed -i '/\/usr\/bin\//d' /etc/rc.local
echo "Step 2: Successfully iunnstalled USB gamepad gadget descriptor."

#Step 3: Install bluestick_device rule to give permission and allow hidg0 access
sudo rm -r /etc/udev/rules.d/bluestick_device.rules
echo "Step 3: Successfully removed bluestick_device rule."

#Step 4: Install gamepad service and start it
sudo systemctl stop 'connection_repair.service' '8_buttons_gamepad.service' '16_buttons_gamepad.service' '32_buttons_gamepad.service' 'ns_gamepad.service' 'ps_gamepad.service' 'xac_gamepad.service'
sudo systemctl disable 'connection_repair.service' '8_buttons_gamepad.service' '16_buttons_gamepad.service' '32_buttons_gamepad.service' 'ns_gamepad.service' 'ps_gamepad.service' 'xac_gamepad.service'
cd /etc/systemd/system/
sudo rm -r connection_repair.service 8_buttons_gamepad.service 16_buttons_gamepad.service 32_buttons_gamepad.service ns_gamepad.service ps_gamepad.service xac_gamepad.service
sudo systemctl daemon-reload 
sudo systemctl reset-failed
echo "Step 4: Service successfully removed"

#Step 5: Rebooting RaspberryPi
echo "Step 5: Rebooting RaspberryPi."
echo "BlueStick software successfully uninstalled..."
sleep 3
sudo reboot
