#!/usr/bin/python3

import podcasts
import json
import sys
import os

SMARTBOT_PATH=os.path.abspath(os.path.join(os.path.realpath(__file__), "..", ".."))
config_file_path = "/home/pi/.config/smartbot/podcasts.json"
if not os.path.isfile(config_file_path):
    print("Configuration file not found ('{}').".format(config_file_path))
    sys.exit(1)

config = {}
with open(config_file_path, "r") as in_file:
    config = json.load(in_file)

config["download_directory"] = config["download_directory"].replace("%SMARTBOT%", SMARTBOT_PATH)
if not os.path.isdir(config["download_directory"]):
    print("Download directory does not exist ({})".format(config["download_directory"]))
    sys.exit(1)

if "podcasts" in config:
    podcast_list = config["podcasts"]

for podcast in podcast_list:
    opt = podcasts.options(
        run=True,
        onlynew=True,
        root_dir=config["download_directory"],
		template="{rootdir}/{podcast}/{date} - {title}{ext}"
    )

    podcastList = {
        podcast["name"]: podcast["url"]
    }

    print(opt)
    print(podcastList)

    podcasts.getpodcast(podcastList, opt)
