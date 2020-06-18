#!/usr/bin/python3

import getpodcast
import json
import sys
import os

config_file_path = "/home/pi/.config/smartbot/podcasts.json"
if not os.path.isfile(config_file_path):
    print("Configuration file not found ('{}').".format(config_file_path))
    sys.exit(1)

config = {}
with open(config_file_path, "r") as in_file:
    config = json.load(in_file)

if not os.path.isdir(config["download_directory"]):
    print("Download directory does not exist ({})".format(config["download_directory"]))
    sys.exit(1)

if "podcasts" in config:
    podcast_list = config["podcasts"]

for podcast in podcast_list:
    opt = getpodcast.options(
        root_dir=config["download_directory"]
    )

    podcasts = {
        podcast["name"]: podcast["url"]
    }

    print(opt)
    print(podcasts)

    getpodcast.getpodcast(podcasts, opt)