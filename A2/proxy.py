import socket
import sys
import datetime

#main function to run the program
def main():
	if (len(sys.argv) == 5):
		logOptions = sys.argv[1]
		srcPort = sys.argv[2]
		server = sys.argv[3]
		dstPort = sys.argv[4]
	elif (len(sys.argv) == 4):
		srcPort = sys.argv[1]
		server = sys.argv[2]
		dstPort = sys.argv[3]
	else:
		print("command is:\n\t'python proxy.py [logOptions] srcPort server dstPort'")
		quit()

	sSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sSocket.bind((socket.gethostname(), int(srcPort)))
	sSocket.listen(0)
	print("Redirecting packets to " + server + " on port " + dstPort)
	print("Listening at " + socket.gethostbyname(socket.gethostname()) + " on port " + str(srcPort) + "...")

	#loop to continue to accept connections
	while 1:
		(cSocket, addr) = sSocket.accept()
		conStartTime = datetime.datetime.now()
		print("connection received from " + str(addr) + " at " + conStartTime.strftime("%Y-%m-%d %H:%M"))
		cmd = (str(cSocket.recv(64), 'utf-8')).rstrip()
		while (cmd != "exit"):
			#loop to accept commands from user
			cmd = (str(cSocket.recv(64), 'utf-8')).rstrip()
		
main()

  
