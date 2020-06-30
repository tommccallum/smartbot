import datetime
import os
import random
import subprocess
import globalvars


def expand_path(path):
    config = globalvars.app_context.config
    if config.HOME_DIRECTORY is not None:
        path = path.replace("%HOME%", config.HOME_DIRECTORY)
    if config.config_path is not None:
        path = path.replace("%CONFIG%", config.config_path)
    if config.SMARTBOT_HOME is not None:
        path = path.replace("%SMARTBOT%", config.SMARTBOT_HOME)
    return path

def blocking_play(path):
    """
    Use aplay or mplayer to directly play a sound effect, this will block until
    the sound is played, so don't make it too long
    """
    path = expand_path(path)
    (rest, ext) = os.path.splitext(path)
    if os.path.isfile(path):
        if ext == ".wav":
            subprocess.run("aplay -t wav \"" + path + "\"", shell=True)
        else:
            subprocess.run("mplayer \"" + path + "\"", shell=True)
        return True
    return False

def replace_tags(text):
    text = text.replace( "%O", globalvars.app_context.config.json["owner"] )
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
        globalvars.app_context.personality.voice_library.say(item)
        return True
    elif type(item) is dict:
        if "type" in item:
            if item["type"].lower() == "sound":
                if "path" in item:
                    blocking_play(item["path"])
                    return True
                else:
                    return False
            if item["type"].lower() == "speech":
                if "text" in item:
                    to_say = replace_tags(item["text"])
                    globalvars.app_context.personality.voice_library.say(to_say)
                    return True
                else:
                    return False
    return False
