#!/bin/bash

curl -X GET -H "Content-type: application/json" -H "Accept: application/json" "https://www.mentalfloss.com/api/facts?limit=1" > /home/pi/.config/smartbot/facts.json