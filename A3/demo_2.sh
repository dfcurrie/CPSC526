#!/bin/bash

if (( $# != 3)); then
   echo "Improper usage. Usage is $0 [ip] [port] [good_key]"
   exit
fi

#256MB write
echo "Uploading 1MB.bin aes128 bad key:"
cat 1MB.bin | python3 client.py write 1MB.bin $1:$2 aes128 12345678910
echo ""

echo "Press a key to run bad file test..."
read -rsn1

echo "Bad file:"
python3 client.py read non_existent.txt $1:$2 aes128 $3
echo ""

echo "Press a key to run 1MB none, aes128, aes256 upload test..."
read -rsn1

echo "Uploading 1MB.bin none"
cat 1MB.bin | python3 client.py write 1MB.bin $1:$2 none
echo ""

echo "Uploading 1MB.bin aes128"
cat 1MB.bin | python3 client.py write 1Maes128.bin $1:$2 aes128 $3
echo ""

echo "Uploading 1MB.bin aes256"
cat 1MB.bin | python3 client.py write 1Maes256.bin $1:$2 aes256 $3
echo ""

echo "Press a key to run download 1MB none, aes128, aes256 test..."
read -rsn1

echo "Downloading 1MB.bin none"
python3 client.py read 1MB.bin $1:$2 none > 1MB.bin
echo ""

echo "Downloading 1MB128.bin aes128"
python3 client.py read 1Maes128.bin $1:$2 aes128 $3 > 1Maes128.bin
echo ""

echo "Downloading 1Maes256.bin aes256"
python3 client.py read 1Maes256.bin $1:$2 aes256 $3 > 1Maes256.bin
echo ""

echo ""
echo "Md5 comparison: "
echo ""
openssl md5 1MB.bin
openssl md5 1Maes128.bin
openssl md5 1Maes256.bin
echo ""

rm *.bin


echo "Demo suite finished. Please remember to delete dummy files on server."
