"""
use evtest to explore /dev/input/event device signals
"""
from evdev import ecodes, InputDevice, categorize, list_devices
from debug_context import DebugContext
from event import Event, EventEnum
import asyncio

from states.announce_state import AnnounceState


class EventDeviceAgent:
    """Agent for handling bluetooth events"""

    def __init__(self, name, async_mode=True, handler=DebugContext()):
        self.async_mode = async_mode
        self.handler = handler
        self.name = name
        self.loop = None
        self.device = None
        self.personality = None
        self.find_device()

    def set_handler(self, handler):
        self.handler = handler

    def find_device(self):
        if self.name == None:
            self.device = None
            print("Device name is none, setting device handle to None")
            return
        for path in list_devices():
            input_dev = InputDevice(path)
            if input_dev.name == self.name:
                self.device = path
                print("Found device " + self.name + " at " + self.device)
        if not self.device:
            # fail here, no point saying anything as speaker has not been found
            raise ValueError("Device " + self.name + " is not found")

    def list_devices(self):
        devices = [InputDevice(path) for path in list_devices()]
        for device in devices:
            print(device.path, device.name, device.phys)

    def read_event(self):
        if self.async_mode:
            if self.device:
                dev = InputDevice(self.device)
                self._async_read_event(dev)
            else:
                raise ValueError("No device name found in configuration.")
        else:
            self._sync_read_event(self.device)

    def _sync_read_event(self, device):
        """Synchronous reading of events"""
        device = InputDevice(device)
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY:
                print(categorize(event))

    def _async_read_event(self, dev):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self._signalHandler(dev))

    def close(self):
        if self.loop:
            self.loop.close()

    async def _signalHandler(self, dev):
        async for ev in dev.async_read_loop():
            # print(repr(ev)+","+ecodes.KEY[ev.code])
            if ev.code != 0:
                if ev.code == 165:
                    if ev.value == 1:
                        self.handler.on_previous_track_down()
                    else:
                        self.handler.on_previous_track_up()
                if ev.code == 163:
                    if ev.value == 1:
                        self.handler.on_next_track_down()
                    else:
                        self.handler.on_next_track_up()
                if ev.code == 200:
                    if ev.value == 1:
                        self.handler.on_play_down()
                    else:
                        self.handler.on_play_up()
