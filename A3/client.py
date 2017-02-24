import select
import socket
import sys
import datetime
import _thread
import string

#TO DO
def read(c_socket):
	print("read")
	
	
	
#TO DO
def write(c_socket, filename):
	print("write")
	
	

#handles connection with serer from beginning to end
def handle_connection(c_socket, command, filename, cipher, key):
	#STEP 1 send cipher
	c_socket.sendall(cipher.encode('UTF-8'))
	
	#STEP 2 challenge from server
	challenge = (c_socket.recv(32)).decode('UTF-8')
	#decrypt with key TO DO
	response = challenge
	#send decrypted message
	c_socket.sendall(response.encode('UTF-8'))
	#receive reult of challenge
	if c_socket.recv(4).decode('UTF-8') == "FAIL":
		print("Error: mismatching keys used")
		return
	
	#STEP 3 send command
	c_socket.sendall((command + ";" + filename).encode('UTF-8'))
	
	#execute read command
	if command == "read":
		read(c_socket)
	#execute write command
	elif command == "write":
		write(c_socket, filename)
 
 
 
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

