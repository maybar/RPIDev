#!/bin/sh
_now=$(date +"%d%m%H%M")
file=""
 
if [ -z "$1" ]	
then 
   file="rec_$_now.wav"
else
   file=$1
fi

echo " Start recording $file "
arecord -D plughw:1 -r 44100 -f cd --vumeter=mono $file
