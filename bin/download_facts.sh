#!/bin/bash

LOCATION="/home/pi/.config/smartbot"
FILENAME="facts"
EXTENSION="json"

TMPFILE="$LOCATION/tmp.json"

if [ -e "$TMPFILE" ]
then
  rm -f "$TMPFILE"
fi

curl -X GET -H "Content-type: application/json" -H "Accept: application/json" "https://www.mentalfloss.com/api/facts?limit=1" > $TMPFILE

COUNTER=1
while true; do
  TEST_FILE="$LOCATION/$FILENAME_$COUNTER.$EXTENSION"
  if [ -e "$TEST_FILE" ]
  then
    ANY_DIFF=$( diff "$TMPFILE" "$TEST_FILE" | wc -l )
    if [ $ANY_DIFF -eq 0 ]
    then
      ## this is the same file
      SAVE_AS=""
      break
    fi
    COUNTER=$((COUNTER+1))
  else
    SAVE_AS="$TEST_FILE"
    break
  fi
done

## if SAVE_AS is not empty then we have not found an existing copy
## and we move our temporary file to our new file path
if [ "x$SAVE_AS" != "x" ]
then
  echo "Saving '$TMPFILE' as '$SAVE_AS'"
  mv "$TMPFILE" "$SAVE_AS"
else
  rm "$TMPFILE"
fi