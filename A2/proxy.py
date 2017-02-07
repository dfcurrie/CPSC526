import socket
import sys
import datetime

logOption = ""
allLogOptions = ["","-raw","-strip","-hex","-auto"]
N = 0

#only call if a logOption is selected besides ""
def logMsg(msg, direction):
	if (logOption == "-raw"):
		#log in raw format
		print("")
	elif (logOption == "-strip"):
		#log after replacing non-printable characters with "."
		print("")
	elif (logOption == "-hex"):
		#logged in hexdump fashion
		print("")
	else:
		#log in N byte chunks WILL NEED TO BE FOUND BEFORE
		
		#write message to file
		#and print the message
		print(direction + message)

#main function to run the program
def main():
	global logOption
	#collect command line arguments
	if (len(sys.argv) == 5):
		logOption = sys.argv[1]
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
		
	#extract N if -autoN is selected
	if ("-auto" in logOption):
		N = int(logOption[5:])
	#else if it's not a valid logOption, quit the program
	elif (logOption not in allLogOptions):
		print("please ensure a valid logOption is entered")
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

  
