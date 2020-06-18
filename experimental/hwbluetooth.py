# Note: don't call this file bluetooth.py as it will confuse the name resolution!
import bluetooth


# if the client device is on scan mode then this will pick it up
nearby_devices = bluetooth.discover_devices(lookup_names=False)

print("found {} devices".format(len(nearby_devices)))

#for name, addr in nearby_devices:
#    print(" %s - %s", (addr, name))
for addr in nearby_devices:
    print( " %s",addr)


