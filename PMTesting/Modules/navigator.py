import devices,time,sys
import logging
import out
import os
import paramiko
import select
import com
import serial
SEPARATOR = "\\"
PYTHON = ""
if (os.name == "posix"):
	SEPARATOR = "/"
	PYTHON = "python "

def ConvertTo4Digits(code):
	char_code = str(code)
	#print char_code
	if len (char_code) < 4:
		char_code = "0" + char_code
	#print char_code	
	if len (char_code) < 4:
		char_code = "0" + char_code
	#print char_code	
	if len (char_code) < 4:
		char_code = "0" + char_code
	return char_code
	
def read1():
	#while 1:
	#	try:
			data_size = devices.s.inWaiting()
			devices.s.read(data_size)
			data = devices.make_packet(0xF2,3,'')
			devices.s.write(data)
			#p = devices.wait(1,0.5)
			p = devices.wait(1)
			#return p.data
			return (p.data).strip()
	#	except Exception,err:
	#		out.prnt( str(err))
	#		out.prnt ("exceptiont (read()) error")
	#		devices.OpenCloseComPort()

def sshlogin(ip = "212.90.164.4", pasword1 = "visonic",command ="tail -n 10 -f /var/log/messages" ):
	
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	#op.load_system_host_keys()
	ssh.connect(ip, username='root',password=pasword1)
	ssh.exec_command('s')
	ssh.exec_command('l')
	ssh.exec_command('visonic')
	transport = ssh.get_transport()
	channel = transport.open_session()
	channel.exec_command(command)	
	print command
	return channel,ssh
def ssh_login(ip = "212.90.164.4", pasword1 = "visonic"):
	
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	#op.load_system_host_keys()
	ssh.connect(ip, username='root',password=pasword1)
	ssh.exec_command('s')
	ssh.exec_command('l')
	ssh.exec_command('visonic')
	
	
	return ssh
	
def sshclose(ssh):

	ssh.close()
			
def waitforOnIPMP(channel, string, timeout= 100,num= 1):
	for k in range(timeout*100):
		rl, wl, xl = select.select([channel],[],[],0.0)
		if len(rl) > 0:
			# Must be stdout
			str1 = channel.recv(1024)
			str_split = str1.split("\n")
			L = len (str_split)
			for l in range (L):
				out.prnt(str1,"ipmp")
				#print str1
				data = string.split('***')
				lens = len(data)
				res = 1
				for i in range(lens) :
					if (data[i] in str_split[l]) ==0 : res = 0
				if res == 1:
				
					#out.prnt(str(num) + " Event " + string + " is received on IPMP")
					strlog = str_split[l].split("(D)")
					
					if len (strlog) > 1 :out.prnt(str(num)+" " + strlog[0][:15]+"->" + strlog[1])
					else : out.prnt (str_split)
					return 1
		time.sleep(0.01)
		
	out.prnt ("Time out "+str(timeout)+" s","all+error")
	out.prnt ("no possible to find "+ string+ "----------ERRORIPMP------------","all+error")
	#strlcd = read()	
	#out.prnt("LCD display: "+strlcd)
	return 0


def waitforany(string1,timeout=60):
	res=False
	for k in range(timeout*3):
		LCD1 = read()
		#out.prnt(LCD1)
		for i in string1:
			if i in LCD1:
				res=True
				string2=i
				break
		if res == True:
			print (LCD1+" contains "+string2)
			return 
		time.sleep(0.33)
	out.prnt ("Time out "+str(timeout)+" s","all+error")
	out.prnt ("no possible to find any string----------ERROR------------","all+error")
	strlcd = read()	
	out.prnt("LCD display: "+strlcd)


	
def waitfor(string1,timeout=60):
	for k in range(timeout*3):
		LCD1 = read()
		#out.prnt(LCD1)
		res = string1 in LCD1 
		if res == True:
			print (LCD1+" contains "+string1)
			return 
		time.sleep(0.33)
	out.prnt ("Time out "+str(timeout)+" s","all+error")
	out.prnt ("no possible to find "+ string1+ "----------ERROR------------","all+error")
	strlcd = read()	
	out.prnt("LCD display: "+strlcd)

def WaitFor(List,timeout=60):
	for k in range(timeout*3):
		LCD1 = read()
		#out.prnt(LCD1)
		
		for c in List:
			res = c in LCD1 
			if res == True:
				print (LCD1+" contains "+c)
				return 1
		time.sleep(0.33)
	out.prnt ("Time out "+str(timeout)+" s","all+error")
	sep = ","
	out.prnt ("no possible to find "+ sep.join(List) + "----------ERROR------------","all+error")
	strlcd = read()	
	out.prnt("LCD display: "+strlcd)
	return 0

def waitfor1(string1,string2,string3,timeout=60,string4 = "afdfasdf"):
	for k in range(timeout*3):
		LCD1 = read()
		#out.prnt(LCD1)
		res1 = string1 in LCD1 
		res2 = string2 in LCD1 
		res3 = string3 in LCD1 
		res4 = string4 in LCD1 
		res = res1 or res2 or res3 or res4
		if res == True:
			print (LCD1+" contains "+string1+" or "+string2+" or "+string3+" or ")
			return 1
		time.sleep(0.33)
	#out.prnt ("Time out "+str(timeout)+" s","all+error")
	out.prnt ("not found "+ string1+ ".Trying again ","all")
	strlcd = read()	
	out.prnt("LCD display: "+strlcd)
	return 0
def send_key_old(key):
    #keys = {'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'away':10,'home':11,'off':12,'*':13,'#':14,'back':15,'ok':16,'panic':17,'next':18,'record off':19,'fire':14,'emergency':15}
    keys = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'away':10,'home':11,'off':12,'*':13,'#':14,'back':15,'ok':16,'panic':17,'next':18,'record off':19,'fire':20,'emergency':21}
    data = devices.make_packet(0xF2,1,chr(keys[key]))
    devices.s.write(data)
    p = devices.wait(1)
    return p.data

def send_key_fast(key,tm = 0.4):
    keys = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'away':10,'home':11,'off':12,'*':13,'#':14,'back':15,'ok':16,'panic':17,'next':18,'record off':19,'fire':20,'emergency':21}
    data = devices.make_packet(0xF2,1,chr(keys[key]))
    devices.s.read(devices.s.inWaiting())
    devices.s.write(data)
    time.sleep(tm)

def send_key(key,tm = 0.4):
    i = 0
    for i in range (5):
    	    tm = 0.06
	    lcd = ""
	    lcdafter = "1"
	    time.sleep(tm)
	    lcd = read()
	    time.sleep(tm)		
	    send_key_fast(key,tm = 0)
	    if key == "ok":    time.sleep(tm)
	    else :   time.sleep(tm)
	    lcdafter = read()
	    if lcdafter != lcd :
	    	#out.prnt("OK")
	    	break
	    time.sleep(3)	
	    lcdafter = read()
	    if lcdafter != lcd :
	    	out.prnt("OK3")
	    	break	
	    out.prnt("Trying to retry " + str(i+1))	
    time.sleep(tm)	    

def wait_lcd(expected_string, timeout = 5):
    stop_time = time.time()+timeout
    lcd = ''
    while time.time()<stop_time and not lcd == expected_string:
        lcd = read().strip()
    #print lcd
    return lcd

def read_old():
    data = devices.make_packet(0xF2,3,'')
    devices.s.write(data)
    p = devices.wait(1)
    #return p.data
    return (p.data).strip()

def read():
    data_size = devices.s.inWaiting()
    devices.s.read(data_size)	
    p = None
    while p == None:
        data = devices.make_packet(0xF2,3,'')
        devices.s.write(data)
        #p = devices.wait(1)
        p = devices.wait(1,0.5)
    #return p.data
    return (p.data).strip()

class menu_not_found(Exception):
    def __init__(self,name):
        self.name = name
        
class device_not_found(Exception):
    def __init__(self,name):
        self.name = name

def search_menu1(menu, exactly = True):
    start = s = read()
    while not (s == menu or (menu in s and not exactly)):
        send_key('next')
        s = read()
        if s == start : raise menu_not_found(menu)
def search_menu(menu, maxsearch = 100):
    LCD = read()

    if menu in LCD: 
        time.sleep(0.1)
    	return 1
    for k in range(maxsearch):
        send_key('next',0.1)
        LCD = read()
        #out.prnt (LCD + " "+ str(k))  
	if menu in LCD: 
		#time.sleep(0.1)
		return 1
    out.prnt ("Not found menu " + menu 	)
    return 0
def login(code):
    send_key('next')
    search_menu("INSTALLER MODE")
    send_key('ok')
    for c in code:
        send_key(c)
       
    return True

def loginToUserSettings(code):
    send_key('next')
    search_menu("USER SETTINGS")
    send_key('ok')
    for c in code:
        send_key(c)
        
    #time.sleep(1)    
    return True
    

def away(code):
    send_key('away')
    for c in code:
        send_key(c)
        
    print 'AWAY'
    return True

def home(code):
    send_key('home')
    for c in code:
        send_key(c)
        
    print 'HOME'
    return True

def disarm(code):
    send_key('off')
    for c in code:
        send_key(c)
        
    print 'DISARM'
    return True

def get_cur_keypad():
    number = ''
    id = ''
    while number == '' or id == '':
        lcd = read()
        if lcd[0:2] == 'KP': number = lcd[2:3]
        if lcd[0:2] == 'ID': id = lcd[-4:]
    return number,id


def get_cur_zone_device():
    zone = ''
    id = ''
    while zone == '' or id == '':
        lcd = read()
        if lcd[0:1] == 'Z': zone = lcd[1:3]
        if lcd[0:2] == 'ID': id = lcd[-4:]
    return zone,id


def get_device(dev_type, serial, func = get_cur_zone_device):
    login('9999')
    search_menu("02:ZONES/DEVICES")
    send_key('ok')
    search_menu("MODIFY DEVICES")
    send_key('ok')
    print "TYPE SEARCHING"
    search_menu(dev_type)
    send_key('ok')
    start_zone, start_id = func()
    id = start_id
    zone = start_zone
    while not id == serial:
        send_key('next')
        zone, id = func()
        if zone == start_zone: raise device_not_found(serial)
    return zone

def set_zone_type(zone_type):
    send_key('ok')
    search_menu('ZONE TYPE',False)
    send_key('ok')
    search_menu(zone_type,False)
    send_key('ok')
    time.sleep(5)


def set_device_type(dev_type,serial,zone_type):
    zone = get_device(dev_type,serial)
    set_zone_type(zone_type)
    search_menu(dev_type)
    while not read() == '<OK> TO EXIT':send_key('home')
    send_key('ok')
    return zone

def enbale_keypad_tamper(serial):
    get_device('KEYPADS',serial,get_cur_keypad)
    send_key('ok')
    search_menu('DEV SETTINGS',False)
    send_key('ok')
    search_menu('TAMPERS',False)
    send_key('ok')
    search_menu('Wall Only',False)
    send_key('ok')
    time.sleep(5)
    send_key('away')
    send_key('ok')


def dev(OperateString):
	time.sleep(0.3)
	devices.s.close()
	os.system(PYTHON+"Modules"+SEPARATOR+"PG.py "+OperateString)
	print OperateString
	strCom = com.ComPanel()
	devices.s = serial.Serial(strCom, 9600, timeout=0)
	time.sleep(0.3)
if __name__ == "__main__":
    
    #LCD1 = { 1:'P1:R  P2:-  P3:-', 2:'  USER SETTINGS ', 3:'  PERIODIC TEST ', 4:' INSTALLER  MODE' }
    LCD1 = { 1:'P1:R  P2:-  P3:-', 2:'USER SETTINGS', 3:'PERIODIC TEST', 4:'INSTALLER  MODE' }
    LcdNum = 1
    i = 1
    #while i <= 1000: # it is passed successfully
    while i <= 25000:
        if LcdNum >= 4:
            LcdNum = 1
        else:
            LcdNum = LcdNum + 1
        
        while True:
            # clear COM-port buffer
            data_size = devices.s.inWaiting()
            devices.s.read(data_size)
        
            send_key_old('next')
            LcdStr = read_old()
            if LCD1[LcdNum] == LcdStr:
                logging.debug( 'equal -- var: "{0}" -- LCD "{1}" -- loop: {2}'.format( LCD1[LcdNum], LcdStr, i ) )
                print 'equal -- var: "{0}" -- LCD "{1}" -- loop: {2}'.format( LCD1[LcdNum], LcdStr, i )
                break
            else:
                str_res = 'not equal -- var: "{0}" -- LCD "{1}" -- loop: {2}'.format( LCD1[LcdNum], LcdStr, i )
                logging.debug( str_res )
                print str_res

        #time.sleep(5)
        #time.sleep(1)
        i  = i + 1
        
    sys.exit()
