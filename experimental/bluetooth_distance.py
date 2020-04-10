import json
from sys import argv

def getDistance(rssi: int, txPower: int):
    """
     Gives distance in metres
     RSSI = TxPower - 10 * n * lg(d)
     n = 2 (in free space)

     d = 10 ^ ((TxPower - RSSI) / (10 * n))
     """
    return 10.0 ** ((txPower - rssi) / (10.0 * 2.0));

def getDistance2(rssi: int):
    return 19.713 * (rssi/-62) - 18.769

file="/home/pi/.config/smartbot/devices.json"
j = json.load(file)


