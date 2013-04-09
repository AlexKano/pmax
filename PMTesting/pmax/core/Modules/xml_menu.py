import re
import time
import sys
from navigator import read 
from navigator import send_key 
from xml.dom.minidom import Document

def get_value_type():
	special_end_char="\xff"
	param_name = read()
	skipped_submenu_p1 = ("NEW INST. CODE","RECORD SPEECH","ENROLL  KEYFOB","ENROLL PROX TAG","SET DATE &FORMAT","SET TIME &FORMAT","2.ENROLLING",
							"3.DEFINE ZONES","8.DEFINE OUTPUTS","14.START UL/DL","12.FACTORY DEFLT", "13.SERIAL NUMBER","LAN SETTINGS","WL SENSORS TEST",
							"WL KEYPADS TEST", "GPRS CONN. TEST", "LAN CONNECT.TEST","LAN RESET OPTION")
	skipped_submenu_p2 = ("SCHEDULER", "DEFINE OUTPUTS", "FACTORY DEFLT", "SERIAL NUMBER", "START UL/DL","ZONES/DEVICES","DIAGNOSTICS","KEYFOBS","10:PIEZO  BEEPS")
	skipped_submenu = skipped_submenu_p1 + skipped_submenu_p2
	if param_name in skipped_submenu: return "notype",None
	send_key("ok")
	param_value = read()
	if(param_value[-1:] == special_end_char):
		value_list = [param_value[:-1].strip()]
		while  True:
			send_key("next")
			s = read()		
			if s==param_value:break
			value_list.append(s)
		send_key("home")
		return ("list",value_list)
	send_key("off")
	default = read()
	if default == "000.000.000.000\x00":
		send_key("home")
		return ("ip",None)
	if default=="":
		send_key("8")
		test1 = read()
		if test1=="8":
			send_key("home")
			return ("numeric",None)
		send_key("8")
		test2 = read()
		send_key("8")
		test3 = read()
		send_key("home")		
		if test1  == 'a' and test2 == 'b' and test3 == 'c':
			return ("text",None)
		return ("error",None)
	extracted = re.match('(.*) ([0-9]{2}):([0-9]{2})([A|P]?)',param_value)
	if not extracted == None:
		mode = extracted.group(4)
		hours = int(extracted.group(2))
		minuts = int(extracted.group(3))
		if ((mode == '' and hours<=24)or(not mode == '' and hours<=12))and minuts<60:
			send_key("home")		
			return ('time',None)
	for c in '0123456789':
		if not c in default:break
	send_key(c)
	new_value = read()
	if new_value == default:
		send_key("home")
		return ("subnode",None)
	for i in range(len(new_value)):
		if default[:i]+c+default[i+1:] == new_value:
			send_key("home")
			value_len =len(default)-i
			return ("special",value_len)
	send_key("home")
	return ("unknown",None)
	
def process_menu(menu):
	if not menu[0] in '0123456789':return ''
	for c in menu:
		if not c in '0123456789': return c
	return ''

def correct_menu(menu,limiter):
	pos = menu.find(limiter)
	if pos == -1: return menu
	return menu[pos+1:]
	
	
def menu_block(parent,doc):
    curr = start = read()
    pos=0
    limiter = process_menu(start)
    while 1:
        tmp_limiter = process_menu(curr)
        if not tmp_limiter == limiter: limiter=""
        writeXMLelement(parent,doc,pos)
        send_key("next")
        pos+=1
        curr = read()
        if curr == start or curr == "<OK> TO EXIT" : 
            print "CUR. %s" % curr
            print "START %s" % start
            print "FINISH"
            break
        #break
    if not limiter=="":
        for child in parent.childNodes:
            child.setAttribute("name",correct_menu(child.getAttribute('name'),limiter))


def writeXMLelement(parent,doc,index):
	tagname = read()
	val_type,values = get_value_type()
	if val_type == "subnode":
		node = doc.createElement('node')
		parent.appendChild(node)
		node.setAttribute("name",tagname)
		node.setAttribute("index","%s" % index)
		send_key("ok")
		menu_block(node,doc)
		send_key("home")
	else:
		node = doc.createElement('param')
		parent.appendChild(node)
		node.setAttribute("name",tagname)
		node.setAttribute("index","%s" % index)
		node.setAttribute("type",val_type)
		if val_type == 'list':
			values_list = doc.createElement('values_list')
			node.appendChild(values_list)
			i = 0
			for l in values:
				v = doc.createElement('value')
				v.setAttribute("id","%s" % i)
				i+=1
				v.setAttribute("name",l)
				values_list.appendChild(v)

class BadXML(Exception):pass

xmls = []
#send_key('next')
#print read()
#exit()

try:
#	for i in range(10):
		print read()
		doc = Document()
#		sys.stdin.readline()
		submenu = doc.createElement("submenu")
		doc.appendChild(submenu)
		menu_block(submenu,doc)
#		send_key('next')
		xmls.append(doc.toxml)
#		if not xmls[i] == xmls[0]: raise BadXML()
#except:
except KeyboardInterrupt:
	print "CYCLE %d FAILED" % i

f = open("menu_py.xml","w")
f.write(doc.toxml())

exit()
