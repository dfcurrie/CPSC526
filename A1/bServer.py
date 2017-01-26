#https://docs.python.org/2/howto/sockets.html

import socket
import sys
import subprocess

#all proper commands
correctCmd = ["pwd", "cd", "ls", "cat", "help", "off"]

#runs a command
def runCmd(cmd):
	if (cmd.split())[0] in correctCmd:									#ensures command is allowed
		if cmd == "help":																	#special case for 'help'
			result = "possible commands:\n"
			for i in correctCmd:
				result = result + "\t" + i
			result = result + "\n"
		elif cmd == "off":																#special case for 'off'
			quit()
		else:																							#else attempts to run command
			try:
				result = subprocess.check_output(["/bin/" + cmd])
				result = result.decode('utf-8')
			except subprocess.CalledProcessError:
				result = "command '" + cmd + " could not be run successfully"
			
	else:
		result = "command not in list of valid commands\n"
		
	return result



def main():
	try:
		port = int(sys.argv[1])
	except:
		print("Please ensure run command is 'python bServer.py port##'")
		quit()

	sSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
	sSocket.bind((socket.gethostname(), port))
	sSocket.listen(0)
	print("Listening at " + socket.gethostname() + " on port " + str(port) + "...")

	#loop to continue to accept connections
	while 1:
		(cSocket, addr) = sSocket.accept()
		print("connection received from " + str(addr))
		print("sending challenge...")
		cSocket.send("password?\n")
		cmd = (cSocket.recv(32)).rstrip();
		if cmd != "password":
			cSocket.send("Denied. Closing coneection...")
			cSocket.close()
			quit()
		
		cSocket.send("correct password received\nPlease enter a command\n")
		
		while cmd != "exit":
			cmd = (cSocket.recv(32)).rstrip();
			print("received command '" + cmd + "'")
			res = runCmd(cmd)
			cSocket.send(res)
			
		cSocket.close()
		print("connection to " + str(addr) + " was closed")
		
		
main()

  
