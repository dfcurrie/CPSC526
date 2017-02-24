import random
import socket
import sys
import os.path
import datetime
import string

#helper function for standardized logging to stdout
def log(msg):
	print((datetime.datetime.now()).strftime("%H:%M:%S") + ": " + msg)

	
	
#sends challenge to client
def challenge_client(c_socket):
	challenge = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))
	
	#encrypt using key TO DO
	enc_challenge = challenge
	
	c_socket.sendall(enc_challenge.encode('UTF-8'))
	response = (c_socket.recv(32)).decode('UTF-8')
	
	return challenge == response
	
	
	
#read file for and send to client
def read(c_socket, filename):
	#check file exists
	if not os.path.isfile(filename):
		error_msg = "error: no file named '" + filename + "'"
		log(error_msg)
		#c_socket.sendall(error_msg.encode('UTF-8'))
		return
		
	#read file and send encrypted to client TO DO
	
	
	
#write file from client
def write(c_socket, filename):
	#"recvall", and unencrypt TO DO
	
	try:
		#write the file TO DO
		print("")
	except:
		error_msg = "error: file is not writable"
		log(error_msg)
		#c_socket.sendall(error_msg.encode('UTF-8'))
		return
	
	
	
#handles client connections from start to finish
def handle_connection(c_socket):
	#STEP 1 cipher establishment
	cipher = (c_socket.recv(8)).decode('UTF-8')
	log("cipher: " + cipher.upper())
	
	#STEP 2 challenge to client
	if not challenge_client(c_socket):
		log("error: incorrect key")
		c_socket.sendall("FAIL".encode('UTF-8'))
		return
	c_socket.sendall("PASS".encode('UTF-8'))
	
	#STEP 3 get command from client
	full_command = (c_socket.recv(32)).decode('UTF-8').split(";")
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

