#!/usr/bin/env bash

REPO_NAME='BlueStick'
RULE_NAME='bluestick_device.rules'

echo "Instaling BlueStick Software..."

GADGET_TYPE=$1

if [ -z $GADGET_TYPE ]; then
    GADGET_NAME='XAC_Gamepad'
    USB_GADGET_NAME='xac_gamepad_usb'
    SERVICE_NAME='xac_gamepad.service'
elif [ $GADGET_TYPE = "8b" ]; then
    GADGET_NAME='8_Buttons_Gamepad'
    USB_GADGET_NAME='8_buttons_gamepad_usb'
    SERVICE_NAME='8_buttons_gamepad.service'
elif [ $GADGET_TYPE = "16b" ]; then
    GADGET_NAME='16_Buttons_Gamepad'
    USB_GADGET_NAME='16_buttons_gamepad_usb'
    SERVICE_NAME='16_buttons_gamepad.service'
elif [ $GADGET_TYPE = "32b" ]; then
    GADGET_NAME='32_Buttons_Gamepad'
    USB_GADGET_NAME='32_buttons_gamepad_usb'
    SERVICE_NAME='32_buttons_gamepad.service'
elif [ $GADGET_TYPE = "ns" ]; then
    GADGET_NAME='NS_Gamepad'
    USB_GADGET_NAME='ns_gamepad_usb'
    SERVICE_NAME='ns_gamepad.service'
elif [ $GADGET_TYPE = "ps" ]; then
    GADGET_NAME='PS_Gamepad'
    USB_GADGET_NAME='ps_gamepad_usb'
    SERVICE_NAME='ps_gamepad.service'
elif [ $GADGET_TYPE = "xac" ]; then
    GADGET_NAME='XAC_Gamepad'
    USB_GADGET_NAME='xac_gamepad_usb'
    SERVICE_NAME='xac_gamepad.service'
else
    GADGET_NAME='XAC_Gamepad'
    USB_GADGET_NAME='xac_gamepad_usb'
    SERVICE_NAME='xac_gamepad.service'
fi
echo "Instaling $GADGET_NAME ..."

#Step 1: Get current kernel version 
KERNEL_VERSION=$(uname -r | egrep -o '^[^-+]+')
echo "Step 1: Kernel version is currently set to ${KERNEL_VERSION}"


#Step 2: Install and update dependencies
sudo apt update
sudo apt install -y python3-pip python3-gpiozero python3-evdev git
sudo python3 -m pip install pyyaml
echo "Step 2: Dependencies successfully installed"


#Step 3: Clone code from github
cd /usr/local/etc
[ ! -d ${REPO_NAME} ] && git clone https://github.com/milador/BlueStick
cd ${REPO_NAME}/resource
echo "Step 3: Repository was cloned"

#Step 4: Load the USB gadget drivers
grep --quiet "^dtoverlay=dwc2$" /boot/config.txt
if [ $? -eq 1 ]; then
    echo "dtoverlay=dwc2" | sudo tee -a /boot/config.txt
fi
grep --quiet "^dwc2$" /etc/modules
if [ $? -eq 1 ]
then
    echo "dwc2" | sudo tee -a /etc/modules
fi
grep --quiet "^libcomposite$" /etc/modules
if [ $? -eq 1 ]
then
    echo "libcomposite" | sudo tee -a /etc/modules
fi
echo "Step 4: Successfully loaded the USB gadget drivers."

#Step 5: Install USB gamepad gadget and load it on boot
cd gadget
sudo cp ${USB_GADGET_NAME} /usr/bin/
sudo chmod +x /usr/bin/${USB_GADGET_NAME}
# Insert line in /etc/rc.local, if needed
sudo sed -i '/\/usr\/bin\//d' /etc/rc.local
sudo sed -i '/^exit 0/i \/usr/bin/'${USB_GADGET_NAME} /etc/rc.local
echo "Step 5: Successfully installed USB gamepad gadget descriptor."
cd ..

#Step 6: Install bluestick_device rule to give permission and allow hidg0 access
cd rules
sudo cp ${RULE_NAME} /etc/udev/rules.d/
echo "Step 6: Successfully added bluestick_device rule."
cd ..

#Step 7: Install gamepad service and start it
IS_ACTIVE=$(sudo systemctl is-active $SERVICE_NAME)
if [ $GADGET_NAME = "8_Buttons_Gamepad" ]; then
    sudo systemctl stop '16_buttons_gamepad.service' '32_buttons_gamepad.service' 'ns_gamepad.service' 'ps_gamepad.service' 'xac_gamepad.service'
	sudo systemctl disable '16_buttons_gamepad.service' '32_buttons_gamepad.service' 'ns_gamepad.service' 'ps_gamepad.service' 'xac_gamepad.service'
elif [ $GADGET_NAME = "16_Buttons_Gamepad" ]; then
    sudo systemctl stop '8_buttons_gamepad.service' '32_buttons_gamepad.service' 'ns_gamepad.service' 'ps_gamepad.service' 'xac_gamepad.service'
	sudo systemctl disable '8_buttons_gamepad.service' '32_buttons_gamepad.service' 'ns_gamepad.service' 'ps_gamepad.service' 'xac_gamepad.service'
elif [ $GADGET_NAME = "32_Buttons_Gamepad" ]; then
    sudo systemctl stop '8_buttons_gamepad.service' '16_buttons_gamepad.service' 'ns_gamepad.service' 'ps_gamepad.service' 'xac_gamepad.service'
	sudo systemctl disable '8_buttons_gamepad.service' '16_buttons_gamepad.service' 'ns_gamepad.service' 'ps_gamepad.service' 'xac_gamepad.service'
elif [ $GADGET_NAME = "NS_Gamepad" ]; then
    sudo systemctl stop '8_buttons_gamepad.service' '16_buttons_gamepad.service' '32_buttons_gamepad.service' 'xac_gamepad.service' 'ps_gamepad.service'
	sudo systemctl disable '8_buttons_gamepad.service' '16_buttons_gamepad.service' '32_buttons_gamepad.service' 'xac_gamepad.service' 'ps_gamepad.service'
elif [ $GADGET_NAME = "PS_Gamepad" ]; then
    sudo systemctl stop '8_buttons_gamepad.service' '16_buttons_gamepad.service' '32_buttons_gamepad.service' 'xac_gamepad.service' 'ns_gamepad.service'
	sudo systemctl disable '8_buttons_gamepad.service' '16_buttons_gamepad.service' '32_buttons_gamepad.service' 'xac_gamepad.service' 'ns_gamepad.service'
elif [ $GADGET_NAME = "XAC_Gamepad" ]; then
    sudo systemctl stop '8_buttons_gamepad.service' '16_buttons_gamepad.service' '32_buttons_gamepad.service' 'ns_gamepad.service' 'ps_gamepad.service'
	sudo systemctl disable '8_buttons_gamepad.service' '16_buttons_gamepad.service' '32_buttons_gamepad.service' 'ns_gamepad.service' 'ps_gamepad.service'
else
    sudo systemctl stop '8_buttons_gamepad.service' '16_buttons_gamepad.service' '32_buttons_gamepad.service' 'ns_gamepad.service' 'ps_gamepad.service'
	sudo systemctl disable '8_buttons_gamepad.service' '16_buttons_gamepad.service' '32_buttons_gamepad.service' 'ns_gamepad.service' 'ps_gamepad.service'
fi
sudo systemctl daemon-reload 
sudo systemctl reset-failed
if [ "$IS_ACTIVE" = "active" ]; then
    # restart the service
    echo "Service is running"
    echo "Restarting service"
    sudo systemctl restart $SERVICE_NAME
    echo "Step 7: Service successfully restarted"
else
    # create service file
    echo "Creating service file"
	cd service
    sudo chmod +x ${SERVICE_NAME}
    sudo cp ${SERVICE_NAME} /etc/systemd/system/
    #Restart daemon, enable and start service
    echo "Reloading daemon and enabling service"
    sudo systemctl daemon-reload 
    sudo systemctl enable ${SERVICE_NAME} # remove the extension
    sudo systemctl start ${SERVICE_NAME}
    echo "Step 7: Service successfully started"
	cd ..
fi

#Step 8: Add auto connect repair service
cd service
sudo chmod +x connection_repair.service
sudo cp connection_repair.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable connection_repair.service
systemctl start connection_repair.service
echo "Step 8: Successfully added auto connect repair service."
cd ..

#Step 9: Rebooting RaspberryPi
echo "Step 9: Rebooting RaspberryPi."
echo "BlueStick software successfully installed..."
sleep 3
sudo reboot
