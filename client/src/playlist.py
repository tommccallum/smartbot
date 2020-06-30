import random
import logging
import os
import numpy

# if "path" in self.state_config:
#     local_path = self.state_config["path"]
#     local_path = local_path.replace("%HOME%", Configuration.HOME_DIRECTORY)
#     local_path = local_path.replace("%CONFIG%", self.configuration.config_path)

class Playlist:
    def __init__(self, list_of_tracks, home_path=None, config_path=None, smartbot_path=None ):
        """Set up playlist"""
        self.playlist = []
        self.ordering = []
        self.position = -1
        self.home_path = home_path
        self.config_path = config_path
        self.smartbot_path = smartbot_path
        self._load(list_of_tracks)

    def size(self):
        return len(self.playlist)

    def _load(self, list_of_tracks):
        """Load playlist from configuration array"""
        # logging.debug(list_of_tracks)
        if type(list_of_tracks) is not list:
            raise ValueError("playlist configuration is not a list of tracks or a list of directories")
        for item in list_of_tracks:
            self._add_track(item)
        # make playlist unique
        self.playlist = list({v['url']:v for v in self.playlist}.values())
        self.ordering = list(range(0, len(self.playlist)))

    def _replace_tags(self, text):
        if self.home_path is not None:
            text = text.replace("%HOME%", self.home_path)
        if self.config_path is not None:
            text = text.replace("%CONFIG%", self.config_path)
        if self.smartbot_path is not None:
            text = text.replace("%SMARTBOT%", self.smartbot_path)
        return text

    def select_by_regex_only_if_earlier(self, text):
        counter = 0
        track = None
        for p in self.playlist:
            if text in p["url"]:
                track = p
                break
            counter += 1
        if track and counter > self.position:
            self.set_current(track)
            return True
        return False

    def select_by_regex(self, text):
        """Select by a substring (Should be a regex but have been lazy!)"""
        for p in self.playlist:
            if text in p["url"]:
                self.set_current(p)
                return True
        return False

    def _add_track(self, track, recursive_dir = True):
            # logging.debug(track)
            if type(track) is dict:
                if "directory" in track:
                    # a directory with options
                    directory = self._replace_tags(track["directory"])
                    recursive = True
                    extensions = None
                    if "include-subdir" in track:
                        recursive = track["include-subdir"]
                    if "extensions" in track:
                        extensions = track["extensions"]
                    self._load_directory(directory, recursive, extensions)
                elif "url" in track:
                    # just a single file or url
                    if not "date" in track:
                        track_date = 0
                        if os.path.isfile(track["url"]):
                            track_date = os.path.getmtime(track)
                        track["date"] = track_date
                    track["url"] = self._replace_tags(track["url"])
                    self.playlist.append(track)
                else:
                    logging.error("invalid playlist track '{}'".format(track))
            else:
                track = self._replace_tags(track)
                if os.path.isdir(track):
                    # a plain directory
                    self._load_directory(track, recursive_dir)
                elif os.path.isfile(track):
                    # a plain file
                    track_date = os.path.getmtime(track)
                    new_item = {
                        "url": track,
                        "date": track_date
                    }
                    self.playlist.append(new_item)
                elif track[0:3] == "http":
                    # a plain url for a stream perhaps
                    new_item = {
                        "url": track,
                        "date": 0
                    }
                    self.playlist.append(new_item)
                else:
                    logging.error("invalid playlist track '{}'".format(track))

    def _check_extension(self, file, extensions):
        """
        Check file against list of allowed extensions
        """
        if extensions is None:
            return True
        if type(extensions) is list and len(extensions) == 0:
            return True
        if type(extensions) is not list:
            extensions = [str(extensions)]
        e = os.path.splitext(file)[1][1:]
        for ext in extensions:
            if e == ext:
                return True
        return False

    def _load_directory(self, directory, recursive = True, extensions = []):
        """Read in all files recursively from directory"""
        all_files = os.listdir(directory)
        for entry in all_files:
            full_path = os.path.join(directory, entry)
            if recursive:
                if os.path.isdir(full_path):
                    self._load_directory(full_path, recursive, extensions)
                else:
                    if self._check_extension( full_path, extensions ):
                        self._add_track(full_path, recursive)
            else:
                # if not recursive we must not send a track to _add_track
                # otherwise it will recurse down for first directory which
                # is not what we want.
                if os.path.isfile(full_path):
                    if self._check_extension(full_path, extensions):
                        self._add_track(full_path, recursive)

    def sort(self, how:list ):
        if len(self.playlist) == 0:
            return
        ordering = "name"
        descending = False
        if type(how) is list:
            ordering = how[0]
            if ordering not in ["name", "date"]:
                ordering = "name"
                logging.error("ordering field is not 'name' or 'date'")
            if len(how) > 1:
                descending = how[1].upper()[0:4] == "DESC"
            self.ordering = list(numpy.argsort([a[ordering] for a in self.playlist]))
            if descending:
                self.ordering.reverse()
        else:
            self.ordering = list(numpy.argsort([a[ordering] for a in self.playlist]))

    def is_empty(self):
        return len(self.playlist) == 0

    def next(self):
        """Get next tack"""
        return self.get_track(self.position+1)

    def prev(self):
        """Get previous track"""
        return self.get_track(self.position-1)

    def first(self):
        """Get first track"""
        return self.get_track(0)

    def last(self):
        """Get last track"""
        return self.get_track(len(self.ordering)-1)

    def shuffle(self):
        """Randomly shuffle the play order"""
        if len(self.playlist) > 0:
            self.ordering = list(range(0,len(self.playlist)))
        random.shuffle(self.ordering)

    def reset(self):
        """Reset playlist to empty playlist"""
        self.ordering.clear()
        self.playlist.clear()
        self.position = -1

    def set_current(self, track):
        """
        this might have come from a saved state, need to find it and set it as this one
        """
        for ii in self.ordering:
            if self.playlist[self.ordering[ii]]["url"] == track["url"]:
                logging.debug("setting track to number {}".format(ii))
                self.position = ii
                return

    def get_track(self, index):
        """Get a track and update book-keeping"""
        if len(self.ordering) == 0:
            return None
        if index >= len(self.ordering):
            index = index % len(self.ordering)
        if index < 0:
            index = len(self.ordering) - (index % len(self.ordering))
        self.position = index
        logging.debug("index {} is position {}".format(index, self.position))
        return self.playlist[self.ordering[self.position]]

    def __repr__(self):
        return "playlist{}".format(self.playlist)

