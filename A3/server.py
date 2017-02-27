import random
import socket
import sys
import os.path
import datetime
import string
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

cipher = 0

#helper function for standardized logging to stdout
def log(msg):
	print((datetime.datetime.now()).strftime("%H:%M:%S") + ": " + msg)
	
	
	
#sends data encrypted 
def send_enc(msg, c_socket):
	padder = padding.PKCS7(128).padder()
	padded_msg = padder.update(msg) + padder.finalize()
	if cipher != 0:
		enc = cipher.encryptor()
		ctext = enc.update(padded_msg) + enc.finalize()
		c_socket.sendall(ctext)
	else:
		c_socket.sendall(padded_msg)
	

	
#receive encrypted data 
def recv_enc(c_socket, num_bytes):
	ctext = c_socket.recv(num_bytes)
	unpadder = padding.PKCS7(128).unpadder()
	#decrypt if encrypted
	if cipher != 0:
		dec = cipher.decryptor()
		padded_msg = dec.update(ctext) + dec.finalize()
	#else do nothing
	else: 
		padded_msg = ctext
	#unpad original message
	try:
		ptext = unpadder.update(padded_msg) + unpadder.finalize()
	except ValueError:
		print("error: padding error likely due to incorrect decryption")
		ptext = ctext
	return ptext



#expands the key to 32 bytes
def expand_key(key):
	while len(key) < 32:
		key = key + key
	return key[:32]
	
	
	
#set the encryption mode https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/
def set_cipher(cipher_type, iv, key):
	global cipher
	backend = default_backend()
	if cipher_type == "aes128":
		cipher = Cipher(algorithms.AES(key[:16].encode('UTF-8')), modes.CBC(iv), backend=backend)
	elif cipher_type == "aes256":
		cipher = Cipher(algorithms.AES(key.encode('UTF-8')), modes.CBC(iv), backend=backend)
	elif cipher_type == "none":
		cipher = 0
	
	
	
#sends challenge to client
def challenge_client(c_socket):
	challenge = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(7)).encode()
	
	send_enc(challenge, c_socket)
	response = recv_enc(c_socket, 32)
	print(response)
	print(challenge)
	return response == (challenge + challenge)
	
	
	
#read file for and send to client
def read(c_socket, filename):
	#check file exists
	if not os.path.isfile(filename):
		error_msg = "error: no file named '" + filename + "'"
		log(error_msg)
		send_enc(b'FAIL', c_socket)
		return
	send_enc(b'PASS', c_socket)
	
	#file exists, send file size
	file_size = os.path.getsize(filename)
	send_enc(str(file_size).encode(), c_socket)
	file = open(filename, 'rb')
	#read file and send encrypted to client TO DO
	while file_size > 0:
		msg = file.read(min(1024, file_size))
		send_enc(msg, c_socket)
		file_size = file_size - 1024

		
	
#write file from client
def write(c_socket, filename):
	#"recvall", and unencrypt TO DO
	
	try:
		#write the file TO DO
		print("")
	except:
		error_msg = "error: file is not writable"
		log(error_msg)
		return
	
	
	
#handles client connections from start to finish
def handle_connection(c_socket, key):
	key = expand_key(key)
	
	#STEP 1 cipher establishment
	cipher_and_iv = c_socket.recv(24).decode('UTF-8').split(";")
	cipher_type = cipher_and_iv[0]
	iv =cipher_and_iv[1]
	log("cipher: " + cipher_type.upper())
	
	set_cipher(cipher_type, iv.encode('UTF-8'), key)
	
	#STEP 2 challenge to client
	if not challenge_client(c_socket):
		log("error: incorrect key")
		send_enc(b'FAIL', c_socket)
		return
	send_enc(b'PASS', c_socket)
	
	#STEP 3 get command from client
	full_command = recv_enc(c_socket, 32).decode().split(";")
	command = full_command[0]
	filename = full_command[1]
	log("command: " + command + " " + filename)
	
	#execute read command
	if command == "read":
		read(c_socket, filename)
	#execute write command
	elif command == "write":
		write(c_socket, filename)



#main
def main():
 #collect command line arguments
	if (len(sys.argv) == 3):
		port = sys.argv[1]
		key = sys.argv[2]
	elif (len(sys.argv) == 2):
		port = sys.argv[1]
		key = "NULL_KEY"
	#if error in arguments, stop the program
	else:
		print("command is:\n\t'server.py port [key]'")
		quit()
		
	#ensure all arguments are valid
	try:
		assert port.isdigit()
	except:
		print("1 or more arguments are invalid. Please ensire all arguments are valid")
		quit()
	
	#generate a random key (cryptographically secure)
	if key == "NULL_KEY":
		key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))
	
	#make a server socket to listen to incoming connections
	s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s_socket.bind(("localhost", int(port)))
	s_socket.listen(5)
	print("Server listening on localhost on port " + port)
	print("Using secret key: " + key)
	
	#loop to accept connections and spawn handler threads
	while 1:
		(c_socket, addr) = s_socket.accept()
		log("new connection from " + str(addr))
		
		handle_connection(c_socket, key)
		log("done")
		print("")
		
		c_socket.close()
	

	
main()

