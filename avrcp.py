#!/usr/bin/python3

import sys
import time
import signal
import dbus
import dbus.service
import dbus.mainloop.glib
import logging
import traceback
from gi.repository import GObject as gobject

SERVICE_NAME = "org.bluez"
AGENT_IFACE = SERVICE_NAME + '.Agent1'
ADAPTER_IFACE = SERVICE_NAME + ".Adapter1"
DEVICE_IFACE = SERVICE_NAME + ".Device1"
PLAYER_IFACE = SERVICE_NAME + '.MediaPlayer1'
TRANSPORT_IFACE = SERVICE_NAME + '.MediaTransport1'

#LOG_LEVEL = logging.INFO
LOG_LEVEL = logging.DEBUG
LOG_FILE = sys.stdout #"avrcp.log" #"/dev/stdout"
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
        gobject.threads_init()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        dbus.service.Object.__init__(self, dbus.SystemBus(), self.AGENT_PATH)
        # tell dbus we want to handle signals to bluez object
#        self.bus.add_signal_receiver(self.playerHandler,
 #                                       bus_name="org.bluez",
  #                                      dbus_interface="org.freedesktop.DBus.Properties",
   #                                     signal_name="PropertiesChanged",
    #                                    path_keyword="path")

        self.bus.add_signal_receiver(self.handleEverything)

        self.registerAgent()
        adapter_path = findAdapter().object_path
        self.bus.add_signal_receiver(self.adapterHandler,
                                        bus_name = "org.bluez",
                                        path = adapter_path,
                                        dbus_interface = "org.freedesktop.DBus.Properties",
                                        signal_name = "PropertiesChanged",
                                        path_keyword = "path")
        self.findPlayer()

        self.mainloop = gobject.MainLoop()
        self.mainloop.run()


    def handleEverything(self, *args, **kwargs):
        print(args)
        print(kwargs)

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
                self.findPlayer()
        elif iface == "MediaTransport1":
            if "State" in changed:
                logging.debug("State has changed to [{}]".format(changed["State"]))	                
                self.state = changed["State"]
            if "Connected" in changed:
                self.connected = changed["Connected"]
        elif iface == "MediaPlayer1":
            if "Track" in changed:
                logging.debug("Track has changed to [{}]".format(changed["Track"]))
                self.track = changed["Track"]
            if "Status" in changed:
                logging.debug("Status has changed to [{}]".format(changed["Status"]))
                self.status = (changed["Status"])
                """Handle relevant property change signals"""

    def adapterHandler(self, interface, changed, invalidated, path):
        """Handle relevant property change signals"""
        if "Discoverable" in changed:
            logging.debug("Adapter dicoverable is [{}]".format(self.discoverable))
            self.discoverable = changed["Discoverable"]
            #self.updateDisplay()

    def shutdown(self):
        logging.debug("Shutting down AVRCP intercept bot")

    def registerAgent(self):
        """Register BluePlayer as the default agent"""
        manager = dbus.Interface(self.bus.get_object(SERVICE_NAME, "/org/bluez"), "org.bluez.AgentManager1")
        manager.RegisterAgent(AvrcpIntercept.AGENT_PATH, AvrcpIntercept.CAPABILITY)
        manager.RequestDefaultAgent(AvrcpIntercept.AGENT_PATH)
        logging.debug("AVCRP is registered as a default agent")

    def findPlayer(self):
        """Find any current media players and associated device"""
        manager = dbus.Interface(self.bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()

        player_path = None
        transport_path = None
        for path, interfaces in objects.items():
            if PLAYER_IFACE in interfaces:
                player_path = path
            if TRANSPORT_IFACE in interfaces:
                transport_path = path

        if player_path:
            logging.debug("Found player on path [{}]".format(player_path))
            self.connected = True
            self.getPlayer(player_path)
            player_properties = self.player.GetAll(PLAYER_IFACE, dbus_interface="org.freedesktop.DBus.Properties")
            if "Status" in player_properties:
                self.status = player_properties["Status"]
            if "Track" in player_properties:
                self.track = player_properties["Track"]
        else:
            logging.debug("Could not find player")

        if transport_path:
            logging.debug("Found transport on path [{}]".format(player_path))
            self.transport = self.bus.get_object("org.bluez", transport_path)
            logging.debug("Transport [{}] has been set".format(transport_path))
            transport_properties = self.transport.GetAll(TRANSPORT_IFACE, dbus_interface="org.freedesktop.DBus.Properties")
            if "State" in transport_properties:
                self.state = transport_properties["State"]


#logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)
root_logger = logging.getLogger()
root_logger.setLevel(LOG_LEVEL)
handler = logging.StreamHandler(sys.stdout) 
handler.setLevel(LOG_LEVEL)
formatter = logging.Formatter(LOG_FORMAT)
handler.setFormatter(formatter)
root_logger.addHandler(handler)

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
