# pySMSd

Python script to receive and send SMS automatically.
-----------

- Python 2.7
- usb_modeswitch (Switch USB Modem from storage to modem. Install: "sudo apt-get install usb-modeswitch")
- Tested with Ubuntu 16.10 and rasberry pi B+ with raspbian
- Check if usb_modeswitch worked ok: lsusb must return the device with "(modem on)" at description
- Edit "funcCMD.py" to process the responses for received commands.
- Run it: "sudo python2.7 pySMSd.py"


![alt tag](https://raw.githubusercontent.com/arturgontijo/pySMSd/master/screeshots/screenshot_01.png)
