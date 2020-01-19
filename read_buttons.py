#!/usr/bin/python3

from abc import ABC, abstractmethod
import asyncio
from evdev import ecodes, InputDevice, categorize, list_devices
import subprocess
import json
import os
import os.path
import hashlib

#import festival
#print(festival.__file__)

# use evtest to explore /dev/input/event device signals
DEVICE_NAME="D0:8A:55:00:9C:27"
LANGUAGE=None #"en"
VOICE=None #"voice_cmu_us_slt_arctic_clunits"
PERSONALITY="personality.json"

with open(PERSONALITY, "r") as in_file:
    personality=json.load(in_file)
    if "say" not in personality:
        personality["say"] = {}
    VOICE=personality["conf"]["festival"]["voice"]
    LANGUAGE=personality["conf"]["language"]
    print("Setting voice to "+VOICE)
    print("Setting language to "+LANGUAGE)


if not os.path.isfile("mplayer.fifo"):
    subprocess.run("mkfifo mplayer.fifo",shell=True)

def get_file_playlist():
    """Get all m4a files in Radio directory"""
    pass

def get_stream_playlist():
    """Get existing radio playlist"""
    pass

def run_mplayer(playlist):
    """Run mplayer and write pid to file just in case we need to clean up"""
    subprocess.run("mplayer --input-file in --framedrop decoder -vo null "+playlist)

def send_command_to(fifo, command):
    with open(fifo,"w") as out_file:
        out_file.write(command)

class MPlayer:
    def __init__(self):
        self.state = 0
        self.fifo = None

    def pause():
        if self.state == 1:
            send_command_to(self.fifo, "cycle pause")
            self.state = 0
    def play():
        if self.state == 0:
            send_command_to(self.fifo, "cycle pause")
    def next_track():
        pass

    def previous_track():
        pass

def save_personality():
    str = json.dumps(personality, sort_keys=True, indent=4)
    with open(PERSONALITY, "w") as out:
        out.write(str)

def sayText(text):
    global personality
    if text in personality["say"]:
        print("[Personality] using existing saying")
        file_path = personality["say"][text]
    else:
        m = hashlib.sha256()
        m.update(text.encode('utf-8'))
        name = m.hexdigest()+".wav"
        file_path = os.path.abspath("cache/"+name)
        if not os.path.isfile(file_path):
            print("[Personality] creating new saying in personality")
            cmd = "echo \""+text+"\" | text2wave -eval \"(voice_cmu_us_slt_arctic_clunits)\" -o \""+file_path+"\""
            subprocess.run(cmd, shell=True)
            personality["say"][text] = file_path
            save_personality()
    subprocess.run("aplay -t raw -f s16 -c 1 \""+file_path+"\"", shell=True)

    
class BluetoothSpeakerHandler(ABC):
    """Abstract class for the bluetooth speaker"""
    @abstractmethod
    def on_previous_track_down(self):
        pass

    @abstractmethod
    def on_previous_track_up(self):
        pass

    @abstractmethod
    def on_next_track_down(self):
        pass

    @abstractmethod
    def on_next_track_up(self):
        pass

    @abstractmethod
    def on_play_down(self):
        pass

    @abstractmethod
    def on_play_up(self):
        pass

class PrintHandler(BluetoothSpeakerHandler):
    """Simply output the function called by the device"""
    def on_previous_track_down(self):
        print("on_previous_track_down")
    def on_previous_track_up(self):
        print("on_previous_track_up")
    def on_next_track_down(self):
        print("on_next_track_down")
    def on_next_track_up(self):
        print("on_next_track_up")
    def on_play_down(self):
        print("on_play_down")
    def on_play_up(self):
        print("on_play_up")


class EvtDevAgent:
    """Agent for handling bluetooth events"""

    def __init__(self, name, async=True, handler=PrintHandler()):
        self.async = async
        self.handler = handler
        self.name=name
        self.find_device()

    def set_handler(handler):
        self.handler=handler

    def find_device(self):
        if self.name == None:
            self.device = None
            return
        for path in list_devices():
            input_dev= InputDevice(path)
            if input_dev.name == self.name:
                self.device = path

    def list_devices(self):
        devices = [ InputDevice(path) for path in list_devices()]
        for device in devices:
            print(device.path, device.name, device.phys)

    def read_event(self):
        if self.async:
            dev = InputDevice(self.device)
            self._async_read_event(dev)
        else:
            self._sync_read_event(self.device)

    def _sync_read_event(self, device):
        """Synchronous reading of events"""
        device = evdev.InputDevice(device)
        for event in device.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                print(categorize(event))


    def _async_read_event(self, dev):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self._signalHandler(dev))

    async def _signalHandler(self, dev):
        async for ev in dev.async_read_loop():
            #print(repr(ev)+","+ecodes.KEY[ev.code])
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


class HandlerState(BluetoothSpeakerHandler):
    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context) -> None:
        self._context = context

    def on_enter(self):
        """on entering this new state"""
        pass

    def on_exit(self):
        """on transitioning from this state"""
        pass

class EndState(PrintHandler,HandlerState):
    def __init__(self):
        pass

    def on_enter(self):
        self._context.add(Printer("EndState::on_enter"))
        self._context.transition_to_first()

    def on_exit(self):
        self._context.add(Printer("EndState::on_exit"))



class RadioState(HandlerState):
    def __init__(self,next_state: HandlerState) -> None:
        self._next_state = next_state

    def on_enter(self):
        self._context.add(Printer("RadioState::on_enter"))

    def on_exit(self):
        self._context.add(Printer("RadioState::on_exit"))

    def on_previous_track_down(self):
        self.context.add(TextToSpeech("Pausing radio"))

    def on_previous_track_up(self):
        #self.context.add(mplayer_pause())
        self.context.execute()

    def on_next_track_down(self):
        self.context.add(TextToSpeech("Next show"))

    def on_next_track_up(self):
        self.context.execute()

    def on_play_down(self):
        self.context.add(TextToSpeech("Pausing radio"))
        self.context.transition_to(self._next_state)
        self.context.execute()

    def on_play_up(self):
        pass

class Content(ABC):
    def play(self):
        pass

class Printer(ABC):
    def __init__(self, text):
        self.text = text

    def play(self):
        if not self.text:
            print("[WARNING] no text was found in object")
        else:
            print("[Printer] "+self.text)

class TextToSpeech(Content):
    def __init__(self, text):
        self.text = text

    def play(self):
        if self.text:
            sayText(self.text)
            print("[TextToSpeech] "+self.text)

class Context(BluetoothSpeakerHandler):
    """Main interface to client"""


    """Reference to the current state"""
    def __init__(self, state: HandlerState) -> None:
        self.queue = []
        self._state = None
        self._first = state
        self.transition_to(state)

    def transition_to_first(self):
        self.transition_to(self._first)

    def transition_to(self, state: HandlerState):
        if not state:
            state = self._first
        if self._state:
            self._state.on_exit()
        self._state = state
        self._state.context = self
        self._state.on_enter()

    def add(self, output : Content) -> None:
        self.queue.append(output)

    def execute(self) -> None:
        for out in self.queue:
            out.play()
        self.queue = []

    def on_previous_track_down(self):
        self._state.on_previous_track_down()

    def on_previous_track_up(self):
        self._state.on_previous_track_up()

    def on_next_track_down(self):
        self._state.on_next_track_down()

    def on_next_track_up(self):
        self._state.on_next_track_up()

    def on_play_down(self):
        self._state.on_play_down()

    def on_play_up(self):
        self._state.on_play_up()

if __name__ == "__main__":
    e = EndState()
    r = RadioState(e)
    context = Context(r)
    ev = EvtDevAgent(DEVICE_NAME, handler=context)
    ev.read_event()
