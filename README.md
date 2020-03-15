# HubitatWizLightDriverX v1.01x
Hubitat Elevation device handler for Philips Wiz wi-fi color lights

## What can I do with this driver?
This driver lets the Hubitat control Wiz color bulbs.  It will probably
mostly work with Wiz on/off and variable CT white bulbs as well, but I only own
the color bulbs at this point and I haven't tested the others yet.

## EXPERIMENTAL VERSION NOTES
Given a Wiz bulb's MAC address, this version can determine and set its
IP address in the device handler dynamically. To make it work, you must run the included python 
utility (mac2iplookup.py) on an always-on machine that can see all your bulbs.

#### Caution: Experimental!
I highly recommend that you use the normal version of this device handler unless
you are comfortable with networking and linux, and have a network configuration 
that makes dynamic ip resolution useful -- this is intended for large networks,
with many devices.  For many people it is easier to just use the
DHCP server on your router to assign static ip addresses to your lights and
other IoT devices.

## To Install and Use the Driver
Install and provision your Wiz bulb using the phone app.  Note the bulb's IP address.

On your Hubitat Elevation's admin page, select "Drivers Code", then click the
"New Driver" button.  Paste the Groovy driver code from this repository into 
the editor window and click the "SAVE" button.

Create a new virtual device on your Hubitat, name and label it, and select 
"Wiz Color Light Experimental" as the device type.  Save your new device.

Click the new device on the Hubitat's "Devices" page, and enter your light's
IP address in the provided field.

If you're using the dynamic resolution scheme, enter your bulb's 
MAC address (available from the Wiz app) and the address (ip:port) of the machine
on which WizMacMapper.py is running.  Then enable the Mac lookup service in
preferences and save your preferences.  That's it. You can now send commands to your Wiz light
via the LAN.   

## mac2iplookup.py 
### What does it do?
mac2iplookup.py is a small(ish) python program that 
- enumerates Wiz bulbs (and in the future, maybe other wifi devices) on your LAN
- exposes http endpoints which an application can query with http GET and recieve a
json response.

The endpoints are:
- /resolve?mac=xxxxxxxxxxxx - 
Used by device handler to get the current ip address of the specified device. Returns a json packet containing the ip address corresponding to the specified mac. Note
that mac addresses can be upper and/or lower case, but should not include colons.  If
the address is not found, the "result" parameter in the return packet will be false, and
the "ip" parameter will contain a brief error message.
    Sample result for successful lookup: ```{"ip":"192.168.1.28","result":true}```

- /refresh -
For manual use, or use by other utilities. Refresh the list of known devices immediately. Useful
- /list -
For manual use, or use by other utilities. Return a json map/dictionary of {mac:ip address} pairs for all the known devices
- /stop -
For manual use, or use by other utilities. Stops all net services and exits the script


### Requirements
- A computer running ubuntu, debian, raspbian, etc. I have tested on Ubuntu 18.04lts, Debian 10, 
Raspbian 4.19 and Windows 10
- Python3 v3.7 or newer.  (I've tested with various 3.7.x versions)
- The twisted framework (www.twistedmatrix.com for info) Twisted greatly simplifies writing
multi-protocol network code. You can install it with the command: ```pip3 install twisted```

### Installation
Once you've got python3 and twisted, copy mac2iplookup.py to whatever directory you
like.  It does not require any special privileges, and definitely need not be run as
root.

### Configuration
The web service is configured to use port 8000 and to refresh the mac/ip address list
at one hour intervals. If you want to change these defaults, use a text editor
to edit the constants HTTP_PORT and POLLING_INTERVAL in the .py file.

### Starting and Stopping
To start the service, ```python3 mac2iplookup.py``` or ```nohup python3 mac2iplookup.py &```
(on linux) to run in the background.

To stop the service, access the /stop http endpoint with your browser or other program.
 
(I'm keeping this super simple for the experimental release.  If enough people are
interested,  I'll make it easy to setup as a linux service.) 


## Credit where credit is due
I got protocol and hardware information, and inspiration from the following:

http://blog.dammitly.net/2019/10/cheap-hackable-wifi-light-bulbs-or-iot.html

https://limitedresults.com/2019/02/pwn-the-wiz-connected/

The OpenHab team, particularly...
https://github.com/SRGDamia1/openhab2-addons/tree/master/bundles/org.openhab.binding.wizlighting/src/main/java/org/openhab/binding/wizlighting

https://www.wireshark.org/

And of course, the Hubitat dev community! I read through a ton of everyone's source looking for and
usually finding solutions to LAN device questions.  Especially useful were...
https://github.com/robheyes/lifxcode

https://github.com/muxa/hubitat/blob/master/drivers/wled-light.groovy

https://github.com/markus-li/Hubitat/tree/master/drivers


