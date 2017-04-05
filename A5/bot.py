import time

ERROR_FLAG = -1

nick = "V"
atk_cnt = 0

#receive a command from the controller
def rcv_command():
	continue


#return a message to the controller
def return_msg(msg):
	continue


#handle the connection to the IRC server
def handle_connection():
	return ERROR_FLAG

#connect to the specified IRC server and channel
def connect():
	continue
	

#main
def main():

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
	if !isdigit(sys.argv[2]):
		print("Command argument 2 could not be processed. Command is...")
		print("\tbot.py <hostname> <port> <channel> <secret-phrase>")
		return
		
	#extract arguments from command line
	hostname = sys.argv[1]
	port = int(sys.argv[2])
	channel = sys.argv[3]
	secret_phrase = sys.argv[4]
	
	while true:
		#connect to the IRC server
		connect()
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
