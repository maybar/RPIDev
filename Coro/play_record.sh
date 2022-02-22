#!/bin/sh

if [ -z "$1" ]
	then echo "No audio file supplied"
	exit 1
fi

echo " Start playing "
aplay -D plughw:1 --vumeter=mono -i $1
