#https://docs.python.org/2/howto/sockets.html

import socket
import sys

try:
	port = int(sys.argv[1])
except:
	print("Please ensure run command is 'python bServer.py port##'")
	quit()


sSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
sSocket.bind((socket.gethostname(), port))
sSocket.listen(0)
print("Listening at " + socket.gethostname() + " on port " + str(port) + "...")

#loop to continue to accept connections
while 1:
	(cSocket, addr) = sSocket.accept()
	print("connection received from " + str(addr))
	cmd = ""
	while cmd != "exit":
		cmd = (cSocket.recv(32)).rstrip();
		print("received command '" + cmd + "'")
		cSocket.send("\n")
		
	cSocket.close()
	print("connection to " + str(addr) + " was closed")
		
