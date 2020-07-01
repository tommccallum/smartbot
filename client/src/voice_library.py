import logging
import os
import hashlib
import subprocess
import datetime
import json
import re
import time


class VoiceLibrary:
    """Stores the voice wav files

        Phrases database has stuff like "You are now listening to %T", and "Hi, my name is %N"
        Speech has the actual text without any %tags in.

    """

    def __init__(self, personality: "Personality"):
        self.personality = personality
        self.phrases_filename = "phrases.json"
        self.speech_filename = "speech.json"
        self.phrases_full_path = personality.config.find(self.phrases_filename)
        self.phrases = []
        self.speech = {}
        self._load()

    def _load(self):
        if os.path.isfile(self.phrases_full_path):
            with open(self.phrases_full_path, "r") as in_file:
                self.phrases = json.load(in_file)

        self.speech_full_path = self.personality.config.find(self.speech_filename)
        if os.path.isfile(self.speech_full_path):
            with open(self.speech_full_path, "r") as in_file:
                self.speech = json.load(in_file)

    def reload(self):
        self._load(self)

    def say(self, text, related_to_file=None, save=True):
        """
        Say some piece of speech
        :param text: the message to say
        :param related_to_file: the file such as a radio track to keep track of, so when it gets removed the speech gets removed
        :return:
        """
        saying = None
        if self._has_saying(text):
            # this does not mean the file actually exists so we still need to
            # have a _make_saying - just in case !
            saying = self._get_saying(text)
        if saying is None or not os.path.isfile(saying["file_path"]):
            saying = self._make_saying(text,related_to_file,save)
        return self._play_speech(saying, save)

    def _play_speech(self, saying, save=True):
        """
        Play a wave file using aplay utility
        :param saying:  the saying dict object from make_saying
        """
        logging.debug("attempting to say message {}, file exists {}".format(saying, os.path.isfile(saying['file_path'])))
        process = None
        if saying is not None and os.path.isfile(saying['file_path']):
            logging.debug("running aplay on {}".format(saying['file_path']))
            # this call only returns when completed
            subprocess.run("aplay -t wav \"" + saying['file_path'] + "\"", shell=True)
            if not save:
                os.remove(saying['file_path'])


    def update(self):
        """Update the voice library by:
                for each phrase, check it is generated and if not, then go ahead and make it
                for each existing speech item, check it still exists and remove if its not needed anymore
        """
        tags = self._get_default_tags()
        print(tags)
        for phrase in self.phrases:
            logging.debug(phrase)
            if "%T" in phrase:
                self._make_saying_for_each_track(phrase, tags)
            else:
                text_list = self._process_phrase(phrase, tags)
                for text_item in text_list:
                    self._make_saying(text_item)
        keys_to_delete = []
        for key in self.speech:
            if "keep_while_exists" in self.speech[key]:
                if not self.speech[key]["keep_while_exists"] is None:
                    if not os.path.isfile(self.speech[key]["keep_while_exists"]):
                        os.remove(self.speech[key]["file_path"])
                        keys_to_delete.append(key)
        for key in keys_to_delete:
            del self.speech[key]
        self._save_files()

    def convert_seconds_to_saying(self, seek_value):
        hour_string = ""
        min_string = ""
        second_string = ""
        conjunction1 = ""
        conjunction2 = ""
        hours = 0
        mins = 0
        seconds = 0

        # convert everything into whole hours, minutes and seconds
        seconds = int(seek_value)
        if seconds >= 60:
            mins = int(seek_value / 60)
            seconds = int(seek_value - (mins * 60))
            if mins >= 60:
                hours = int(mins / 60)
                mins = int(mins - (hours * 60))

        if hours > 0:
            if hours == 1:
                hour_string = "{} hour".format(hours)
            else:
                hour_string = "{} hours".format(hours)
        if mins > 0:
            if mins == 1:
                min_string = "{} minute".format(mins)
            else:
                min_string = "{} minutes".format(mins)
        if seconds > 0:
            if seconds == 1:
                second_string = "{} second".format(seconds)
            else:
                second_string = "{} seconds".format(seconds)

        if hours > 0 and mins > 0 and seconds > 0:
            conjunction1 = ""
            conjunction2 = "and"
        if hours > 0 and mins == 0 and seconds > 0:
            conjunction1 = "and"
            conjunction2 = ""
        if hours > 0 and mins > 0 and seconds == 0:
            conjunction1 = "and"
            conjunction2 = ""
        if hours == 0 and mins > 0 and seconds > 0:
            conjunction1 = ""
            conjunction2 = "and"

        return "{} {} {} {} {}".format(hour_string, conjunction1, min_string, conjunction2, second_string).strip(" ").replace("  ", " ").replace("  ", " ")

    def _has_saying(self, text):
        """Check if the phrase 'text' has already been generated"""
        item = self._get_key(text)
        return item in self.speech

    def _get_saying(self, text):
        """Get the speech item for text, returns None if it does not exist"""
        item = self._get_key(text)
        try:
            return self.speech[item]
        except:
            return None

    def _get_all_owners_from_devices(self):
        devices_file_path = self.personality.config.get_devices_path()
        logging.debug(devices_file_path)
        owners = []
        if devices_file_path is not None:
            if os.path.isfile(devices_file_path):
                with open(devices_file_path, "r") as in_file:
                    devices_data = json.load(in_file)
                    for device_key in devices_data:
                        if "owner" in devices_data[device_key]:
                            owners.append(devices_data[device_key]["owner"])
                owners = list(set(owners))
        return owners

    def _get_default_tags(self):
        tags = {}
        tags["name"] = self.personality.get_name()
        tags["owners"] = self._get_all_owners_from_devices()
        return tags

    @staticmethod
    def _process_phrase_2(text, tag, replacements):
        """Replaces tag in all text strings
            @return [] if tag is not text
        """
        if not tag in text:
            return []
        # standardize text and replacements as lists
        # as they could be strings
        if not type(text) is list:
            text = [ text ]
        if not type(replacements) is list:
            replacements = [replacements]
        new_text_list = []
        for txt_string in text:
            for value in replacements:
                new_text_list.append(txt_string.replace(tag, value))
        return new_text_list

    @staticmethod
    def _process_phrase(text, replacements):
        """replacements is a dictionary of values to replace
            returns a LIST of strings, as the tags can expand to more than 1 item
        """
        phrase_strings = []
        if "name" in replacements:
            tag = "%N"
            replacement_values = replacements["name"]
            phrase_strings += VoiceLibrary._process_phrase_2(text, tag, replacement_values)
        if "track" in replacements:
            tag = "%T"
            replacement_values = replacements["track"]
            phrase_strings += VoiceLibrary._process_phrase_2(text, tag, replacement_values)
        if "owners" in replacements:
            tag = "%O"
            replacement_values = replacements["owners"]
            phrase_strings += VoiceLibrary._process_phrase_2(text, tag, replacement_values)
        return phrase_strings

    def _get_saying_path(self, text):
        """Get the absolute path to the voice file we need, does not test if it exists"""
        logging.debug("Get saying '{}'".format(text))
        name = self._generate_filename_from_text(text)
        root_path = os.path.join(self.personality.config.get_config_path(), "cache", self.personality.get_voice())
        if not os.path.isdir(root_path):
            os.makedirs(root_path)
        file_path = os.path.join(root_path, name)
        return file_path

    def _save_saying(self, saying):
        """Saves the text to the voice database"""
        logging.debug("Saving saying '{}'".format(saying["text"]))
        key = self._get_key(saying["text"])
        self.speech[key] = saying
        self._save_files()

    def _save_files(self):
        """Save phrases (where appropriate) and speech databases"""
        logging.debug("Saving speech to {}".format(self.speech_full_path))
        str = json.dumps(self.speech, sort_keys=True, indent=4)
        with open(self.speech_full_path, "w") as out:
            out.write(str)

    @staticmethod
    def _generate_filename_from_text(text):
        logging.debug(text)
        m = hashlib.sha256()
        m.update(text.encode('utf-8'))
        name = m.hexdigest() + ".wav"
        return name

    @staticmethod
    def _get_key(phrase):
        """Convert the phrase into something that we can rely on as a key"""
        m = hashlib.sha256()
        m.update(phrase.encode('utf-8'))
        return m.hexdigest()

    def _make_saying(self, text, related_file_path=None, save=True):
        """Make the saying

            note that we need to cope with:
            key does not exist, file does not exist => make both
            key does exist, file does not exist => remake sound and save
            key does not exist, file does exist => save settings
            key does exist, file does exist => return
        """
        file_path = self._get_saying_path(text)
        required_key = self._get_key(text)
        if required_key in self.speech:
            if os.path.isfile(file_path):
                logging.debug("'"+text+"' already exists at '"+file_path+"'")
                return
        text = text.replace("'", "")
        text = text.replace("\u00B0", " degrees")
        text = text.replace("...", " ")
        text = text.replace("\"", "'")
        text = text.replace("’", "'")
        text = text.replace("…", " ")
        logging.debug("creating new saying '{}' in '{}'".format(text, file_path))
        if not os.path.isfile(file_path):
            #cmd = "echo \"" + text + "\" | text2wave -eval \"("+self.personality.get_voice()+")\" -o \"" + file_path + "\""
            cmd = "/home/pi/flite/bin/flite -voice slt -t \"{}\" -o \"{}\"".format(text, file_path)
            logging.debug("Cmd: {}".format(cmd))
            subprocess.run(cmd, shell=True)
            logging.debug("waiting for sound file to process")
            while not os.path.isfile(file_path):
                time.sleep(1)
        saying = { "text": text, "keep_while_exists": related_file_path, "file_path": file_path, "timestamp": datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp() }
        if save:
            self._save_saying(saying)
        return saying

    @staticmethod
    def convert_filename_to_speech_text(filename):
        """Also called from audio_state"""
        invalid_chars = re.compile('[\W_]+')
        has_num = re.compile('[0-9]+')
        has_ch = re.compile('[a-zA-Z]+')
        is_bbc_ending = re.compile("_m[\dA-Za-z]+_original")
        filename = os.path.basename(filename)
        filename = is_bbc_ending.sub("", filename)
        filename = filename[:filename.rfind('.')]
        filename = invalid_chars.sub(" ", filename)
        words = filename.split(" ")
        # remove words that are sequences of multiple letters and numbers
        # e.g.  M9 is OK
        #       BBC2 is OK
        #       m4823702aqs is not
        #       md23212 is not
        #       m23213 is not
        words = [w for w in words if not has_num.search(w) and has_ch.search(w)]
        return " ".join(words)

    def _make_saying_for_directory(self, phrase_text, dir, tags):
        if not os.path.isdir(dir):
            logging.debug("{} does not exist".format(dir))
            return
        logging.debug(dir)
        all_files = os.listdir(dir)
        for entry in all_files:
            full_path = os.path.join(dir, entry)
            if os.path.isdir(full_path):
                self._make_saying_for_directory(phrase_text, full_path, tags)
            else:
                logging.debug(entry)
                text = self.convert_filename_to_speech_text(entry)
                tags["track"] = text
                phrase_text_list = self._process_phrase( phrase_text, tags )
                for phrase_item in phrase_text_list:
                    self._make_saying(phrase_item, related_file_path=full_path)
                del tags["track"]

    def _make_saying_for_each_track(self, text, tags):
        """Iterate over each track in Radio_Uncompressed and Music"""
        path = self.personality.config.get_radio_path()
        if path:
            self._make_saying_for_directory(text, path, tags)
        else:
            logging.debug("No radio show path was given, check config.json.")
        path = self.personality.config.get_music_path()
        if path:
            self._make_saying_for_directory(text, path, tags)
        else:
            logging.debug("No music path was given, check config.json.")




