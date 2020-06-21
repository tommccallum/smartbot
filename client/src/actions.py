import os
import subprocess


def blocking_play(path):
    """
    Use aplay or mplayer to directly play a sound effect, this will block until
    the sound is played, so don't make it too long
    """
    (rest, ext) = os.path.splitext(path)
    if os.path.isfile(path):
        if ext == "wav":
            subprocess.run("aplay -t wav \"" + path + "\"", shell=True)
        else:
            subprocess.run("mplayer \"" + path + "\"", shell=True)
        return True
    return False


def inline_action(item, default=None):
    """
    Do an inline action, either say a string or play some music
    Uses global app_context to access personality model
    :param personality:
    :param item:
    :param default:     what to do if no item given
    :return:
    """
    global app_context
    if item is None:
        if default is None:
            return False
        else:
            item = default
    if type(item) is str:
        app_context.personality.voice_library.say(item)
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
                    app_context.personality.voice_library.say(item)
                    return True
                else:
                    return False
    return False
