#!/bin/bash

DEST="$HOME/Radio"

for full in $( find $HOME/Radio_Uncompressed -iname "*.m4a" | head -n 1 ) 
do 
    echo "Compressing $full"
    ls -la $full
    f=$(basename $full)
    ffmpeg -i "$full" -vbr 1 $DEST/"${f%.m4a}.m4a"
done
