#!/bin/bash

if (( $# != 2)); then
   echo "Improper usage. Usage is $0 [ip] [port]"
   exit
fi

echo "Creating dummy files..."
dd if=/dev/urandom bs=1K iflag=fullblock count=1 > 1KB.bin
dd if=/dev/urandom bs=1K iflag=fullblock count=1K > 1MB.bin
dd if=/dev/urandom bs=1K iflag=fullblock count=256K > 256MB.bin

echo "MD5 checksums in order (1kb, 1mb, 256mb)"
openssl md5 1KB.bin
openssl md5 1MB.bin
openssl md5 256MB.bin

echo "Files created. Press any key to test 256MB write no encryption ..."
read -rsn1

#256MB write
echo "Uploading 256MB.bin md5:"
openssl md5 256MB.bin
python3 client.py write 256MB.bin $1:$2 none < 256MB.bin
echo ""

echo "Press any key to test 1MB write no encryption"
read -rsn1

echo "Uploading 1MB.bin md5:"
openssl md5 1MB.bin
python3 client.py write 256MB.bin $1:$2 none < 1MB.bin
echo ""

echo "Press any key to download 1MB no encryption & compare md5"
read -rsn1

echo "Downloading 1MB.bin md5:"
openssl md5 1MB.bin
python3 client.py read 256MB.bin $1:$2 none > 1MB_copy.bin

echo ""
echo "Md5 comparison: "
echo ""
openssl md5 1MB.bin
openssl md5 1MB_copy.bin
echo ""


echo "Demo suite 1 complete. Please run demo suite 2."
