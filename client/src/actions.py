import datetime
import logging
import os
import random
import subprocess
import globalvars


def expand_path(path):
    config = globalvars.app_state.settings
    if config.HOME_DIRECTORY is not None:
        path = path.replace("%HOME%", config.HOME_DIRECTORY)
    if config.config_path is not None:
        path = path.replace("%CONFIG%", config.config_path)
    if config.SMARTBOT_HOME is not None:
        path = path.replace("%SMARTBOT%", config.SMARTBOT_HOME)
    return path

def blocking_play(path, timeout=10):
    """
    Use aplay or mplayer to directly play a sound effect, this will block until
    the sound is played, if using non-wave files then we have a timeout settings
    to stop whole sound files form being played.  Large music files should use the
    audio_player instance under the context object.
    """
    path = expand_path(path)
    (rest, ext) = os.path.splitext(path)
    if os.path.isfile(path):
        if ext == ".wav":
            subprocess.run("aplay -t wav \"" + path + "\"", shell=True)
        else:
            # this is a separate process which is not interruptable
            # only to be used on very SHORT files otherwise it will clog
            # everything up
            # we purposefully kill after 10 seconds so it does not block
            subprocess.run("timeout {} mplayer -noautosub -novideo -really-quiet -noconsolecontrols \"{}\"".format(timeout,path), shell=True)
        return True
    return False

def replace_tags(text):
    if globalvars.app_state:
        if globalvars.app_state.settings:
            if "owner" in globalvars.app_state.settings.json:
                text = text.replace( "%O", globalvars.app_state.settings.json["owner"] )
    return text

def time_based_greeting():
    when = datetime.datetime.now()
    if when.hour >= 21:
        greeting = "Evening"
    elif when.hour >= 18:
        greeting = "Evening"
    elif when.hour >= 12 and when.hour < 16:
        greeting = "Afternoon"
    elif when.hour >= 16 and when.hour < 18:
        greeting = "Hello"
    elif when.hour < 2:
        greeting = "Hello"
    elif when.hour < 6:
        greeting = "Morning"
    else:
        # after 6 and before 12
        greeting = "Morning"
    if type(greeting) is list:
        greeting = random.choice(greeting)
    return greeting


def inline_action(item, default=None):
    """
    Do an inline action, either say a string or play some music
    Uses global app_context to access personality model
    :param personality:
    :param item:
    :param default:     what to do if no item given
    :return:
    """
    if item is None:
        if default is None:
            return False
        else:
            item = default
    if type(item) is str:
        item = replace_tags(item)
        globalvars.app_state.voice_library.say(item)
        return True
    elif type(item) is dict:
        if "type" in item:
            if item["type"].lower() == "sound":
                if "path" in item:
                    blocking_play(item["path"])
                    return True
                else:
                    logging.warning("no 'path' key found in dict {}".format(item))
                    return False
            if item["type"].lower() == "speech":
                if "text" in item:
                    to_say = replace_tags(item["text"])
                    globalvars.app_state.voice_library.say(to_say)
                    return True
                else:
                    return False
    return False
