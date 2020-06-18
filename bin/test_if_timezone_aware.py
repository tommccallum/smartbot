#!/usr/bin/python3

from dateutil.tz import tzlocal
import datetime
import time

print(datetime.datetime.now())
print(datetime.datetime.now().timestamp())
print(time.time())
print(datetime.datetime.now(tzlocal()))