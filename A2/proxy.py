import select
import socket
import sys
import datetime
import _thread
import string

allLogOptions = ["","-raw","-strip","-hex","-auto"]
N = 0

#-----------------------------------------------------------------------------
#                           AUTO N FUNCTIONS
#-----------------------------------------------------------------------------
#processes N bytes 
def filterNBytes(text):
	msg = ""
	for ch in text:
		chValue = ord(ch)
		#backslash
		if chValue == 92:
			msg +="\\"
		#tab
		elif chValue == 9:
			msg +="\\t"
		#newline
		elif chValue == 10:
			msg +="\\n"
		#car return
		elif chValue == 13:
			msg +="\\r"
		#32 to 127
		elif ((chValue >= 32) and (chValue <= 127)):  
			msg += ch
		#print hex value
		else:
			msg += "\\"
			hexValue = hex(ord(ch))
			msg += hexValue[2:]
			
	msg += ("\n")
	return	msg

#processes message into N byte segments
def autoN(text,n):
	strLength = len(text)
	offset = 0	
	outputtxt= ""
	#while the offset is less than the end of string continue processing
	while offset <= strLength:
		#get the next up to N bytes to process
		unfilteredstr = text[offset:min(offset+n,strLength-1)]
		outputtxt += filterNBytes(unfilteredstr) 
		offset += n
	return outputtxt
	

#-----------------------------------------------------------------------------
#                           HEXDUMP FUNCTIONS
#-----------------------------------------------------------------------------
#converts chunk of string char by char to a Hex format
#ie AABBCCDD becomes 
#41 41 42 42 43 43 44 44 
def texttohex(text):
	hextxt = ""
	for ch in text:
		HEX = hex(ord(ch))
		HEX += " "
		hextxt += HEX[2:]
	
	hextxt = hextxt[:-1]
	return	hextxt

#takes in string and formats it to the hexdump format
def hexa(text):
	strLength = len(text)
	outputxt = ""	
	offset = 0	
	#while there are characters still in the string
	while offset <= strLength:
		#get the first and second parts of the strings padded	
		if (offset + 8) <= (strLength - 1):
			firststr = text[offset:offset+8].ljust(8)
			secondstr = text[offset+8:min(offset+16, strLength-1)].ljust(8)
		else:
			firststr = text[offset:(strLength - 1)].ljust(8)
			secondstr = "".ljust(8)
		
		#get the strings in hex format
		first_formatted_hex = texttohex(firststr).ljust(23)
		second_formatted_hex = texttohex(secondstr).ljust(23)
		
		#update offsets
		offset += 16
		offsetindex = hex(offset)
		offsetindex = offsetindex[2:].zfill(8)
		
		#add line to output
		outputxt += "%s  %s  %s  |%s%s|\n" % (offsetindex, first_formatted_hex, second_formatted_hex,firststr,secondstr)
	return outputxt
	

#-----------------------------------------------------------------------------
#                           LOGGING 
#-----------------------------------------------------------------------------	
#only call if a logOption is selected besides ""
def logMsg(logOption, msg, direction):
	msg = str(msg.decode('utf-8', 'ignore'))
	#log in raw mode
	if (logOption == "-raw"):
		#nothing needs to be done
		pass
	#log in strip mode
	elif (logOption == "-strip"):
		#replace non-printable characters with '.'
		msg = ''.join([i if ord(i) < 128 and ord(i) > 31 else '.' for i in msg])
	#log in hex mode
	elif (logOption == "-hex"):
		#logged in hexdump fashion
		msg = ''.join([i if ord(i) < 128 and ord(i) > 31 else '' for i in msg])
		msg = hexa(msg)
	#log in auntoN mode
	else:
		msg = autoN(msg,N)
	newlineCount = msg.count("\n")
	formatMsg = direction + msg.replace("\n", "\n" + direction, newlineCount - 1)
	#and print the message
	print(formatMsg)
	
#-----------------------------------------------------------------------------
#                           COMMUNICATION FUNCTIONS
#-----------------------------------------------------------------------------
def recvall(sock):
	BUFF_SIZE = 4096 # 4 KiB
	data = []
	part = sock.recv(BUFF_SIZE)
	data.append(part)
	return b''.join(data)

def handleConnection(cSocket, fSocket, logOption):
	while 1:
		cmd = recvall(cSocket)
		if len(cmd) == 0:
			break
		if (logOption != ""):
			logMsg(logOption, cmd, "--> ")
		fSocket.sendall(cmd)
		resp = recvall(fSocket)
		if len(resp) == 0:
			break
		if (logOption != ""):
			logMsg(logOption, resp, "<-- ")
		cSocket.sendall(resp)
	print("Connection closed.") 	
	cSocket.close()
	fSocket.close()

	
#-----------------------------------------------------------------------------
#                              MAIN
#-----------------------------------------------------------------------------
#main function to run the program
def main():
	#collect command line arguments
	if (len(sys.argv) >= 5):
		logOption = sys.argv[1]
		srcPort = sys.argv[2]
		server = sys.argv[3]
		dstPort = sys.argv[4]
	elif (len(sys.argv) == 4):
		logOption = ""
		srcPort = sys.argv[1]
		server = sys.argv[2]
		dstPort = sys.argv[3]
	#if error in arguments, stop the program
	else:
		print("command is:\n\t'python proxy.py [logOptions] srcPort server dstPort'")
		quit()
		
	#extract N if -autoN is selected
	if ("-auto" in logOption):
		global N
		N = int(logOption[5:])
	#else if it's not a valid logOption, quit the program
	elif (logOption not in allLogOptions):
		print("please ensure a valid logOption is entered")
		quit()
		
	#make a server socket to listen to incoming messages
	sSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sSocket.bind((socket.gethostname(), int(srcPort)))
	sSocket.listen(5)
	print("Port logger running on " + socket.gethostname() + ": srcPort=" + srcPort  + " host=" + server + " dstPort=" + dstPort)
	
	#loop to accept connections and spawn handler threads
	while 1:
		(cSocket, addr) = sSocket.accept()
		conStartTime = datetime.datetime.now()
		print("New connection: " + conStartTime.strftime("%Y-%m-%d %H:%M")	+ ", from " + str(addr))
		fSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		fSocket.connect((server,int(dstPort)))
	
		#create new thread to handle connection between fScocket and cSocket
		_thread.start_new_thread(handleConnection, (cSocket, fSocket, logOption))

main()
