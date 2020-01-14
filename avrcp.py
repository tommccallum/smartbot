#!/usr/bin/python3

import time
import signal
import dbus
import dbus.mainloop.glib
import logging
import traceback

SERVICE_NAME = "org.bluez"
AGENT_IFACE = SERVICE_NAME + '.Agent1'
ADAPTER_IFACE = SERVICE_NAME + ".Adapter1"
DEVICE_IFACE = SERVICE_NAME + ".Device1"
PLAYER_IFACE = SERVICE_NAME + '.MediaPlayer1'
TRANSPORT_IFACE = SERVICE_NAME + '.MediaTransport1'

#LOG_LEVEL = logging.INFO
LOG_LEVEL = logging.DEBUG
LOG_FILE = "/dev/stdout"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"

def getManagedObjects():
    bus = dbus.SystemBus()
    bluez = bus.get_object("org.bluez", "/")
    manager = dbus.Interface(bluez, "org.freedesktop.DBus.ObjectManager")
    return manager.GetManagedObjects()

def findAdapter():
    objects = getManagedObjects();
    bus = dbus.SystemBus()
    for path, ifaces in objects.items():
        adapter = ifaces.get(ADAPTER_IFACE)
        if adapter is None:
            continue
        obj = bus.get_object(SERVICE_NAME, path)
        return dbus.Interface(obj, ADAPTER_IFACE)
    raise Exception("Bluetooth adapter not found")

def print_all_dbus_services():
	for service in dbus.SystemBus().list_names():
		print(service)

#getManagedObjects()
#print(findAdapter())

class AvrcpIntercept(dbus.service.Object):
	AGENT_PATH="/avrcpintercept/agent"
	CAPABILITY="NoInputNoOutput"

	def __init__(self):
		self.bus = None
		self.adapter = None
		self.device = None
		self.device_alias = None
		self.player = None
		self.transport= None
		self.connected = None
		self.status = None
		self.discoverable = None
		self.track = None
		self.mainloop = None

	def start(self):
		# Initiate this class with DBus
		self.bus = dbus.SystemBus()
        dbus.service.Object.__init__(self, dbus.SystemBus(), self.AGENT_PATH)
		# tell dbus we want to handle signals to bluez object
		self.bus.add_signal_receiver(self.playerHandler,
                				        bus_name="org.bluez",
		        		                dbus_interface="org.freedesktop.DBus.Properties",
				                        signal_name="PropertiesChanged",
				                        path_keyword="path")
        self.registerAgent()
		adapter_path = findAdapter().object_path
        self.bus.add_signal_receiver(self.adapterHandler,
                				        bus_name = "org.bluez",
        				                path = adapter_path,
		        		                dbus_interface = "org.freedesktop.DBus.Properties",
				                        signal_name = "PropertiesChanged",
				                        path_keyword = "path")

	def get_device(self,path):
		"""Get a device from a dbus path"""
        self.device = self.bus.get_object("org.bluez", path)
       	self.deviceAlias = self.device.Get(DEVICE_IFACE, "Alias", dbus_interface="org.freedesktop.DBus.Properties")

	def playerHandler(self, interface, changed, invalidated, path ):
		"""Handle relevant property change signals"""
        logging.debug("Interface [{}] changed [{}] on path [{}]".format(interface, changed, path))
       	iface = interface[interface.rfind(".") + 1:]

        if iface == "Device1":
       		if "Connected" in changed:
          		self.connected = changed["Connected"]
       if iface == "MediaControl1":
       		if "Connected" in changed:
           		self.connected = changed["Connected"]
            if changed["Connected"]:
   		        logging.debug("MediaControl is connected [{}] and interface [{}]".format(path, iface))
           	    #self.findPlayer()
            elif iface == "MediaTransport1":
      	        if "State" in changed:
                    logging.debug("State has changed to [{}]".format(changed["State"]))
	                self.state = (changed["State"])
        	    if "Connected" in changed:
                	self.connected = changed["Connected"]
	        elif iface == "MediaPlayer1":
    			if "Track" in changed:
               		logging.debug("Track has changed to [{}]".format(changed["Track"]))
	                self.track = changed["Track"]
        		if "Status" in changed:
               		logging.debug("Status has changed to [{}]".format(changed["Status"]))
	                self.status = (changed["Status"])"""Handle relevant property change signals"""

	def adapterHandler(self, interface, changed, invalidated, path):
	    """Handle relevant property change signals"""
        if "Discoverable" in changed:
            logging.debug("Adapter dicoverable is [{}]".format(self.discoverable))
	        self.discoverable = changed["Discoverable"]
        	        #self.updateDisplay()

	def shutdown(self):
		logging.debug("Shutting down AVRCP intercept bot")

logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)
logging.info("Starting AVRCP intercept bot")

try:
	bot = AvrcpIntercept()
	bot.start()
except KeyboardInterrupt as ex:
	logging.info("Bot cancelled by user")
except Exception as ex:
	logging.error("An error occurred: {}".format(ex))
	traceback.print_exc()
finally:
	bot.shutdown()
