#!/usr/bin/python3

import os
import subprocess
import time
from multiprocessing import Pool
from sys import stdout

file="/opt/smartbot/programs.txt"
dest_dir="/home/pi/Radio_Uncompressed/tmp"
get_iplayer="/home/pi/get_iplayer/get_iplayer"

if not os.path.isfile(file):
    raise ValueError("file "+file+" was not found")
if not os.path.isfile(get_iplayer):
    raise ValueError("get_iplayer was not found at "+get_iplayer)
if not os.path.isdir(dest_dir):
    raise ValueError(dest_dir+" does not exist to save downloads to.")


def load_targets():
    global file
    global dest_dir
    targets=[]
    with open(file,"r") as in_file:
        line = in_file.readline()
        while line:
            if line[0] == '#' or len(line.strip()) == 0:
                line = in_file.readline()
                continue
            if not os.path.isdir(dest_dir):
                raise ValueError(dest_dir+" does not exist")
            channel, regex = line.split(",")
            channel=channel.strip('\n').strip('\"')
            regex = regex.strip('\n').strip('\"')
            target = { "channel": channel, "regex": regex, "dest_dir": dest_dir }
            targets.append(target)
            line = in_file.readline()
    return targets


def run_get_iplayer(target, ID):
    # can we locate get_iplayer some how or read in from a config file
    cmd = get_iplayer+" --type=radio --channel=\""+target["channel"]+"\" --radiomode=good -g --output \""+target["dest_dir"]+"\" \""+target["regex"]+"\""
    stdout.write("["+str(ID)+"] "+cmd+"\n")
    stdout.flush()
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    (output,junk) = p.communicate()
    lines = output.decode("utf-8").split("\n")
    output_str = "\n".join([ "["+str(ID)+"] " + line for line in lines ])
    stdout.write(output_str+"\n")
    stdout.flush()


if __name__ == "__main__":
    print("Loading programmes to download")
    targets = load_targets()
    # this should be set to num processors - 1
    pool = Pool(processes=3)
    jobs = []
    ID=0
    #run_get_iplayer(targets[0], -1)
    for target in targets:
        print("Creating thread for "+target['regex'])
        proc = pool.apply_async(func=run_get_iplayer, args=(target,ID))
        jobs.append(proc)
        ID += 1

    print("Waiting for jobs to finish")
    while(not all([p.ready() for p in jobs])):
        stdout.flush()
        time.sleep(1)
    pool.close()
    pool.join()

