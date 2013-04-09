#!/usr/bin/env python

import serial, time, sys, cPickle
import logging
import os.path
SEPARATOR = "\\"
if (os.name == "posix"):
    SEPARATOR = "/"
import os
cmd_folder = os.path.dirname(os.path.abspath(__file__))
#print cmd_folder+'\PowerMaster'
sys.path.append( cmd_folder + SEPARATOR+'PowerMaster' )
import serial_port_craft as SPC
import com


CurrDir = cmd_folder
#print 'CurrDir: "%s"' % CurrDir

LOG_FILENAME = CurrDir + SEPARATOR + 'LogPG.txt' # Win
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


class packet:
    cmd = 0
    data = ''

class device_type:
    # "PowerCodeII Device Protocol.doc":"3.3 Device Categories" - This is 'Manufacturing Information'?
    # D'10, D'11
    # //RF/PowerCode2/Design Docs/Application Design/PowerCodeII Device Protocol.doc

    contact           = '\x03\x29' # Dec:3,41 (TypeID: 100, LCD: "Contact")
    contact_aux       = '\x03\x2A' # Dec:3,42 (TypeID: 101, LCD: "Contact_1in") "Contact + Auxiliary Input"
    motion_sensor     = '\x03\x01' # Dec:3,01 "Motion, PIR"
    motion_camera     = '\x03\x04' # Dec:3,04 (LCD: "Motion Camra", TypeID: 140) "PIR-Camera"
    tower30           = '\x03\x06' # Dec:3,06 (TypeID: 123, LCD: "MOTION SENSORS"\"Motion Sens")  "Motion, PIR + AM"
    tower32           = '\x03\x07' # Dec:3,07 (TypeID: 150, LCD: "MOTION SENSORS"\"Motion DUAL")  "Motion, PIR Dual AM" (2012-08-28)
    tower20           = '\x03\x08' # Dec:3,08 (TypeID: 130, LCD: "MOTION SENSORS"\"Motion Outd.") "Motion, Outdor"      (2012-08-28)

    # Safety Detectors
    smoke             = '\x03\x15' # Dec:3,21 - Smoke + Siren
    smoke_heat        = '\x03\x16' # Dec:3,22 - Smoke + Siren + Heat
    gas               = '\x03\x17' # Dec:3,23 (TypeID: 230, LCD: "GAS Sensor")
    co                = '\x03\x18' # Dec:3,24 (TypeID: 220, LCD: "CO Sensor")
    flood             = '\x03\x19' # Dec:3,25 (TypeID: 240, LCD: "Flood Sensor")
    #heat              = '' # Dec:
    temperature       = '\x03\x1A' # Dec:3,26 (LCD: "Temp. Sensor", TypeID: 250)
    smoke_heat_temp   = '\x03\x1B' # Dec:3,27 - Smoke + Siren + Heat + Temperature
    shock             = '\x03\x32' # Dec:3,50 (TypeID: 1xx, LCD: "SHOCK SENSORS"\"Shock xx")     "" (2012-08-28) ???
    shock_aux         = '\x03\x33' # Dec:3,51 (TypeID: 171, LCD: "SHOCK SENSORS"\"Shk+AX")       "" (2012-08-28)
    shock_contact     = '\x03\x34' # Dec:3,52 (TypeID: 172, LCD: "SHOCK SENSORS"\"Shk+CntG3")    "" (2012-08-28)
    shock_aux_contact = '\x03\x35' # Dec:3,53 (TypeID: 170, LCD: "SHOCK SENSORS"\"Shk+AX+CntG3") "" (2012-08-28)
    shock_contact_g2  = '\x03\x36' # Dec:3,54 (TypeID: 173, LCD: "SHOCK SENSORS"\"Shock+CntG2")  "" (2012-08-28)

    outdoor_siren     = '\x02\x01' # 
    indoor_siren      = '\x02\x02' # 

    keyfob            = '\x05\x01' # KF-234
    keyfob_235        = '\x05\x02' # KF-235
    keyfob_lcd        = '\x05\x03' # LCD Keyfob # now don't work (panel K15.008)

    repeater          = '\x00\x01'
    # KP-150 (big with LCD?) - only PowerCode1
    keypad_big        = '\x04\x01' # Dec:4,01 (TypeID: 370, LCD: "Keypad")         # Big Keypad   (KP-140)
    keypad_small      = '\x04\x02' # Dec:4,02 (TypeID: 371, LCD: "Prox Keypad")    # Small Keypad (KP-141) (without LCD with proxy tags)
    arming_station    = '\x04\x05' # Dec:4,05 (TypeID: 374, LCD: "LCD Keypad")     # KP-160 With sensor button.
    keypad_250        = '\x04\x06' # Dec:4,06 (TypeID: 375, LCD: "LCD Keypad")     # KP-250 Stand alone keypad? Full functionality?

    #New devices (27.04.2011)
    clip              = '\x03\x03' # (TypeID: 122, LCD: "Motion Curtn") - certain? narrow?
    glass_break       = '\x03\x05' # (TypeID: 160, LCD: "Glass Break")
    wired_zone        = '\x03\xFE'


class ser():
    def __init__(self):
        self.ff = 'dd'
        None

    def ser(self):
        #f2 = open(CurrDir + SEPARATOR + 'com.txt', "r", 0) # Win
        #f2 = open('com.txt', "r", 0) # Linux

        strCom = com.ComPanel()
        #print 'COM: "%s"' % strCom
        #f2.close()

        #if sys.platform == 'win32':
        self.ser = serial.Serial(strCom, 9600, timeout=0) # Win
        #s = serial.Serial('/dev/ttyS0', 9600, timeout=0) # Linux


    def send_host_cmd(self, pkt, f2_code = 9):
        #print hexdump(pkt)
        #self.ser.read( self.ser.inWaiting() ) # Is it clear port buffer?
        packet = make_packet( 0xF2, f2_code, pkt )

        StrLog = '(ser.send_host_cmd): {0}'.format( hexdump(packet) )
        print StrLog
        logging.debug( StrLog )

        self.ser.write(packet)

def send_host_cmd(pkt, f2_code = 9):
    #print hexdump(pkt)
    #s.read( s.inWaiting() ) # Is it clear port buffer?
    packet = make_packet( 0xF2, f2_code, pkt )

    StrLog = '(send_host_cmd): {0}'.format( hexdump(packet) )
    print StrLog
    logging.debug( StrLog )

    s.write(packet)

def hexdump(s):
    return ' '.join(["%02X" % ord(i) for i in s ])

def str_l(s):
    return chr(len(s)) + s

def crc16(data):
    crc = 0
    for p in data:
        crc += ord(p)
    return chr(crc & 0x00ff)+chr((crc & 0xff00)>>8)

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
        f = open(CurrDir + SEPARATOR + "seq","r")
        seq = int(f.readline())
        f.close()
    except:
        seq = 0
    f = open(CurrDir + SEPARATOR + "seq","w")
    print CurrDir + SEPARATOR + "seq"
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

'''
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
        if data_size == 0:
            #print 'data_size == 0. sleep and continue'
            time.sleep(0.09)
            continue
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
    print '(def read_packet) Output due to a timeout {0} sec.'.format( timeout )
    return pack
    
def wait(code, timeout = 10):
    buffer = ''
    pkt = None
    stop_time = time.time() + timeout
    while time.time() < stop_time:
        buffer = read_packet(4)

        if len(buffer) < 9:
            print 'Error: len(buffer) < 9'
            continue
        
        data_len = ord(buffer[5:6])
        #assert buffer[6+data_len+2] == '\n'
        print 'wait: ' + hexdump(buffer)
        
        if ord(buffer[2:3]) == code:
            pkt = packet()
            pkt.cmd = ord(buffer[2:3])
            pkt.data = buffer[6:6+data_len]
            print 'PACKET RECEIVED. CMD CODE: {0} ({1})'.format( pkt.cmd , hex(pkt.cmd) )
            if pkt.cmd == code: return pkt

    print '("def wait" Cmd: {0}) Exit by timeout {1} sec.'.format( code, timeout )
    return pkt
'''

def save(dev):
    if os.path.exists(CurrDir + SEPARATOR + "devices"):
        f = open(CurrDir + SEPARATOR + "devices" + SEPARATOR + "device_" + ( "%d" % dev.short_id ), "w")
        cPickle.dump(dev,f)
    else:
        logging.error( 'Path for Save: "{0}" not exist.'.format( CurrDir + SEPARATOR + "devices" ) )

def load(short_id):
    if os.path.exists(CurrDir + SEPARATOR + "devices"):
        f = open(CurrDir + SEPARATOR + "devices" + SEPARATOR + "device_" + ( "%d" % short_id ), "r")
        return cPickle.load(f)
    else:
        logging.error( 'Path for Load: "{0}" not exist.'.format( CurrDir + SEPARATOR + "devices" ) )

class enroll_failed(BaseException):
    #print 'enroll_failed'
    pass

class device:
    """ class for work with devises """

    def __init__(self, serial, type):
        self.serial = serial
        self.type = type
        #self.SerialPort = None

    def SendPacketTo_PortOrFile(self, Packet, StrForLog):
        """ ... and print in console and log file """

        StrLog = '({0}): {1}'.format( StrForLog, SPC.hexdump(Packet) )
        print StrLog
        logging.debug( StrLog )

        #if self.SerPort.ser == None:
        #    print 'The port is not open'
        #    return

        if (self.SerPort != None): self.SerPort.ser.write(Packet)
        else:
            print 'The port is not open. Saving to file.'
            f = open(CurrDir+ SEPARATOR +'Tmp'+ SEPARATOR +'packet_for_run.txt', "w", 0)
            f.write( SPC.hexdump2(Packet) )
            f.close()

    def enroll(self, customer_Mid = 0, customer_Did = 0):
        """ enroll device """

        ser_num = SPC.dev_serial(int(self.serial))
        #print SPC.hexdump(ser_num)

        rssi = '\x32'
        tx_power = '\x01'
        association_request_data = '\x00'
        #attached_device_information = '\x01'+self.type+'\x03\x14\x03\x00\x00'
        attached_device_information = '\x00'+self.type+'\x01\x14\x03\x00\x00'
        #Counting customer id
        manufacturing_information = chr(customer_Mid) + chr(customer_Did % 256) + chr(customer_Did / 256)
        rf_module_information = '\x00\x70\x09\x28\x03\x08\x01' 
        host_protocol_message = SPC.make_host_packet( 0x41, ser_num + rssi + tx_power
            + association_request_data + '\x00' + SPC.str_len_plus_str(attached_device_information)
            + '\x01' + SPC.str_len_plus_str(manufacturing_information) + '\x02'
            + SPC.str_len_plus_str(rf_module_information) )
        enroll_packet = '\x01' + host_protocol_message

        packet_f2 = SPC.make_packet( 0xF2, 13, enroll_packet ) # F2 protocol packet

        StrLog = '(enroll): {0}'.format( SPC.hexdump(packet_f2) )
        print StrLog
        logging.debug( StrLog )

        Cmd = SPC.packet( 11 )
        self.SerPort.wait(Cmd, 'Start')
        #self.SerPort.ser.write(packet_f2)
        self.SendPacketTo_PortOrFile( packet_f2, 'enroll' )
        self.SerPort.wait(Cmd, 'Check', 5)

        #print 'ShortID {0}, DevTypeNum {1}, DevNum {2}'.format( Cmd.ShortID, Cmd.DevTypeNum, Cmd.DevNum )

        if Cmd.ShortID == -1: raise enroll_failed()
        self.short_id = Cmd.ShortID

        if   Cmd.DevTypeNum == 0:      self.DevType = 'RP'
        elif Cmd.DevTypeNum == 1:      self.DevType = 'K'   # KEYPAD_2WAY_TYPE
        elif Cmd.DevTypeNum == 2:      self.DevType = 'SR'
        elif Cmd.DevTypeNum == 3:      self.DevType = 'Z'
        elif Cmd.DevTypeNum == 4:      self.DevType = 'K'   # KEYPAD_1WAY_TYPE
        elif Cmd.DevTypeNum == 5:      self.DevType = 'F'   # KEYFOB_TYPE
        else:            self.DevType = 'Unknown'

        self.DevNum  = '%02d' % Cmd.DevNum
        if self.DevType == 'RP': self.DevNum  = '%d' % Cmd.DevNum
        print 'After wait cmd #11. short_id: {0}, DevType: {1}, DevNum: {2}'.format( self.short_id, self.DevType, self.DevNum )

        return


    def update(self):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 253, chr(0))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'update={0}'.format(1) )

    def tamper(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 39, chr(IsOpen))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'tamper={0}'.format(IsOpen) )

    def lowbattery(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 40, chr(IsOpen))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'lowbattery={0}'.format(IsOpen) )

    def ac_fail(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 41, chr(IsOpen))
        #send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'ac_fail={0}'.format(IsOpen) )

    def hello(self): #Seems to be Keep-alive message
        pkt_ka = SPC.device_cmd(self.serial, self.short_id, 5, 64, chr(0))
        #send_host_cmd(pkt_ka)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt_ka ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'hello ka' )

    def fire(self):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 34, chr(1))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'fire' )

class restorable_device(device):

    def open(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 8, chr(IsOpen)) # Switch / Magnetic
        #pkt = '\x29\x30\x0B\x04\xF8\x00\x4A\xED\x04\x88\x23\xF9\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0B\xE4\x00\x2D\x02\x00\x00\x05\x03\x08\x01\x01\x7F\x0A'
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'open/close={0}'.format(IsOpen) )

    def smoke_alarm(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 9, chr(IsOpen))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'smoke_alarm={0}'.format(IsOpen) )

    def smoke_trouble(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 46, chr(IsOpen))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'smoke_trouble={0}'.format(IsOpen) )

    def aux(self, IsOpen=1):
        bMask = 0xFF * IsOpen #Open all 8 auxilary inputs, according to mask 0b11111111 = 0xFF
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 17, chr(bMask)) # Magnet with Auxiliary Input
        #ser_old.send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'aux={0}'.format(IsOpen) )

    def heat_alarm(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 10, chr(IsOpen))
        #ser_old.send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'heat_alarm={0}'.format(IsOpen) )

    def heat_trouble(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 45, chr(IsOpen))
        #ser_old.send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'heat_trouble={0}'.format(IsOpen) )
        
    def supervision(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 116, chr(IsOpen))
        #ser_old.send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'supervision={0}'.format(IsOpen) )

    #Need to Clean event
    def clean_me(self):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 10, chr(2))
        #send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'clean_me' )

class violated_device(device):
    def violate(self):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 1, chr(2)) # Passive Motion ?
        #send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'violate' )

class glass_break_device(violated_device):
    def glass_break(self):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 6, chr(2)) # Glass Break
        #send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'glass_break' )

class tower_device(violated_device):
    def masking(self, IsOpen = 1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 44, chr(IsOpen))
        #send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'masking={0}'.format(IsOpen) )

class device_co(device):

    def alert(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 11, chr(IsOpen)) # CO
        #send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'alert={0}'.format(IsOpen) )

    def trouble(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 51, chr(IsOpen)) # CO Sensor Trouble
        #send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'trouble={0}'.format(IsOpen) )

class gas_device(device):

    def gas_alert(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 13, chr(IsOpen))
        #send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'gas_alert={0}'.format(IsOpen) )

    def gas_trouble(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 52, chr(IsOpen))
        #send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'gas_alert={0}'.format(IsOpen) )

class flood_device(device):
    def flood(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 16, chr(IsOpen))
        #send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'gas_alert={0}'.format(IsOpen) )


class temperature_device(device):
    iMinTemp = 0x05
    iMaxTemp = 0xF0
    aTemp = [iMaxTemp, iMinTemp]

    def freezer(self, IsOpen=1): # <-10
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 24, chr(self.aTemp[IsOpen]))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'freezer={0}'.format(IsOpen) )

    def freezing(self, IsOpen=1): # < 7
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 24, chr(self.aTemp[IsOpen]))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'freezing={0}'.format(IsOpen) )

    def cold(self, IsOpen=1): # < 19
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 24, chr(self.aTemp[IsOpen]))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'cold={0}'.format(IsOpen) )

    def hot(self, IsOpen=1): # > 28(35)
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 24, chr(self.aTemp[int(not(IsOpen))]))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'hot={0}'.format(IsOpen) )

    def freezer_trouble(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 34, chr(IsOpen))
        send_host_cmd(pkt)

    def probe(self, IsOpen=1): # ?
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 50, chr(IsOpen))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'probe={0}'.format(IsOpen) )

    def set_temperature(self, iTemperature = -40.0):
        # Temperature:  0x00 - out of range (low)
        #               0xFC - out of range (high)
        # 0x01 = -40.0, 0x02 = -39.5, 0x03 = -39.0, ... , oxFA = +84.5, 0xFB = +85.0
        TempHex = 0
        iTemperature = float(iTemperature)
        if (iTemperature > 85.0):
            TempHex = 0xFC
        elif (iTemperature >= -40.0):
            TempHex = int(((iTemperature + 40.0) * 2) + 1)
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 24, chr(TempHex))
        #send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'set_temperature={0}'.format(iTemperature) )


class arming_device(device):
    def __init__(self, serial, type):
        self.serial = serial
        self.type = type 
        #types: big_keypad, keyfob
        
        #keyfob is non-user and non-partition device but keypad is not
        #so keyfob.partitions field is always set for [] and keyfob.user_code is always set for 'AAAA'
        self.bin_user_code = '\xAA\xAA'
        self.bin_partitions = 0
        
    def specific_action(self, action = "disarm"):       
        if action.lower() == "arm_away":
            action_id = 3
        elif action.lower() == "arm_home":
            action_id = 2
        elif action.lower() == "disarm":
            action_id = 1
        elif action.lower() == "arm_latchkey":
            action_id = 4
        elif action.lower() == "arm_partition":
            action_id = 5
        elif action.lower() == "arm_quick":
            action_id = 6
        elif action.lower() == "arm_home_quick":
            action_id = 7
        elif action.lower() == "arm_instant":
            action_id = 8 
        #elif action.lower() == "check_code":
        #    action_id = 9
        else:
            print "Wrong event was specified for TAG"
            sys.exit(0)
        
        pkt = SPC.device_cmd(self.serial, self.short_id, 4, 69, chr(self.bin_partitions) + chr(action_id) + self.bin_user_code)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'arm_away' )

    def arm_away(self):
        pkt = SPC.device_cmd(self.serial, self.short_id, 4, 69, chr(self.bin_partitions)+'\x03'+self.bin_user_code)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'arm_away' )

    def arm_home(self):
        pkt = SPC.device_cmd(self.serial, self.short_id, 4, 69, chr(self.bin_partitions)+'\x02'+self.bin_user_code)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'arm_home' )

    def disarm(self):
        pkt = SPC.device_cmd(self.serial, self.short_id, 4, 69, chr(self.bin_partitions)+'\x01'+self.bin_user_code)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'disarm' )

    def panic(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 33, chr(IsOpen))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'panic' )

    def emergency(self):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 35, chr(1))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'emergency' )

    def aux_button(self):
        pkt = SPC.device_cmd(self.serial, self.short_id, 4, 74, chr(1))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'aux_button' )

    # *** TAG actions

    def tag_action(self, tag_id=0, action="away" ''',part_bitmap=0'''):
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

        packet = SPC.device_cmd(self.serial, self.short_id, 4, 73, chr(self.bin_partitions) + chr(action_id) + '\x28\x00\x00\x00\x00' + chr(tag_id) + '\x00\x00\x00')
        packet_f2 = SPC.make_packet( 0xF2, 9, packet ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'tag_action={0}'.format(action) )


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

    def set_partitions2(self,partitions):
        ''' Input parameter partitions format like "101" (Set 1st and 3th partition) '''
        self.bin_partitions = 0
        #import binascii
        #print binascii.a2b_uu("111")
        #print partitions
        for i in range(len(partitions)-1, -1, -1):
            #print '{0} - {1}'.format( i, partitions[i] )
            self.bin_partitions = self.bin_partitions | (int(partitions[i])<<i)
        #print bin(self.bin_partitions)
        #print hex(self.bin_partitions)
        #print self.bin_partitions
        
    def set_user_code(self,user_code):
        print self.__class__
        self.user_code = user_code
        self.bin_user_code = chr(int(user_code[:2],16))+chr(int(user_code[2:],16))

    def enable_partitions(self):
        pkt = SPC.device_cmd(self.serial, self.short_id, 4, 118, chr(self.h_partitions))
        #send_host_cmd(pkt)
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'enable_partitions' )

class arming_station(big_keypad):
    pass

class repeater(device):
    def __init__(self, serial):
        self.serial = serial
        self.type = device_type.repeater

    def jamming(self, IsOpen=1):
        pkt = SPC.device_cmd(self.serial, self.short_id, 5, 48, chr(IsOpen))
        packet_f2 = SPC.make_packet( 0xF2, 9, pkt ) # F2 protocol packet
        self.SendPacketTo_PortOrFile( packet_f2, 'jamming={0}'.format(IsOpen) )



if __name__ == "__main__":

    print 'main code - not used'

    #ser = ser()
    #ser.ser()

    #s = ser.ser

