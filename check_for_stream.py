#!/usr/bin/python3
import http.client
import os
import subprocess
import time
import psutil

n=5
r2="http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p"

def is_item_playing():
	for proc in psutil.process_iter():
		try:
			pinfo = proc.as_dict(attrs=['name'])
			if "mplayer" in pinfo["name"]:
				return False
		except:
			pass
	return True

while True:
	if is_item_playing():
		# try radio 2
		print("Detected no other stream, playing Radio 2")
		cmd = "mplayer --really-quiet "+r2
		subprocess.Popen(cmd.split(" ")).communicate()
	else:
		time.sleep(10)

