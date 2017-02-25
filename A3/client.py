import select
import socket
import sys
import datetime
import _thread
import string

#sebds data encrypted TO DO
def send_enc(msg, c_socket):
	c_socket.sendall(msg.encode('UTF-8'))
	

	
#receive encrypted data TO DO
def recv_enc(c_socket, num_bytes):
	return c_socket.recv(num_bytes).decode('UTF-8')
	
	
	
#communicates with server in read mode
def read(c_socket):
	if recv_enc(c_socket, 4) == "FAIL":
		print("error: server could not find file")
		return
	file_size = int(recv_enc(c_socket, 4))
	while file_size > 0:
		msg = recv_enc(c_socket, 1024)
		print(msg, end='')
		file_size = file_size - 1024
	
	
	
#TO DO
def write(c_socket):
	print("write")
	
	

#handles connection with serer from beginning to end
def handle_connection(c_socket, command, filename, cipher, key):
	#STEP 1 send cipher
	c_socket.sendall(cipher.encode('UTF-8'))
	
	#STEP 2 challenge from server
	challenge = recv_enc(c_socket, 8)
	#decrypt with key TO DO
	response = challenge 
	#send re-encrypted message with padding
	send_enc(response + "AAAAAAAA", c_socket)
	#receive reult of challenge
	if recv_enc(c_socket, 4) == "FAIL":
		print("Error: mismatching keys used")
		return
	
	#STEP 3 send command
	send_enc((command + ";" + filename), c_socket)
	
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
		cipher = sys.arg[4]
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

