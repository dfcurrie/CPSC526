import random
import socket
import sys
import os.path
import datetime
import string

#helper function for standardized logging to stdout
def log(msg):
	print((datetime.datetime.now()).strftime("%H:%M:%S") + ": " + msg)
	
	
	
#sebds data encrypted TO DO
def send_enc(msg, c_socket):
	c_socket.sendall(msg.encode('UTF-8'))
	

	
#receive encrypted data TO DO
def recv_enc(c_socket, num_bytes):
	return c_socket.recv(num_bytes).decode('UTF-8')

	
	
#sends challenge to client
def challenge_client(c_socket):
	challenge = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
	
	send_enc(challenge, c_socket)
	response = recv_enc(c_socket, 16)
	
	return response == (challenge + "AAAAAAAA")
	
	
	
#read file for and send to client
def read(c_socket, filename):
	#check file exists
	if not os.path.isfile(filename):
		error_msg = "error: no file named '" + filename + "'"
		log(error_msg)
		send_enc("FAIL", c_socket)
		return
	send_enc("PASS", c_socket)
	
	#file exists, send file size
	file_size = os.path.getsize(filename)
	send_enc(str(file_size), c_socket)
	file = open(filename, 'r')
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
def handle_connection(c_socket):
	#STEP 1 cipher establishment
	cipher = c_socket.recv(8).decode('UTF-8')
	log("cipher: " + cipher.upper())
	
	#STEP 2 challenge to client
	if not challenge_client(c_socket):
		log("error: incorrect key")
		send_enc("FAIL", c_socket)
		return
	send_enc("PASS", c_socket)
	
	#STEP 3 get command from client
	full_command = recv_enc(c_socket, 32).split(";")
	command = full_command[0]
	filename = full_command[1]
	log("command: " + command + " " + filename)
	
	#execute read command
	if command == "read":
		result = read(c_socket, filename)
	#execute write command
	elif command == "write":
		result = write(c_socket, filename)



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
		
		handle_connection(c_socket)
		log("done")
		print("")
		
		c_socket.close()
	

	
main()

