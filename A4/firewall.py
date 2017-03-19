import fileinput

##allowed inputs
ALLOWED_DIRECTION_IN = ["in","IN","In"]
ALLOWED_DIRECTION_OUT = ["out","OUT","Out"]

MAX_PORT_SIZE = 65535
ALLOWED_RESPONSE_A = ["accept","ACCEPT","Accept"]
ALLOWED_RESPONSE_D = ["deny","DENY","Deny"]
ALLOWED_RESPONSE_DR = ["drop","DROP","Drop"]
ALLOWED_FLAG = "established"


def fileToArray(filename):
	with open(filename) as f:
		for line in f:
			
		
#main
def main():

	##READ THE CONFIG FILE
	##STORE THE RULES
	if len(sys.argv) == 1:
	filename = sys.argv[1]
	rulelist = fileToArray(filename)

else:
	print("ERROR: Incorrect Args should be a file")


##READ THE STDIN LINE BY LINE AND COMPARE TO THE TABLE 
	
main()

