#!/usr/bin/python

import datetime
import time
import os
import select

# Read fifo pipe
fifo = "/home/pi/.config/smartbot/fifos/lescanner.fifo"

while True:
    if os.path.exists(fifo) == False:
        time.sleep(1)
        continue
    with open(fifo, "w+") as f:
        select.select([f],[],[f])
        data = f.read()
        if len(data) > 0:
            print("{} {}".format(datetime.datetime.now(),data))
#            f.write("")

