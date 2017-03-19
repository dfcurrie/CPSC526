#!/bin/bash

if (( $# != 1)); then
   echo "Improper usage. Usage is $0 [config file]"
   exit
fi

echo "Press any key to test incorrect file configurations"
read -rsn1

echo "Testing non-existant file..."
python3 fw.py missingFile
echo "Testing bad configuration file..."
python3 fw.py badConfigFile
echo ""


echo "Press any key to run the firewall"
read -rsnl

python3 fw.py $1 < packets
