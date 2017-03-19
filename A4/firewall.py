import fileinput
import sys

##allowed inputs

MAX_PORT_SIZE = 65535
ALLOWED_RESPONSE_A = ["accept","ACCEPT","Accept"]
ALLOWED_RESPONSE_D = ["deny","DENY","Deny"]
ALLOWED_RESPONSE_DR = ["drop","DROP","Drop"]
ALLOWED_FLAG = "established"


def fileToList(filename):

	linenum = 1
	IN_LIST = []
	OUT_LIST = []
	with open(filename) as f:
		for line in f:
			line = line.strip().lower()
			if line.startswith("in"):
				IN_LIST.append(line+" "+str(linenum))

			elif line.startswith("out"):
				OUT_LIST.append(line+" "+str(linenum))
			 
			##do nuffin
			linenum += 1

	return [IN_LIST,OUT_LIST]

			

##converts each section of the string into a element in a list
#ie "in 136.159.5.5 22 0" 
#becomes
#	['in', '136.159.5.5', '22']
##list within lists
def strlisttolist(ruleslist):
	inlist = []
	outlist = []
	for rule in ruleslist[0]:
		newrule = rule.split()
		inlist.append(newrule)
	for rule in ruleslist[1]:
		newrule = rule.split()
		inlist.append(newrule)
	fixedlist = [inlist,outlist]
	return fixedlist
	
	
	
def pancakeInput(ruleslist):
	for line in sys.stdin:
		line = line.strip().lower()
		
		## IN		
		##check in rules in ruleslist[0]
		if line.startswith("in"):
			#splits the line into a list
			packet = line.split()
			packetHandler(ruleslist[0],packet)
			print("in")
		## OUT
		##check in rules in ruleslist[1]
		elif line.startswith("out"):
			#splits the line into a list
			packet = line.split()
			packetHandler(ruleslist[1], packet)
			print("out")
			
def packetHandler(rules, packet):
	for rule in rules
		#if rule met break
			
			
			
			#set rule found to true
		
		#if rule not found drop
	
#main
def main():

	##READ THE CONFIG FILE
	##STORE THE RULES
	if len(sys.argv) == 2:
		filename = sys.argv[1]
		#list in the format [INLIST,OUTLIST]
		#where INLIST and OUTLIST contain a list of strings
		ruleslist = fileToList(filename)
		print(ruleslist)
		#Changes the contents of rules list from strings to list of smaller strings
		clearedlist = strlisttolist(ruleslist)
		print(clearedlist)
		##process each line
		pancakeInput(clearedlist)
	
	else:
		print("ERROR: Incorrect Args should be a file")


##READ THE STDIN LINE BY LINE AND COMPARE TO THE TABLE 
	
main()

