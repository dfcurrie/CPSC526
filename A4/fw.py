import fileinput
import os
import sys
import ipaddress

##allowed inputs

MAX_PORT_SIZE = 65535
ALLOWED_FLAG = "established"
ALLOWED_DIRECTION = ["in", "out"]
ALLOWED_ACTION = ["drop", "deny", "accept"]
ALLOWED_WILDCARD = ["*"]

ERROR_FLAG = False
IGNORE = True

#validate if rule is a proper rule
	#takes a list representing a rule [direction, action, ip/mask, [ports], <flag>, line#]
	#returns ERROR_FLAG if not proper else returns True
def validate_rule(rule_list):
	#validate num of arguments
	if len(rule_list) > 6:
		print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1] + "\t- too many arguments")
		return ERROR_FLAG	
	if len(rule_list) < 5:
		print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1][0] + "\t- too few arguments")
		return ERROR_FLAG
			
	#validate if direction is allowed
	if rule_list[0].lower() not in ALLOWED_DIRECTION:
		print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1] + "\t- invalid direction '" + rule_list[0] + "'")
		return ERROR_FLAG
		
	#validate if action is allowed
	if rule_list[1].lower() not in ALLOWED_ACTION:
		print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1] + "\t- invalid action '" + rule_list[1] + "'")
		return ERROR_FLAG
		
	#validate if ip is allowed
	if rule_list[2] not in ALLOWED_WILDCARD:
		try:
			ruleinter = ipaddress.IPv4Interface(rule_list[2])
		except ipaddress.AddressValueError:
			print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1] + "\t- invalid address")
			return ERROR_FLAG
		except ipaddress.NetmaskValueError:
			print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1] + "\t- invalid mask")
			return ERROR_FLAG

	#validate if port is allowed
	for port in rule_list[3]:
		#validate if wildcard
		if port not in ALLOWED_WILDCARD:
			try:
				#validate port number
				if int(port) <= 0 or int(port) > MAX_PORT_SIZE:
					print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1] + "\t- invalid port number '" + port + "'")
					return ERROR_FLAG
			#validate port format (int or not)
			except ValueError:
				print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1] + "\t- invalid port format '" + port + "'")
				return ERROR_FLAG
		
	#validate if 5th element is allowed flag if flag is detected
	if len(rule_list) == 6:
		if rule_list[4].lower() != ALLOWED_FLAG:
			print("ERROR: malformed rule on line #" + rule_list[len(rule_list) - 1] + "\t- invalid flag '" + rule_list[4] + "'")
			return ERROR_FLAG

	#else it is good packet
	return True
	

#validate if packet is a proper packet
	#takes a list representing a packet [direction, ip/mask, ports, flag]
	#returns ERROR_FLAG if not proper else returns True
def validate_packet(packet_list):
	#validate number of arguments
	if len(packet_list) != 4:
		print("ERROR: malformed packet\t\t- incorrect number of arguments")
		return ERROR_FLAG
		
	#validate direction
	elif packet_list[0].lower() not in ALLOWED_DIRECTION:
		print("ERROR: malformed packet\t\t- invalid direction '" + packet_list[0] + "'")
		return ERROR_FLAG
		
	#check ip address	
	try:
		packetip = ipaddress.IPv4Address(packet_list[1])
	except ipaddress.AddressValueError:
		print("ERROR: malformed packet\t\t- invalid ip '" + packet_list[1] + "'")
		return ERROR_FLAG
		
	#validate port
	try:
		#validate port number
		if int(packet_list[2]) <= 0 or int(packet_list[2]) > MAX_PORT_SIZE:
			print("ERROR: malformed packet\t\t- invalid port number '" + packet_list[2] + "'")
			return ERROR_FLAG
	#validate port format (int or not)
	except ValueError:
		print("ERROR: malformed packet\t\t- invalid port format '" + packet_list[2] + "'")
		return ERROR_FLAG
		
	#validate flag
	try:
		#validate flag number
		if int(packet_list[3]) < 0 or int(packet_list[3]) > 1:
			print("ERROR: malformed packet\t\t- invalid flag number '" + packet_list[3] + "'")
			return ERROR_FLAG
	except ValueError:
		print("ERROR: malformed packet\t\t- invalid flag format '" + packet_list[3] + "'")
		return ERROR_FLAG	
		
	return True

	
def fileToList(filename):
	linenum = 1
	IN_LIST = []
	OUT_LIST = []
	if os.path.isfile(filename) and os.path.exists(filename):
		try:
			with open(filename, errors='ignore') as f:
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
						if not IGNORE:
							return ERROR_FLAG
					linenum += 1
			return [IN_LIST,OUT_LIST]
		except UnicodeDecodeError:
			print("ERROR: Unicode decode error prevents rule from being processed")	
			return ERROR_FLAG	
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
		newrule[3] = newrule[3].split(',')
		if validate_rule(newrule) != ERROR_FLAG:
			inlist.append(newrule)
		elif not IGNORE:
			return ERROR_FLAG
	for rule in ruleslist[1]:
		newrule = rule.split()
		newrule[3] = newrule[3].split(',')
		if validate_rule(newrule) != ERROR_FLAG:
			outlist.append(newrule)
		elif not IGNORE:
			return ERROR_FLAG
	fixedlist = [inlist,outlist]
	return fixedlist
	
	
def packetInput(ruleslist):
	try:	
		for line in sys.stdin:
			line = line.strip().lower()
			if line != "":
				packet = line.split()
				if validate_packet(packet) != ERROR_FLAG:
					## IN		
					##validate in rules in ruleslist[0]
					if line.startswith("in"):
						#splits the line into a list
						packetHandler(ruleslist[0],packet,"in")
					## OUT
					##validate in rules in ruleslist[1]
					elif line.startswith("out"):
						#splits the line into a list
						packetHandler(ruleslist[1], packet,"out")
				elif not IGNORE:
					return ERROR_FLAG
	except UnicodeDecodeError:
		print("ERROR: Unicode decode error prevents packets from being processed")	
		if not IGNORE:			
			return ERROR_FLAG
	return
	

def packetHandler(ruleslist, packet, direction):
	rulefound = False
	for rule in ruleslist:
		#handle many ports
		ports = rule[3]
		
		if len(rule) >= 5:
			ipmatch = False
			portmatch = False
			#established set
			if len(rule) == 6:
				estmatch = False
			#established unset
			else:
				estmatch = True
			
			#validate port
			if '*' in ports or packet[2] in ports:
				portmatch = True
				
			#validate ip
			if rule[2] == '*':
				ipmatch = True
			else:
				packetip = ipaddress.IPv4Address(packet[1])
				ruleinter = ipaddress.IPv4Interface(rule[2])
				rulenet = ruleinter.network
				if packetip in rulenet:
					ipmatch = True
			
			#validate flag
			if not estmatch:
				if rule[4] == ALLOWED_FLAG and packet[3] == '1':
					estmatch = True
				
			#if all rules match print responses and break
			if ipmatch and portmatch and estmatch:
				response = rule[1]
				linenum = rule[len(rule) - 1]
				flag = packet[3]
				print("%s(%s) %s %s %s %s"  %   (response,linenum,direction,packet[1],packet[2],flag) )
				rulefound = True
				break
			
		#if rule not found drop
	if rulefound != True:
		print("%s() %s %s %s %s"  %   ("drop",direction,packet[1],packet[2],packet[3]) )
	
	
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
		
		##process each line
		if packetInput(clearedlist) == ERROR_FLAG:
			print("ERROR: Packets could not be processed")
			return
	else:
		print("ERROR: Incorrect number of args provided")
		print("command is:\t 'python fw.py <config_file>")
		
		
##READ THE STDIN LINE BY LINE AND COMPARE TO THE TABLE 

main()
