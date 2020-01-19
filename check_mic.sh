#!/bin/bash

EXISTS=$( lsusb | grep "JMTek" )

if [ "x$EXISTS" == "x" ]
then
    echo "USB Mic is not attached."
    exit 1
fi
echo "USB Mic has been attached"
lsusb | grep "JMTek"
exit 0
