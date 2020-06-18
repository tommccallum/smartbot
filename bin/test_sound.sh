#!/bin/bash

echo "This should play 1 second of white noise if Pulse is working as expected."
timeout 1 pacat -vvvv /dev/urandom
