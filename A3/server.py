import random
import socket
import sys
import os.path
import datetime
import time
import string
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

MAX_KEY_LENGTH = 32 		#in bytes 256 in bits
AES128_KEY_LENGTH = 16	#in bytes 128 in bits
MSG_BLOCK_SIZE = 1024		#in bytes or 1 KB

cipher = 0
pad = padding.PKCS7(128)#in bits 16 in bytes

#helper function for standardized logging to stdout
	#msg string of the message to be logged by the server
def log(msg):
	print((datetime.datetime.now()).strftime("%H:%M:%S") + ": " + msg)
	
	
	
	
#pads, encrypts and sends data
	#msg should be a bytes object
	#c_socket, is the socket it should be sent through
def send_enc(msg, c_socket):
	#pad message
	padder = pad.padder()
	padded_msg = padder.update(msg) + padder.finalize()
	
	#pad length of padded message
	msg_length = str(len(padded_msg)).encode()
	padder = pad.padder()
	padded_msg_length = padder.update(msg_length) + padder.finalize()
	
	if cipher != 0:
		#encrypt and send length
		enc = cipher.encryptor()
		ctext = enc.update(padded_msg_length) + enc.finalize()
		c_socket.sendall(ctext)
		
		#encrypt and send message
		enc = cipher.encryptor()
		ctext = enc.update(padded_msg) + enc.finalize()
		c_socket.sendall(ctext)
	else:
		#send in clear if 'none'
		c_socket.sendall(padded_msg_length)
		c_socket.sendall(padded_msg)
	

	
#receives, decrypts, and unpads data
	#c_socket is the socket it should be sent through
	##returns bytes object of message
def recv_enc(c_socket, timeout=0):
	#receives the length of the next package
	ctext = c_socket.recv(16)
	unpadder = pad.unpadder()
	now = time.time()
	end = now + timeout
	#makes sure it gets the whole int and padding
	while (len(ctext) < 16 and now < end):
		ctext = ctext + c_socket.recv(16-len(ctext))
		now = time.time()
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
		log("error: padding error")
		return b'error'
	
	#receive the entire packet based on the length already received
	ctext = c_socket.recv(int(ptext))
	unpadder = pad.unpadder()
	now = time.time()
	end = now + timeout
	while (len(ctext) < int(ptext) and now < end):
	    ctext = ctext + c_socket.recv(int(ptext)-len(ctext))
	    now = time.time()
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
		log("error: padding error")
		ptext = ctext
	return ptext



#expands the key to 32 bytes (256 bits)
	#key is the key that may or may not be too short
	##returns key as string
def expand_key(key):
	while len(key) < MAX_KEY_LENGTH:
		key = key + key
	return key[:MAX_KEY_LENGTH]
	
	
	
#set the cipher, and apply the correct key kength
	#cipher_type is a string that is aes128 aes256 or none 
	#iv is initalization vector as bytes object
	#key is string
def set_cipher(cipher_type, iv, key):
	global cipher
	backend = default_backend()
	if cipher_type == "aes128":
		cipher = Cipher(algorithms.AES(key[:AES128_KEY_LENGTH].encode()), modes.CBC(iv), backend=backend)
	elif cipher_type == "aes256":
		cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv), backend=backend)
	elif cipher_type == "none":
		cipher = 0
	
	
	
#sends challenge to client
	#c_socket is socket to communicate with client
	##returns bool whether pass or fail
def challenge_client(c_socket):
	#generates a random challenge
	challenge = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8)).encode()
	send_enc(challenge, c_socket)
	#receives response that should be original challenge twice
	response = recv_enc(c_socket)
	return response == (challenge + challenge)
	
	
	
#read file for and send to client
	#c_socket is socket to communicate with client
	#filename is name of file to read from
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
	#read file and send encrypted to client
	while file_size > 0:
		msg = file.read(min(MSG_BLOCK_SIZE, file_size))
		send_enc(msg, c_socket)
		file_size = file_size - MSG_BLOCK_SIZE
	file.close()
		
		
	
#write contents received from client to filename
	#c_socket is socket to communicate with
	#filename is string of file to write to
def write(c_socket, filename):
	#try to open file. if error, communicate to client
	try:
		# open file to write
		write_file = open(filename, "wb")
		send_enc(b'PASS', c_socket)
	#if file can't open, tell client	
	except:
		error_msg = "error: file is not writable"
		log(error_msg)
		send_enc(b'FAIL', c_socket)
		return
	
	#receive the contents from client
	msg = recv_enc(c_socket, 1)
	while (len(msg) == 1024):
		write_file.write(msg)
		msg = recv_enc(c_socket,1)
	write_file.write(msg)
	
	#confirm file was read to completion
	send_enc(b'PASS', c_socket)
	
	#close the socket
	write_file.close()
		

	
#handles client connections from start to finish
	#c_socket is socket to communicate with client
	#key is string
def handle_connection(c_socket, key):
	key = expand_key(key)
	
	#STEP 1 cipher establishment
	cipher_and_iv = c_socket.recv(24).decode().split(";")
	cipher_type = cipher_and_iv[0]
	iv =cipher_and_iv[1]
	log("cipher: " + cipher_type.upper())
	
	set_cipher(cipher_type, iv.encode(), key)
	
	#STEP 2 challenge to client
	if not challenge_client(c_socket):
		log("error: incorrect key")
		send_enc(b'FAIL', c_socket)
		return
	send_enc(b'PASS', c_socket)
	
	#STEP 3 get command from client
	full_command = recv_enc(c_socket).decode().split(";")
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
		key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(MAX_KEY_LENGTH))
	
	#make a server socket to listen to incoming connections
	s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host = socket.gethostname()
	s_socket.bind((host, int(port)))
	s_socket.listen(5)
	print("Server listening on " + host + " on port " + port)
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
