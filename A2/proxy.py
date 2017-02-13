import select
import socket
import sys
import datetime
import _thread
import string

allLogOptions = ["","-raw","-strip","-hex","-auto"]
N = 0

def textfilter(text):
	hextxt = ""
	for i in range(0,len(text)):
		hexa = text[i]
		avalue = ord(hexa)
		
		#backslash
		if avalue == 92:
			hextxt +="\\"
		#tab
		elif avalue == 9:
			hextxt +="\\t"
		#newline
		elif avalue == 10:
			hextxt +="\\n"
		#car return
		elif avalue == 13:
			hextxt +="\\r"
		#32 to 127
		elif ((avalue >= 32) and (avalue <= 127)):  
			hextxt += hexa
		#print hex value
		else:
			hextxt += "\\"
			HEX = hex( ord(hexa))
			hextxt += HEX[2:]
			
	hextxt += ("\n")
	return	hextxt

def autoN(text,n):
	
	strlength = len(text)
	bytesize = n	
	offset = 0	
	outputtxt= ""
	while strlength != 0:
		if strlength > n:
			
			#byte by byte			
			unfilteredstr = text[offset:offset+n]
			
			outputtxt += textfilter(unfilteredstr) 

			offset += n
			strlength -= n
		#when you reach the end of the strings and have to deal with the remaing charecters		
		else:

			unfilteredstr = text[offset:]
			outputtxt += textfilter(unfilteredstr) 

			strlength = 0
	return outputtxt
	

#converts strings char by char to a Hex format
#ie AABBCCDD becomes 
#41 41 42 42 43 43 44 44 
def texttohex(text):
	hextxt = ""
	for i in range(0,len(text)):
		hexa = text[i]
		HEX = hex( ord(hexa))
		HEX += " "
		hextxt += HEX[2:]
	
	hextxt = hextxt[:-1]
	return	hextxt

##takes in string and formats it to the hexdump format
def hexa(text):
	strlength = len(text)
	outputxt = ""	
	offset = 0	

	while strlength != 0:
		if strlength > 16:
			
			#get the first and second parts of the strings and convert to hex			
			firststr = text[offset:offset+8]
			secondstr = text[offset+8:offset+16]
		
			first_formatted_hex = texttohex(firststr)
			second_formatted_hex = texttohex(secondstr)
			
			offset += 16
			#get the offset to print
			offsetindex = hex(offset)
			offsetindex = offsetindex[2:].zfill(8)		

			outputxt += "\n%s  %s  %s  |%s%s|" % (offsetindex, first_formatted_hex, second_formatted_hex,firststr,secondstr)

			strlength -= 16

		#when you reach the end of the strings and have to deal with the remaing charecters		
		else:
		
			if strlength > 8:
				#get the first and second parts of the strings and convert to hex			
				firststr = text[offset:offset+8]
				secondstr = text[offset+8:offset+strlength]
				
				#formats to the strings to have a length 16 chars
				secondstr = secondstr.ljust(8)

				#converts the text for the strings to there hex values
				#and pads the hexvalues to have length 23
				first_formatted_hex = texttohex(firststr)
				second_formatted_hex = texttohex(secondstr)
				second_formatted_hex = second_formatted_hex.ljust(23)	
				
				#Offset part calcs offset
				offset += strlength
				#converts to hex and pads
				offsetindex = hex(offset)
				offsetindex = offsetindex[2:].zfill(8)

				outputxt += "\n%s  %s  %s  |%s%s|"  % (offsetindex, first_formatted_hex, second_formatted_hex,firststr,secondstr)
			else:

				#get the first and second parts of the strings and convert to hex			
				firststr = text[offset:offset+8]
				
				#formats to the strings to have a length 16 chars
				firststr = firststr.ljust(8)				
				secondstr = secondstr.ljust(8)

				#pads the hexvalues to have length 23
				first_formatted_hex = texttohex(firststr)
				first_formatted_hex = first_formatted_hex.ljust(23)		
				
				second_formatted_hex = ""
				second_formatted_hex = second_formatted_hex.ljust(23)

				#Offset part calcs offset
				offset += strlength

				#converts to hex and pads
				offsetindex = hex(offset)
				offsetindex = offsetindex[2:].zfill(8)
			
				outputxt += ("\n%s  %s  %s  |%s%s|"  % (offsetindex, first_formatted_hex, second_formatted_hex,firststr,secondstr))

			#make sure it ends jsut in casehe
			strlength = 0
	return outputxt
			
			
#only call if a logOption is selected besides ""
def logMsg(logOption, msg, direction):
	msg = str(msg.decode())
	if (logOption == "-raw"):
		#nothing needs to be done
		pass
	elif (logOption == "-strip"):
		#replace non-printable characters with '.'
		msg = ''.join([i if ord(i) < 128 and ord(i) > 31 else '.' for i in msg])
	elif (logOption == "-hex"):
		#logged in hexdump fashion
		msg = ''.join([i if ord(i) < 128 and ord(i) > 31 else '' for i in msg])
		msg = hexa(msg)
	else:
		msg = autoN(msg,N)
	newlineCount = msg.count("\n")
	formatMsg = direction + msg.replace("\n", "\n" + direction, newlineCount - 1)
	#and print the message
	print(formatMsg)
		
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
		
	sSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sSocket.bind((socket.gethostname(), int(srcPort)))
	sSocket.listen(5)
	
	print("Port logger running on " + socket.gethostname() + ": srcPort=" + srcPort  + " host=" + server + " dstPort=" + dstPort)
	while 1:
		(cSocket, addr) = sSocket.accept()
		conStartTime = datetime.datetime.now()
		print("New connection: " + conStartTime.strftime("%Y-%m-%d %H:%M")	+ ", from " + str(addr))
		fSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		fSocket.connect((server,int(dstPort)))
	
		#create new thread to handle connection between fScocket and cSocket
		_thread.start_new_thread(handleConnection, (cSocket, fSocket, logOption))

main()
