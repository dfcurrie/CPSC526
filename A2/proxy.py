import socket
import sys
import datetime

allLogOptions = ["","-raw","-strip","-hex","-auto"]
N = 0

#only call if a logOption is selected besides ""
def logMsg(logFile, logOption, msg, direction):
	if (logOption == "-raw"):
		#log in raw format
		newlineCount = msg.count("\n")
		formatMsg = direction + msg.replace("\n", "\n" + direction, newlineCount - 1)
	elif (logOption == "-strip"):
		formatMsg = ''.join([i if ord(i) < 128 and ord(i) > 31 else '.' for i in msg])
		formatMsg = direction + formatMsg.replace("\n", "\n" + direction, newlineCount - 1)
		#log after replacing non-printable characters with "."
		print("")
	elif (logOption == "-hex"):
		#logged in hexdump fashion
		print("")
	else:
		#log in N byte chunks WILL NEED TO BE FOUND BEFORE
		print("")
		
	#write message to file
	logFile.write(formatMsg)
	#and print the message
	print(formatMsg)
		
#http://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
def recvall(sock):
    BUFF_SIZE = 4096 # 4 KiB
    data = ""
    while True:
        part = str(sock.recv(BUFF_SIZE), 'utf-8')
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data
#http://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data

#main function to run the program
def main():
	#collect command line arguments
	if (len(sys.argv) == 5):
		logOption = sys.argv[1]
		srcPort = sys.argv[2]
		server = sys.argv[3]
		dstPort = sys.argv[4]
		log = open("log", 'w')
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

	#create server socket to accept client connection
	sSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sSocket.bind((socket.gethostname(), int(srcPort)))
	sSocket.listen(5)
	
	if (logOption != ""):
		log.write("Redirecting packets to " + server + " on port " + dstPort + "\n")
		log.write("Listening at " + socket.gethostbyname(socket.gethostname()) + " on port " + str(srcPort) + "..." + "\n")
	print("Redirecting packets to " + server + " on port " + dstPort)
	print("Listening at " + socket.gethostbyname(socket.gethostname()) + " on port " + str(srcPort) + "...")
	
	#loop to continue to accept connections
	while 1:
		#accept connection from client
		(cSocket, addr) = sSocket.accept()
		conStartTime = datetime.datetime.now()
		if (logOption != ""):
			log.write("connection received from " + str(addr) + " at " + conStartTime.strftime("%Y-%m-%d %H:%M") + "\n")
		print("connection received from " + str(addr) + " at " + conStartTime.strftime("%Y-%m-%d %H:%M"))
		cmd = ""
		while 1:
			fSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			fSocket.connect((server,int(dstPort)))
			cmd = recvall(cSocket)
			if (logOption != ""):
				logMsg(log, logOption, cmd, "--> ")
			else:
				print("--> " + cmd.replace("\n", "\n" + "--> "))
			fSocket.sendall(bytes(cmd, 'utf-8'))
			resp = recvall(fSocket)
			if (logOption != ""):
				logMsg(log, logOption, resp, "<-- ")
			else:
				print("--> " + resp.replace("\n", "\n" + "--> "))
                
			cSocket.sendall(bytes(resp, 'utf-8'))
		
main()

'''
import binascii

def hexa(text):
	
	strlength = len(text)
	outputxt = ""	
	offset = 0	

	while strlength != 0:
		if strlength > 16:
			
			offset += 16
			#get the offset to print
			offsetinhex = hex(offset)[2:]

			#get the first and second parts of the strings and convert to hex			
			firststr = text[offset:offset+8]
			secondstr = text[offset+8:offset+16]
		
			first_hex = str(binascii.hexlify(b(firststr), 'ascii')
						
			first_formatted_hex = " ".join(first_hex[i:i+2] for i in range(0, len(first_hex),2))			

			second_hex = str(binascii.hexlify(b(secondstr)), 'ascii')
			second_formatted_hex = ' '.join(second_hex[i:i+2] for i in range(0, len(second_hex), 2))	
			
			print("%8x %s15  %s15 |%s8%s8|" % (offsetinhex, first_formatted_hex, second_formatted_hex,firststr,secondstr))


			strlength -= 16
		#when you reach the end of the strings and have to deal with the remaing charecters		
		else:
			#get the offset to print
			offsetinhex = hex(offset)[2:]
			
			if strlength > 8:
				#get the first and second parts of the strings and convert to hex			
				firststr = text[offset:offset+8]
				secondstr = text[offset+8:offset+strlength]

				first_hex = str(binascii.hexlify(b(firststr)), 'ascii')
				first_formatted_hex = ' '.join(first_hex[i:i+2] for i in range(0, len(first_hex), 2))			

				second_hex = str(binascii.hexlify(b(secondstr)), 'ascii')
				second_formatted_hex = ' '.join(second_hex[i:i+2] for i in range(0, len(second_hex), 2))				
				print("%8x %s15  %s15 |%s8%s8|" % (offsetinhex, first_formatted_hex, second_formatted_hex,firststr,secondstr))
			else:

				#get the first and second parts of the strings and convert to hex			
				firststr = text[offset:offset+8]

				first_hex = str(binascii.hexlify(b(firststr)), 'ascii')
				first_formatted_hex = ' '.join(first_hex[i:i+2] for i in range(0, len(first_hex), 2))			

				second_formatted_hex = ""			
				print("%8x %s15  %s15 |%s8%s8|" % (offsetinhex, first_formatted_hex, second_formatted_hex,firststr,secondstr))
			strlength = 0

'''
