import fileinput
import os
import sys
import ipaddress

##allowed inputs

MAX_PORT_SIZE = 65535
ALLOWED_RESPONSE_A = ["accept","ACCEPT","Accept"]
ALLOWED_RESPONSE_D = ["deny","DENY","Deny"]
ALLOWED_RESPONSE_DR = ["drop","DROP","Drop"]

ALLOWED_FLAG = "established"
ALLOWED_DIRECTION = ["in", "out"]
ALLOWED_ACTION = ["drop", "deny", "accept"]
ALLOWED_WILDCARD = ["*"]

ERROR_FLAG = "ERROR"

#check if rule is a proper rule
def check_rule(rule_list):
	#check num of arguments
	if len(rule_list) > 6 or len(rule_list) < 5:
		print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1] + " - incorrect number of arguments")
		return ERROR_FLAG
			
	#check if direction is allowed
	elif rule_list[0].lower() not in ALLOWED_DIRECTION:
		print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1] + " - invalid direction '" + rule_list[0] + "'")
		return ERROR_FLAG
		
	#check if action is allowed
	elif rule_list[1].lower() not in ALLOWED_ACTION:
		print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1] + " - invalid action '" + rule_list[1] + "'")
		return ERROR_FLAG
		
	#check if ip is allowed
#	elif rule_list[2] of proper ip mask format:
#		print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1] + " - invalid ip '" + rule_list[2] + "'")
#		return ERROR_FLAG		

	#check if port is allowed
#	elif rule_list[3] not in ALLOWED_WILDCARD and of proper port format:
#		print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1] + " - invalid action '" + rule_list[1] + "'")
#		return ERROR_FLAG
		
	#check if 5th element is allowed flag if flag is detected
	elif len(rule_list) == 6:
		if rule_list[4].lower() != ALLOWED_FLAG:
			print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1] + " - invalid flag '" + rule_list[4] + "'")
			return ERROR_FLAG

	#else it is good packet
	else:
		return True


def fileToList(filename):
	linenum = 1
	IN_LIST = []
	OUT_LIST = []
	if os.path.isfile(filename) and os.path.exists(filename):
		
		with open(filename) as f:
			for line in f:
				line = line.strip().lower()
				if line.startswith("in"):
					IN_LIST.append(line+" "+str(linenum))
				elif line.startswith("out"):
					OUT_LIST.append(line+" "+str(linenum))
				elif line.startswith("#") or line == "":
					pass
				else:
					print("ERROR: line #" + str(linenum) + " is invalid")
					#return ERROR_FLAG
				linenum += 1
		return [IN_LIST,OUT_LIST]
		
	else:
		print("ERROR: File does not exist")
		return ERROR_FLAG


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
		if check_rule(newrule) != ERROR_FLAG:
			inlist.append(newrule)
		#else:
		#	return ERROR_FLAG
	for rule in ruleslist[1]:
		newrule = rule.split()
		if check_rule(newrule) != ERROR_FLAG:
			outlist.append(newrule)
		#else:
		#	return ERROR_FLAG
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
			packetHandler(ruleslist[0],packet,"in")
		## OUT
		##check in rules in ruleslist[1]
		elif line.startswith("out"):
			#splits the line into a list
			packet = line.split()
			packetHandler(ruleslist[1], packet,"out")
			
def packetHandler(ruleslist, packet, direction):
	rulefound = False
	for rule in ruleslist:
		#handle many ports
		ports = rule[3].split(',')
		#if established isn't it
		if len(rule) == 5:
			ipmatch = False
			portmatch = False
			#check port
			if rule[3] == '*':
				portmatch = True
			elif packet[2] in ports :
				portmatch = True
			
			#check ip
			if rule[2] == '*':
				ipmatch = True
			else:
				packetip = ipaddress.IPv4Address(packet[1])
				ruleinter = ipaddress.IPv4Interface(rule[2])
				rulenet = ruleinter.network
			
				if packetip in rulenet:
					ipmatch = True
			
			
			#if all rules match print responses and break
			if ipmatch and portmatch:
				response = rule[1]
				linenum = rule[4]
				print("%s(%s) %s %s %s 0"  %   (response,linenum,direction,packet[1],packet[2]) )
				rulefound = True
				break
			
			#if rule found set it to true
		
		
		#if established is possibly in it
		elif len(rule) == 6:
			ipmatch = False
			portmatch = False
			estmatch= False
			#check port
			if rule[3] == '*':
				portmatch = True
			elif packet[2] in ports:
				portmatch = True
			#check ip
			
			if rule[2] == '*':
				ipmatch = True
			else:
				packetip = ipaddress.IPv4Address(packet[1])
				ruleinter = ipaddress.IPv4Interface(rule[2])
				rulenet = ruleinter.network
			
				if packetip in rulenet:
					ipmatch = True
			
			
			if rule[5] == "established" and packet[3] == '1':
				estmatch = True
				
			#if all rules match print responses and break
			if ipmatch and portmatch and estmatch:
				response = rule[1]
				linenum = rule[4]
				print("%s(%s) %s %s %s 1"  %   (response,linenum,direction,packet[1],packet[2]) )
				rulefound = True
				break
			
		#if rule not found drop
	if rulefound != True:
		print("%s() %s %s %s 1"  %   ("drop",direction,packet[1],packet[2]) )
	
#main
def main():

	##READ THE CONFIG FILE
	##STORE THE RULES
	if len(sys.argv) == 2:
		filename = sys.argv[1]
		#list in the format [INLIST,OUTLIST]
		#where INLIST and OUTLIST contain a list of strings
		ruleslist = fileToList(filename)
		if ruleslist == ERROR_FLAG:
			print("ERROR: Configuration file could not be read")
			return
		
		#Changes the contents of rules list from strings to list of smaller strings
		clearedlist = strlisttolist(ruleslist)
		if clearedlist == ERROR_FLAG:
			print("ERROR: Rules could not be processed")
			return
			
		print("Rules we are working with FOR in")
		
		print(clearedlist[0])
		
		print("Rules we are working with FOR out")
		
		print(clearedlist[1])
		
		##process each line
		pancakeInput(clearedlist)
	
	else:
		print("ERROR: Incorrect number of args provided")
		print("command is:\t 'python fw.py <config_file>")
		
		
##READ THE STDIN LINE BY LINE AND COMPARE TO THE TABLE 

main()