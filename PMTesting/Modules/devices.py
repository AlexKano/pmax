#!/usr/bin/env python

import serial, time, sys, cPickle
import logging
import os.path
import com
import navigator
import out

SEPARATOR = "\\"
if (os.name == "posix"):
    SEPARATOR = "/"
def hexdump(s):
    return ' '.join(["%02X" % ord(i) for i in s ])

class packet:
    cmd = 0
    data = ''

class device_type:
    # "PowerCodeII Device Protocol.doc":"3.3 Device Categories" - This is 'Manufacturing Information'?
    # D'10, D'11
    contact           = '\x03\x29' # Dec:3,41 (TypeID: 100, LCD: "Contact")
    motion_sensor     = '\x03\x01'
    motion_camera     = '\x03\x04' # Dec:3, (LCD: "Motion Camra", TypeID: 140)
    smoke             = '\x03\x15' # Dec:3,21 - Smoke + Siren
    smoke_heat        = '\x03\x16' # Dec:3,22 - Smoke + Siren + Heat
    gas               = '\x03\x17' # Dec:3,23 (TypeID: 230, LCD: "GAS Sensor")
    co                = '\x03\x18' # Dec:3,24 (TypeID: 220, LCD: "CO Sensor")
    flood             = '\x03\x19' # Dec:3,25 (TypeID: 240, LCD: "Flood Sensor")
    #heat              = '' # Dec:
    temperature       = '\x03\x1A' # Dec:3,26 (LCD: "Temp. Sensor", TypeID: 250)
    smoke_heat_temp   = '\x03\x1B' # Dec:3,27 - Smoke + Siren + Heat + Temperature
    outdoor_siren     = '\x02\x01' # 
    indoor_siren      = '\x02\x02' # 
    keyfob            = '\x05\x01'
    keyfob_lcd        = '\x05\x02' 
    repeater          = '\x00\x01'
    keypad_big        = '\x04\x01'
    keypad_small      = '\x04\x02'

    #New devices (27.04.2011)
    contact_aux       = '\x03\x2A' # Dec:3,42 (TypeID: 101, LCD: "Contact_1in")
    clip              = '\x03\x03' # (TypeID: 122, LCD: "Motion Curtn") - certain? narrow?
    tower30           = '\x03\x06' # (TypeID: 123, LCD: "Motion Sens")
    glass_break       = '\x03\x05' # (TypeID: 160, LCD: "Glass Break")
    #kp141             = '\x0\x0'
    arming_station    = '\x04\x05' # (TypeID: 374, LCD: "LCD Keypad")
    wired_zone        = '\x03\xFE'

def str_l(s):
    return chr(len(s)) + s

def make_host_packet(cmd,data):
    data = chr(cmd) + data
    l = 2 + len(data)
    data = chr(l) + data
    data = data + crc16(data)[0]+'\x0A'
    return data

def make_packet(proto, cmd, data):
    p = chr(proto & 0xff)+chr(cmd & 0xff)+'\x00\x00'+str_l(data)
    crc = crc16(p)
    return '\x0D' + p + crc + '\x0A'

def crc16(data):
    crc = 0
    for p in data:
        crc += ord(p)
    return chr(crc & 0x00ff)+chr((crc & 0xff00)>>8)

def dev_serial(id):
    #if not id>>13==0: print "Improper device id"
    id_s=''
    for i in range(4):
        c = 0xff & id
        id = id>>8
        id_s = id_s + chr(c)
    return id_s

def generateSeq():
    try:
        f = open(CurrDir+SEPARATOR+"seq","r")
        seq = int(f.readline())
        f.close()
    except:
        seq = 0
    f = open(CurrDir+SEPARATOR+"seq","w")
    print CurrDir+SEPARATOR+"seq"+"my"
    new_seq = seq+1
    if new_seq == 256: new_seq = 1
    f.write("%d" % new_seq)
    f.close()
    return seq
    
def device_cmd( serial, short_id, mcode, mdata_type, mdata_value ):
    # prepare device protocol
    seq = generateSeq()
    SerNum = dev_serial(int(serial))[:3]
    mdata = chr(mcode) + str_l( chr(mdata_type) + str_l(mdata_value) )
    device_packet = '\xE4\x00' + chr(seq) + SerNum + mdata
    
    # prepare host protocol
    final_hop_info = '\x00'*11
    relaying_repeater_ID = 0
    repeater_hop_info = '\x00'*11
    host_protocol_message = make_host_packet( 0x30, chr(short_id)+'\x01\xF8'+final_hop_info+chr(relaying_repeater_ID)+repeater_hop_info+str_l(device_packet) )
    return host_protocol_message

def read_packet(timeout = 5):
    """ Read packet with one command
        # Example:
        # 0D F2 0B 00 00 0A 01 05 BB 0B 00 00 64 01 04 08 44 02 0A
        # 0D F2 0C 00 00 05 50 64 01 00 00 B8 01 0A
    """
    pack = ''
    pack_len = 0
    stop_time = time.time() + timeout
    while time.time() < stop_time:
        #time.sleep(0.1)
        data_size = s.inWaiting()
        if data_size == 0: continue
        #print "0. data_size: %d" % data_size
        pack = pack + s.read(1)
        fnd = pack.find('\x0D\xF2')
        if len(pack) >= 2:
            if fnd > (-1): # '0x0D 0xF2'
                if fnd > 0:
                    print 'TRASH FOUND??: {0}'.format( hexdump(pack[:fnd]) )
                    pack = pack[fnd:] # cut buffer
                pack = pack + s.read(4)
                pack_len = ord( pack[len(pack)-1:] )
                #print 'pack_data_len: {0} ({1})'.format( pack_len, hex(pack_len) )
                pack = pack + s.read(pack_len+3)
                if pack[len(pack)-1:] == '\x0A': # '0x0A'
                    #print 'pack 0: {0}'.format( hexdump(pack) )
                    return pack
            else:
                print 'TRASH FOUND?: {0}'.format( hexdump(pack) )
    print 'Exit with timeout'
    return " ERROR        "
def wait(code, timeout = 10):
    buffer = ''
    stop_time = time.time() + timeout
    while time.time() < stop_time:
        time.sleep(0.1)
        data_size = s.inWaiting()
        if data_size == 0: continue
        buffer = read_packet(4)

        if len(buffer) < 9: print 'Error: len(buffer) < 9'
        
        l = ord(buffer[5:6])
        #if buffer[6+l+2:6+l+2+1] == '':
        #    break
        #assert buffer[6+l+2] == '\n'
        
        p = packet()
        p.cmd = ord(buffer[2:3])
        p.data = buffer[6:6+l]
##        print 'PACKET RECEIVED. CMD CODE: {0} ({1})'.format( p.cmd , hex(p.cmd) )

        buffer = buffer[6+l+2+1:] # cut buffer # don't need?
        
        if p.cmd == code: return p

def send_host_cmd(cmd, f2_code = 9):
    s.read(s.inWaiting())
    #print 'packet (send_host_cmd): {0}'.format( hexdump(cmd) )
    packet = make_packet(0xF2,f2_code,cmd)
    logging.debug( 'packet (send_host_cmd): {0}'.format( hexdump(packet) ) )
    s.write(packet)

def save(dev):
    if os.path.exists(CurrDir+"/devices"):
        f = open(CurrDir+"/devices/device_"+( "%d" % dev.short_id ), "w")
        cPickle.dump(dev,f)
    else:
        logging.error( 'Path for Save: "{0}" not exist.'.format( CurrDir+"/devices" ) )

def load(short_id):
    if os.path.exists(CurrDir+"/devices"):
        f = open(CurrDir+"/devices/device_"+( "%d" % short_id ), "r")
        return cPickle.load(f)
    else:
        logging.error( 'Path for Load: "{0}" not exist.'.format( CurrDir+"/devices" ) )

class enroll_failed(BaseException):
    #print 'enroll_failed'
    pass

class device:
    def __init__(self, serial, type):
        self.serial = serial
        self.type = type

    def enroll(self, customer_Mid = 0, customer_Did = 0):
        s = dev_serial(int(self.serial))
        rssi = '\x32'
        tx_power = '\x01'
        association_request_data='\x00'
        #attached_device_information='\x01'+self.type+'\x03\x14\x03\x00\x00'
        attached_device_information='\x00'+self.type+'\x01\x14\x03\x00\x00'
        #Counting customer id
        manufacturing_information=chr(customer_Mid) + chr(customer_Did % 256) + chr(customer_Did / 256)
        rf_module_information='\x00\x70\x09\x28\x03\x08\x01' 
        host_protocol_message = make_host_packet(0x41,s + rssi + tx_power + association_request_data + '\x00' + str_l(attached_device_information)+'\x01'+str_l(manufacturing_information)+'\x02'+str_l(rf_module_information))
        enroll_packet = '\x01'+host_protocol_message     
        #print 'host enroll protocol: {0}'.format( hexdump(enroll_packet) )
        send_host_cmd(enroll_packet, 13)
        
        p = wait(11,5)
        if p == None: raise enroll_failed()
        self.short_id = ord(p.data[6])
        
        if p.data[7] == '\x00':
            self.DevType = 'RP'
        elif p.data[7] == '\x01':
            self.DevType = 'KP' # KEYPAD_2WAY_TYPE
        elif p.data[7] == '\x02':
            self.DevType = 'SR'
        elif p.data[7] == '\x03':
            self.DevType = 'Z'
        elif p.data[7] == '\x04':
            self.DevType = 'KP' # KEYPAD_1WAY_TYPE
        elif p.data[7] == '\x05':
            self.DevType = 'K' # KEYFOB_TYPE
        else:
            self.DevType = 'Unknown'
        
        if self.DevType == 'KP':
            self.DevNum  = '%d' % ord(p.data[8])
        else:
            self.DevNum  = '%02d' % ord(p.data[8])
        print 'After wait cmd #11. short_id: {0}, DevType: {1}, DevNum: {2}\n'.format( self.short_id, self.DevType, self.DevNum )
        
        p = wait(12,5)
        if p == None: raise enroll_failed()
        self.short_id = ord(p.data[1])
        print 'After wait cmd #12 (Enroll success). short_id: {0}'.format( self.short_id )

    def update(self):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 253, chr(0))
        send_host_cmd(pkt_open)
        
    def tamper(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 39, chr(IsOpen))
        send_host_cmd(pkt_open)

    def lowbattery(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 40, chr(IsOpen))
        send_host_cmd(pkt_open)

    def ac_fail(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 41, chr(IsOpen))
        send_host_cmd(pkt_open)

    def hello(self): #Seems to be Keep-alive message
        pkt_ka = device_cmd(self.serial, self.short_id, 5, 64, chr(0))
        send_host_cmd(pkt_ka)
        
class violated_device(device):
    def violate(self):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 1, chr(2)) # Passive Motion ?
        send_host_cmd(pkt_open)

class glass_break_device(violated_device):
    def glass_break(self):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 6, chr(2)) # Glass Break
        send_host_cmd(pkt_open)

class tower_device(violated_device):
    def masking(self, IsOpen = 1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 44, chr(IsOpen))
        send_host_cmd(pkt_open)

class restorable_device(device):
    def open(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 8, chr(IsOpen)) # Switch / Magnetic
        send_host_cmd(pkt_open)

    def smoke_alarm(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 9, chr(IsOpen))
        send_host_cmd(pkt_open)

    def heat_alarm(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 10, chr(IsOpen))
        send_host_cmd(pkt_open)

    def aux(self, IsOpen=1):
        bMask = 0xFF * IsOpen #Open all 8 auxilary inputs, according to mask 0b11111111 = 0xFF
        pkt_open = device_cmd(self.serial, self.short_id, 5, 17, chr(bMask)) # Magnet with Auxiliary Input
        send_host_cmd(pkt_open)
        
    def smoke_trouble(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 46, chr(IsOpen))
        send_host_cmd(pkt_open)

    def heat_trouble(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 45, chr(IsOpen))
        send_host_cmd(pkt_open)
        
    def fire(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 34, chr(IsOpen))
        send_host_cmd(pkt_open)

    def supervision(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 116, chr(IsOpen))
        send_host_cmd(pkt_open)

    #Need to Clean event
    def clean_me(self):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 10, chr(2))
        send_host_cmd(pkt_open)

class device_co(device):
    def alert(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 11, chr(IsOpen)) # CO
        send_host_cmd(pkt_open)
    def trouble(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 51, chr(IsOpen)) # CO Sensor Trouble
        send_host_cmd(pkt_open)

class gas_device(device):
    def gas_alert(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 13, chr(IsOpen))
        send_host_cmd(pkt_open)
    def gas_trouble(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 52, chr(IsOpen))
        send_host_cmd(pkt_open)

class flood_device(device):
    def flood(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 16, chr(IsOpen))
        send_host_cmd(pkt_open)


class temperature_device(device):
    iMinTemp = 0x05
    iMaxTemp = 0xF0
    aTemp = [iMaxTemp, iMinTemp]
    def freezer(self, IsOpen=1): # <-10
        pkt_open = device_cmd(self.serial, self.short_id, 5, 24, chr(self.aTemp[IsOpen]))
        send_host_cmd(pkt_open)
    def freezing(self, IsOpen=1): # < 7
        pkt_open = device_cmd(self.serial, self.short_id, 5, 24, chr(self.aTemp[IsOpen]))
        send_host_cmd(pkt_open)
    def cold(self, IsOpen=1): # < 19
        pkt_open = device_cmd(self.serial, self.short_id, 5, 24, chr(self.aTemp[IsOpen]))
        send_host_cmd(pkt_open)
    def hot(self, IsOpen=1): # > 28(35)
        pkt_open = device_cmd(self.serial, self.short_id, 5, 24, chr(self.aTemp[int(not(IsOpen))]))
        send_host_cmd(pkt_open)
    def freezer_trouble(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 34, chr(IsOpen))
        send_host_cmd(pkt_open)
    def probe(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 50, chr(IsOpen))
        send_host_cmd(pkt_open)

class arming_device(device):
    def __init__(self, serial, type):
        self.serial = serial
        self.type = type 
        #types: big_keypad, keyfob
        
        #keyfob is non-user and non-partition device but keypad is not
        #so keyfob.partitions field is always set for [] and keyfob.user_code is always set for 'AAAA'
        self.bin_user_code = '\xAA\xAA'
        self.bin_partitions = 0

    def arm_away(self):
        pkt_open = device_cmd(self.serial, self.short_id, 4, 69, chr(self.bin_partitions)+'\x03'+self.bin_user_code)
        send_host_cmd(pkt_open)

    def arm_home(self):
        pkt_open = device_cmd(self.serial, self.short_id, 4, 69, chr(self.bin_partitions)+'\x02'+self.bin_user_code)
        send_host_cmd(pkt_open)

    def disarm(self):
        pkt_open = device_cmd(self.serial, self.short_id, 4, 69, chr(self.bin_partitions)+'\x01'+self.bin_user_code)
        send_host_cmd(pkt_open)

    def aux_button(self):
        pkt_open = device_cmd(self.serial, self.short_id, 4, 74, chr(1))
        send_host_cmd(pkt_open)

    def panic(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 33, chr(IsOpen))
        send_host_cmd(pkt_open)
        
    def fire(self):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 34, chr(1))
        send_host_cmd(pkt_open)

    def emergency(self):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 35, chr(1))
        send_host_cmd(pkt_open)

    #TAG actions

    def tag_action(self, tag_id=0, action="away", part_bitmap=0):
        action_id = 3
        if action.lower() == "away":
            action_id = 3
        elif action.lower() == "home":
            action_id = 2
        elif action.lower() == "disarm":
            action_id = 1
        elif action.lower() == "away_latchkey":
            action_id = 4
        elif action.lower() == "arm_part":
            action_id = 5
        elif action.lower() == "quick_away":
            action_id = 6
        elif action.lower() == "quick_home":
            action_id = 7
        elif action.lower() == "arm_instant":
            action_id = 8 
        elif action.lower() == "check_code":
            action_id = 9
        else:
            print "Wrong event was specified for TAG"
            sys.exit(0)
        packet = device_cmd(self.serial, self.short_id, 4, 73, chr(part_bitmap) + chr(action_id) + '\x28\x00\x00\x00\x00' + chr(tag_id) + '\x00\x00\x00');
        send_host_cmd(packet)

class keyfob(arming_device):
    def __init__(self, serial, dev_type = device_type.keyfob):
        arming_device.__init__(self, serial, dev_type)

class big_keypad(arming_device):
    def __init__(self, serial, dev_type = device_type.keypad_big):
        arming_device.__init__(self, serial, dev_type)

    def set_partitions(self,partitions):
        self.partitions = partitions
        pbitmap = 0
        for p in partitions:
            pbitmap = pbitmap | (1<<p)
        self.bin_partitions = pbitmap>>1
        
    def set_user_code(self,user_code):
        print self.__class__
        self.user_code = user_code
        self.bin_user_code = chr(int(user_code[:2],16))+chr(int(user_code[2:],16))

    def enable_partitions(self):
        pkt_open = device_cmd(self.serial, self.short_id, 4, 118, chr(self.h_partitions))
        send_host_cmd(pkt_open)

class arming_station(big_keypad):
    def fire(self):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 34, chr(1))
        send_host_cmd(pkt_open)
        
    def supervision(self, IsOpen = 1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 116, chr(1))
        send_host_cmd(pkt_open)

class repeater(device):
    def __init__(self, serial):
        self.serial = serial
        self.type = device_type.repeater

    def jamming(self, IsOpen=1):
        pkt_open = device_cmd(self.serial, self.short_id, 5, 48, chr(IsOpen))
        send_host_cmd(pkt_open)

#==================================++++++++============================================
#==================================++++++++============================================
#==================================++++++++============================================
#==================================++++++++============================================
#==================================++++++++============================================
def ClearDevices():
	f = open ("Modules"+SEPARATOR +"devices"+SEPARATOR +"devices.info","w")
	f.close

def ClearZones():
	f = open ("Modules"+SEPARATOR +"devices"+SEPARATOR +"devices.info","r")
	devices_list_before=f.readlines()
	f.close
	print devices_list_before
	devices_list_after=[]
	for s in devices_list_before:
		if s[0]!="Z": devices_list_after.append(s)
	print devices_list_after
	f = open ("Modules"+SEPARATOR +"devices"+SEPARATOR +"devices.info","w")
	f.writelines(devices_list_after)
	f.close
	
 

def EnrollDev(typedev,LongID):
	navigator.dev("enroll "+typedev+" "+str(LongID))

	print navigator.read()
	f = open ("Modules"+SEPARATOR +"ShortID.txt","r")
	line = f.readline()
	f.close
	line_split = line.split(",")
	typenumdev = line_split[1]+str(int(line_split[2]))
	ShortID = line_split[0]
	time.sleep(3)
	navigator.dev("update "+str(ShortID)+" " +str(LongID))
	print line
	print typenumdev
	print ShortID
	f = open ("Modules"+SEPARATOR +"devices"+SEPARATOR +"devices.info","a")
	f.write (typenumdev+","+ShortID+ "," + str(LongID)+ "," + typedev + "," )
	f.write ("\n")
	f.close
def UpdateDev(typeofdevice = "all", num = 1,time_sleep = 1):
	if typeofdevice != "all":
		typeofdevicenum = typeofdevice+str(num)
		flag = 0
		f = open ("Modules"+SEPARATOR +"devices"+SEPARATOR +"devices.info","r")
		for line in f:
			time.sleep(time_sleep)	
			data= line.split(',')
			#print data[0]
			#print "\ndfsdfsd"
			if data[0] == typeofdevicenum:
				navigator.dev("update " +data[1]+" "+data[2])
				flag = 1
				break
		if flag == 0:
			out.prnt("Warning: NO found virtual device: "+typeofdevicenum+"\n")
	if typeofdevice == "all":
		f = open ("Modules"+SEPARATOR +"devices"+SEPARATOR +"devices.info","r")
		for line in f:
			time.sleep(time_sleep)
			data= line.split(',')
			navigator.dev("update " +data[1]+" "+data[2])
			

def deletedevices(dev):
	time_after_sent_key = 0.3
	navigator.login("9999")
	navigator.search_menu("ZONES/DEVICES")
	navigator.send_key("ok",time_after_sent_key)
	navigator.search_menu("DELETE")
	navigator.send_key("ok",time_after_sent_key)

	while 1 :
		navigator.search_menu(dev)
		navigator.send_key("ok",time_after_sent_key)
		if "NO EXISTING" in navigator.read(): 
			navigator.send_key("away",time_after_sent_key)			
			navigator.send_key("ok",2)						
			break	
		navigator.send_key("ok",time_after_sent_key)
		navigator.send_key("off",time_after_sent_key+0.3)
		
def AllDeleteDevices():
	time_after_sent_key = 0.3
	navigator.login("9999")
	navigator.search_menu("ZONES/DEVICES")
	navigator.send_key("ok",time_after_sent_key)
	navigator.search_menu("DELETE")
	navigator.send_key("ok",time_after_sent_key)
	list1 = ["CONTACT","MOTION","GLASS","SMOKE","CO ","GAS","FLOOD","TEMPERATURE","WIRED","TAGS","KEYFOB","KEYPADS","SIRENS","REPEATERS"]
	len1 = len (list1)
	for i in range(len1):
		while 1 :
			navigator.search_menu(list1[i])
			navigator.send_key("ok",time_after_sent_key)
			if "NO EXISTING" in navigator.read(): break	
			navigator.send_key("ok",time_after_sent_key)
			navigator.send_key("off",time_after_sent_key+0.3)
	navigator.send_key("away",time_after_sent_key)			
	navigator.send_key("ok",2)					
def GenEvent(typeofdevice,num,event,timebefore = 5):
	typeofdevicenum = typeofdevice+str(num)
	time.sleep(timebefore)
	flag = 0
	f = open ("Modules"+SEPARATOR +"devices"+SEPARATOR +"devices.info","r")
	for line in f:
		data= line.split(',')
		#print data[0]
		#print "\ndfsdfsd"
		if data[0] == typeofdevicenum:
			navigator.dev(event +" "+data[1]+" "+data[2])
			flag = 1
			break
	if flag == 0:
		out.prnt("Warning: NO found virtual device: "+typeofdevicenum+"\n")
	
	
	
	
	
	
	
	
		

	
		
		
#==================================++++++++============================================
#==================================++++++++============================================
#==================================++++++++============================================
#==================================++++++++============================================
		
		

CurrDir = "Modules"#'\\'.join(sys.argv[0].split('\\')[:-1])
#print 'CurrDir: "%s"' % CurrDir
 
class ser():
    def __init__(self):
        None
        
    def ser(self):
        #f2 = open(CurrDir+'\com.txt', "r", 0) # Win
        #f2 = open('com.txt', "r", 0) # Linux

        strCom = com.ComPanel()
        #print 'COM: "%s"' % strCom
        #f2.close()

        self.ser = serial.Serial(strCom, 9600, timeout=0) # Win
        #s = serial.Serial('/dev/ttyS0', 9600, timeout=0) # Linux

ser = ser()
ser.ser()

s = ser.ser


LOG_FILENAME = CurrDir+'/LogPG.txt' # Win
#LOG_FILENAME = 'LogPG.txt' # Linux
logging.basicConfig(level=logging.DEBUG,
#logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=LOG_FILENAME
                    #,filemode='w'
                   )
#logging.debug('This is a debug message')
#logging.info('This is an info message')
#logging.warning('This is a warning message')
#logging.error('This is an error message')
#logging.critical('This is a critical error message')
