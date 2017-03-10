import random
import select
import socket
import sys
import datetime
import _thread
import string
import fileinput
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

MAX_KEY_LENGTH = 32 		#in bytes 256 in bits
AES128_KEY_LENGTH = 16	#in bytes 128 in bits
IV_LENGTH = 16					#in bytes 128 in bits
MSG_BLOCK_SIZE = 1024		#in bytes or 1 KB

cipher = 0
pad = padding.PKCS7(128)#in bits 16 in bytes
	
	
#pads, encrypts and sends data
	#msg should be a bytes object
	#c_socket, is the socket it should be sent through
def send_enc(msg, c_socket):
	padder = pad.padder()
	padded_msg = padder.update(msg) + padder.finalize()
	if cipher != 0:
		enc = cipher.encryptor()
		ctext = enc.update(padded_msg) + enc.finalize()
		c_socket.sendall(ctext)
	else:
		c_socket.sendall(padded_msg)
	

	
#receives, decrypts, and unpads data
	#c_socket is the socket it should be sent through
	#num_bytes is the number of bytes to receive, including any padding bytes in message
	##returns bytes object of message
def recv_enc(c_socket, num_bytes):
	ctext = c_socket.recv(num_bytes)
	unpadder = pad.unpadder()
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
		print("error: padding error")
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
	
	
#communicates with server in read mode
	#c_socket is the socket to communicate through
def read(c_socket):
	if recv_enc(c_socket, 16) == b'FAIL':
		print("error: server could not find file")
		return
	#receive the size of file and then receive in 1024 chunks (1040 with padding)
	file_size = int(recv_enc(c_socket, 16))
	while file_size > 0:
		msg = recv_enc(c_socket, min(MSG_BLOCK_SIZE + 16, file_size + (16 - file_size%16)))
		sys.stdout.buffer.write(msg)
		file_size = file_size - MSG_BLOCK_SIZE
	
	
	
#communicates with server to write the stdin to the file
	#c_socket is the socket to communicate through
def write(c_socket):
	if (recv_enc(c_socket, 16) != b'PASS'):
		print("File is unwritable")
		return
	#Read the file in blocks and send in blocks
	msg = sys.stdin.buffer.read(MSG_BLOCK_SIZE)
	while (len(msg) == MSG_BLOCK_SIZE):
		send_enc(msg, c_socket)
		msg = sys.stdin.buffer.read(MSG_BLOCK_SIZE)
	#send the last block which is less than 1024 bits
	send_enc(msg, c_socket)
	
	#check for confirmation from server of correct receipt
	if (recv_enc(c_socket, 16) == b'PASS'):
		print("OK")
	else:
		print("error: didn't receive confirmation from server")
	
	

#handles connection with server from beginning to end
	#c_socket is socket to connect through
	#command is string of read or write
	#filename is a string
	#cipher_type is a string of none, aes128, or aes256
	#key is a string
def handle_connection(c_socket, command, filename, cipher_type, key):
	key = expand_key(key)
		
	#STEP 1 send cipher and set up cipher
	iv = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(IV_LENGTH))
	c_socket.sendall((cipher_type + ";" + iv).encode())
	set_cipher(cipher_type, iv.encode(), key)
	
	#STEP 2 challenge from server
	challenge = recv_enc(c_socket, 16)
	#send re-encrypted message with padding
	send_enc((challenge + challenge), c_socket)
	#receive reult of challenge
	if recv_enc(c_socket, 16) != b'PASS':
		print("error: mismatching keys used")
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
	
	#close the socket	
	c_socket.close()	
	
main()
