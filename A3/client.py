import random
import select
import socket
import sys
import datetime
import _thread
import string
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

	
cipher = 0
	
	
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

	

#expands the key to 32 bytes (256 bits)
def expand_key(key):
	while len(key) < 32:
		key = key + key
	return key[:32]
	
	
	
#set the cipher, and apply the correct key kength
def set_cipher(cipher_type, iv, key):
	global cipher
	backend = default_backend()
	if cipher_type == "aes128":
		cipher = Cipher(algorithms.AES(key[:16].encode('UTF-8')), modes.CBC(iv), backend=backend)
	elif cipher_type == "aes256":
		cipher = Cipher(algorithms.AES(key.encode('UTF-8')), modes.CBC(iv), backend=backend)
	
	
	
#communicates with server in read mode
def read(c_socket):
	if recv_enc(c_socket, 16) == b'FAIL':
		print("error: server could not find file")
		return
	#receive the size of file and then receive in 1024 chunks (1040 with padding)
	file_size = int(recv_enc(c_socket, 16))
	while file_size > 0:
		msg = recv_enc(c_socket, min(1040, file_size + (16 - file_size%16)))
		print(msg, end='')
		file_size = file_size - 1024
	
	
	
#TO DO
def write(c_socket):
	print("write")
	
	

#handles connection with server from beginning to end
def handle_connection(c_socket, command, filename, cipher_type, key):
	key = expand_key(key)
		
	#STEP 1 send cipher and set up cipher
	iv = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))
	c_socket.sendall((cipher_type + ";" + iv).encode('UTF-8'))
	set_cipher(cipher_type, iv.encode('UTF-8'), key)
	
	#STEP 2 challenge from server
	challenge = recv_enc(c_socket, 16)
	#send re-encrypted message with padding
	send_enc((challenge + challenge), c_socket)
	#receive reult of challenge
	if recv_enc(c_socket, 16) != b'PASS':
		print("Error: mismatching keys used")
		return
	
	#STEP 3 send command
	send_enc((command + ";" + filename).encode(), c_socket)
	
	#execute read command
	if command == "read":
		read(c_socket)
	#execute write command
	elif command == "write":
		write(c_socket)
 
 
 
#main
def main():
	#collect command line arguments
	if (len(sys.argv) == 6):
		command = sys.argv[1]
		filename = sys.argv[2]
		host_port_list = sys.argv[3].split(":")
		hostname = host_port_list[0]
		port = host_port_list[1]
		cipher = sys.argv[4]
		key = sys.argv[5]
	elif (len(sys.argv) == 5):
		command = sys.argv[1]
		filename = sys.argv[2]
		host_port_list = sys.argv[3].split(":")
		hostname = host_port_list[0]
		port = host_port_list[1]
		cipher = sys.argv[4]
		key = "NULL_KEY"
	#if error in arguments, stop the program
	else:
		print("command is:\n\t'client.py command filename hostname:port cipher [key]'")
		quit()
		
	#ensure all arguments are valid
	try:
		assert (command == "write" or command == "read")
		assert port.isdigit()
		assert (cipher == "aes256" or cipher == "aes128" or cipher == "none")
		assert(key != "NULL_KEY" or cipher == "none")
	except:
		print("1 or more arguments are invalid. Please ensure all arguments are valid")
		quit()
		
	#try to make a connection
	c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		c_socket.connect((hostname,int(port)))
	except:
		print("A connection could not be established. The program shall now close...")
		c_socket.close()
		quit()
	
	handle_connection(c_socket, command, filename, cipher, key)
	
	
main()