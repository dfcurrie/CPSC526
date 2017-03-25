#!/bin/bash

if (( $# != 1)); then
   echo "Improper usage. Usage is $0 [config file]"
   exit
fi

echo "Press any key to test incorrect file configurations"
read -rsn1

echo "Testing non-existant file..."
python3 fw.py missingFile
echo ""

echo "Testing bad configuration files..."
python3 fw.py bad_comment
python3 fw.py bad_line
python3 fw.py bad_mask
echo ""

echo "Press any key to run specified config file with bad packets"
read -rsnl
python3 fw.py $1 < bad_packets
echo ""

echo "Press any key to run specified config file with good packets"
read -rsnl
python3 fw.py $1 < packets
echo ""
