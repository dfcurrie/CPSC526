import time

nick = "controller"

#send a command to the bots
def send_command:
	continue


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
		print("\tconbot.py <hostname> <port> <channel> <secret-phrase>")
		return
		
	#ensure port is a number
	if !isdigit(sys.argv[2]):
		print("Command argument 2 could not be processed. Command is...")
		print("\tconbot.py <hostname> <port> <channel> <secret-phrase>")
		return
		
	#extract arguments from command line
	hostname = sys.argv[1]
	port = int(sys.argv[2])
	channel = sys.argv[3]
	secret_phrase = sys.argv[4]

main()
