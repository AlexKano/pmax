#!/usr/bin/env python

import log, itertools
from config import BASE_PATH

class Protocol():
    NAME = None
    NUMBER = None
    CMD_BYTE = None
    MIN_PACKET_LEN = None
    EOM = None

    def __init__(self, protocol = "RF"):    
        if (protocol == "RF"):
            self.NAME = "RF"
            #TODO: Define protocol number
            self.NUMBER = None
            self.CMD_BYTE = 2
            self.MIN_PACKET_LEN = 5
            self.EOM = "\x0A"
        elif (protocol == "AUTO"):
            self.NAME = "AUTO"
            self.NUMBER = 0xF2
            self.CMD_BYTE = 3
            self.MIN_PACKET_LEN = 9
            self.EOM = "\x0A"
        elif (protocol == "PGH"):
            self.NAME = "PGH"
            self.NUMBER = None
            self.CMD_BYTE = 5
            self.MIN_PACKET_LEN = 9
            self.SOM = "\x0D"
            self.EOM = "\x0A\xEB\x90"
            self.REPEATS = 10
        #else:
        #    log.write("Incorrect protocol type: " + str(protocol))
def custom_format_field(name, value):
    if name == 'Long ID':
        return hexdump(value[::-1]).replace(" ", "")

    return None #this function doesn't format this field, use default formatting

def process_subtree(packet, template, dict_root, subtree = False):
    description = ''
    position = 0
    length = 0
    value = 0

    for key in template.keys():

        format = "\n\t{0:.<40}"
        #do we process subfield?
        if subtree:
            format = "\n\t{0:.<30}"

        #already was added to output string
        if key == 'name': continue

        #try to find length of the field
        if 'length' in template[key].keys():
            #print "found length"
            length = template[key]['length']
            #is length was defined at previous field?
            if (type(length) is str) and ('[prev-data]' in length):
                for p in length.split('*'):
                    amount = p.strip()
                    if amount == '[prev-data]':
                        length = value
                        if type(length) is str:
                        #length.strip()
                            length = hexdump_to_int(length)
                            continue
                    if(amount):
                        amount = int(amount)
                        length = length * amount
                        
        if (length != 0) and ('template' in template[key].keys()):
            #there is a reference to another dictionary
            template_key = template[key]['template']
            if template_key in dict_root.keys():
                description += "\n\t{0:<40}".format(key)
                description += process_subtree(packet[position:], dict_root[template_key], dict_root, True)

                position += length
                continue    #no necessary to out dump for subfield

        description += format.format(key)
        #try format with specialized function

        value = custom_format_field(key, packet[position:position + length])
        if value == None:
        #the formatting wasn't done, use default way
            if 'values' in template[key].keys():
                #print "found values"
                value_dict = template[key]['values']
                #print "value dict:" + str(template[key]['values'])
                if type(value_dict) is str:
                    #key values has a reference to another dict key
                    value_dict = dict_root[value_dict]
                if length == 1 :
                    if ord(packet[position]) in value_dict.keys():
                        value = value_dict[ord(packet[position])]
                    else:
                        value = ord(packet[position])
            else:
                #if length == 1:
                #    value = ord(packet[position])
                #elif length == 2:
                #    value = chars_to_int(packet[position : position + length])
                #else:
                value = hexdump(packet[position : position + length])
        #collect data to string
        description += ' {0}'.format(str(value))
        #shift position
        position += length
    return description


def _describe_command(packet, protocol, describe_root_dict):
    if (protocol.NAME != "PGH"):
        return None

    describing_text = ''

    cmd = ord(packet[protocol.CMD_BYTE - 1])
    if cmd not in describe_root_dict.keys():
        log.write ("The command has no description" , "console")
        return None

    describing_text += '>>>>  {0}:'.format(describe_root_dict[cmd]['name'])
    describing_text += str(process_subtree(packet[protocol.CMD_BYTE:], describe_root_dict[cmd], describe_root_dict))
    describing_text += "\n"
    log.write(describing_text)

def fromhex(packet):
    hex_packet = ''
    for byte in packet.split(" "):
        hex_packet += chr(int(byte, 16))
    return hex_packet

def hexdump(s):
    if (type(s) is int):
        s = chr(s)
    elif (s is None):
        return 'NONE'
    return ' '.join(["%02X" % ord(i) for i in s ])

def hexdump_to_int(s):
    res = 0
    cnt = 0
    for a in s.split(' '):
            res += (int(a,16))<<(8*cnt)
            cnt += 1
    return res

def chars_to_int(data):
    return int(hexdump(data[::-1]).replace(" ", ""), 16)

def num_to_chars(number, length = 0 , reverse = 1):
    result = ''

    #Converting HEX number
    if (type(number) is not int) and (type(number) is not long):
        # print type(number)
        number = int(number, 0)
    if (length == 0):
        if (number == 0):
            return chr(number)

        while (number > 0):
            result += chr(number % 256)
            number /= 256
    else:
        for i in range(length):
            result += chr(number % 256)
            number /= 256

    #Returning reverse number
    if reverse: return result [::-1]
    return result


def str_to_chars(string_bitmap):
    chars_bitmap = ''
    for num in string_bitmap:
        num = num.upper()
        if (ord(num) >= ord("A")) and (ord(num) <= ord("F")):
            num = "0x" + num
        chars_bitmap += num_to_chars(int(num,0))

    return chars_bitmap

def str_to_bcd(string):
    if(not string.isdigit()):
        return None
    result = ''
    byte = 0
    length = len(string)
    if length > 8:
        length = 8
    for i in range(length):
        if (i+2)%2 == 0:
            byte |= int(string[i])<<4
        else:
            byte |= int(string[i])
            result += chr(byte)
            byte = 0
    if byte != 0:
        byte |= 0x0F
        result += chr(byte)
    return result

def reverse_bytes(packet):
    if (type(packet) is not str):
        packet = num_to_chars(packet)

    return packet[::-1]


def str_l(s):
    return chr(len(s)) + s


def crc16(data):
    crc = 0
    for p in data:
        crc += ord(p)
    return chr(crc & 0x00ff) + chr((crc & 0xff00)>>8)


def checksum(data):
    cs = 0
    for p in data:
        cs += ord(p)
    return chr(cs & 0x00ff)

def crc16_F0(data):
    CRC_TAB = (
        0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7,
        0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
        0x1231, 0x0210, 0x3273, 0x2252, 0x52B5, 0x4294, 0x72F7, 0x62D6,
        0x9339, 0x8318, 0xB37B, 0xA35A, 0xD3BD, 0xC39C, 0xF3FF, 0xE3DE,
        0x2462, 0x3443, 0x0420, 0x1401, 0x64E6, 0x74C7, 0x44A4, 0x5485,
        0xA56A, 0xB54B, 0x8528, 0x9509, 0xE5EE, 0xF5CF, 0xC5AC, 0xD58D,
        0x3653, 0x2672, 0x1161, 0x0630, 0x76D7, 0x66F6, 0x5695, 0x46B4,
        0xB75B, 0xA77A, 0x9719, 0x8738, 0xF7DF, 0xE7FE, 0xD79D, 0xC7BC,
        0x48C4, 0x58E5, 0x6886, 0x78A7, 0x0840, 0x1861, 0x2802, 0x3823,
        0xC9CC, 0xD9ED, 0xE98E, 0xF9AF, 0x8948, 0x9969, 0xA90A, 0xB92B,
        0x5AF5, 0x4AD4, 0x7AB7, 0x6A96, 0x1A71, 0x0A50, 0x3A33, 0x2A12,
        0xDBFD, 0xCBDC, 0xFBBF, 0xEB9E, 0x9B79, 0x8B58, 0xBB3B, 0xAB1A,
        0x6CA6, 0x7C87, 0x4CE4, 0x5CC5, 0x2C22, 0x3C03, 0x0C60, 0x1C41,
        0xEDAE, 0xFD8F, 0xCDEC, 0xDDCD, 0xAD2A, 0xBD0B, 0x8D68, 0x9D49,
        0x7E97, 0x6EB6, 0x5ED5, 0x4EF4, 0x3E13, 0x2E32, 0x1E51, 0x0E70,
        0xFF9F, 0xEFBE, 0xDFDD, 0xCFFC, 0xBF1B, 0xAF3A, 0x9F59, 0x8F78,
        0x9188, 0x81A9, 0xB1CA, 0xA1EB, 0xD10C, 0xC12D, 0xF14E, 0xE16F,
        0x1080, 0x00A1, 0x30C2, 0x20E3, 0x5004, 0x4025, 0x7046, 0x6067,
        0x83B9, 0x9398, 0xA3FB, 0xB3DA, 0xC33D, 0xD31C, 0xE37F, 0xF35E,
        0x02B1, 0x1290, 0x22F3, 0x32D2, 0x4235, 0x5214, 0x6277, 0x7256,
        0xB5EA, 0xA5CB, 0x95A8, 0x8589, 0xF56E, 0xE54F, 0xD52C, 0xC50D,
        0x34E2, 0x24C3, 0x14A0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
        0xA7DB, 0xB7FA, 0x8799, 0x97B8, 0xE75F, 0xF77E, 0xC71D, 0xD73C,
        0x26D3, 0x36F2, 0x0691, 0x16B0, 0x6657, 0x7676, 0x4615, 0x5634,
        0xD94C, 0xC96D, 0xF90E, 0xE92F, 0x99C8, 0x89E9, 0xB98A, 0xA9AB,
        0x5844, 0x4865, 0x7806, 0x6827, 0x18C0, 0x08E1, 0x3882, 0x28A3,
        0xCB7D, 0xDB5C, 0xEB3F, 0xFB1E, 0x8BF9, 0x9BD8, 0xABBB, 0xBB9A,
        0x4A75, 0x5A54, 0x6A37, 0x7A16, 0x0AF1, 0x1AD0, 0x2AB3, 0x3A92,
        0xFD2E, 0xED0F, 0xDD6C, 0xCD4D, 0xBDAA, 0xAD8B, 0x9DE8, 0x8DC9,
        0x7C26, 0x6C07, 0x5C64, 0x4C45, 0x3CA2, 0x2C83, 0x1CE0, 0x0CC1,
        0xEF1F, 0xFF3E, 0xCF5D, 0xDF7C, 0xAF9B, 0xBFBA, 0x8FD9, 0x9FF8,
        0x6E17, 0x7E36, 0x4E55, 0x5E74, 0x2E93, 0x3EB2, 0x0ED1, 0x1EF0
    )

    cs = 0
    for ch in data:
        v1 = ((cs>>8)&0xff)^ord(ch)
        cs = ((cs>>8)&0xffff)^CRC_TAB[v1]
    return cs
'''
#define POLYNOMIAL                    0x8005 // CRC-16-IBM polynomial.
#define CRC_MSB                       0x8000

/*******************************************************************************
**
**     Function: calculateCRC16
**      Returns: 16 bit CRC value
**   Parameters: *pData - pointer to the data
**               length - length of the data to compute
**               crc    - Initial CRC value. (usually 0xFFFF)
**  Description: Calculates a 16 bit CRC.  The polynomial is defined in CRC.H.
**
*******************************************************************************/
UINT16 calculateCRC16(UINT8 * pData, UINT16 length, UINT16 crc)
{
   UINT8 bitIndex;
   UINT8 dataValue;
   UINT16 lengthIndex;
   UINT16 bit;

   for(lengthIndex = 0; lengthIndex < length; lengthIndex++)
   {
      dataValue = *pData++;
      for(bitIndex = 0x80; bitIndex; bitIndex >>= 1)
      {
         bit = crc & CRC_MSB;
         crc <<= 1;
         if(dataValue & bitIndex)
         {
            bit ^= CRC_MSB;
         }
         if(bit)
         {
            crc ^= POLYNOMIAL;
         }
      }
   }
   return(crc);
}
'''
def crc_PGH_20(data, inital_crc = 0xFFFF):
    crc = inital_crc
    for byte in data:
        byte = ord(byte)
        for _bit_index in range(7, -1, -1): # 7, 6, 5, .. 0
            bit_index = (1 << _bit_index )  # 128, 64, 32, .. 1 
            bit = crc & 0x8000
            crc <<= 1
            crc = (crc & 0xFFFF)
            if (byte & bit_index) != 0:
                bit ^= 0x8000
            if bit != 0:
                crc ^= 0x8005
            # print "step=%d, crc=%d" % (bit_index, crc)
    return crc



def convert_longid(long_id):
    #if not id>>13==0: print "Improper device id"
    serial=''
    for i in range(4):
        c = 0xff & long_id
        long_id = long_id>>8
        serial = serial + chr(c)
    return serial

class Sequence:
    _seq = 0
    _cur_val = 0
    _len = None

    def __init__(self, length):
        self._len = length

    def reset(self):
        self._seq = 0
        self._cur_val = 0
        
    def get_new(self):
        # first run after simulator start or reset
        if(self._seq == 0):
            self._seq = itertools.cycle(range(self._len))
            self._cur_val = self._seq.next()
            return self._cur_val
        else:
            self._cur_val = self._seq.next()
            # print "cur_val = %d" % self._cur_val
            if self._cur_val == 0:
                self._cur_val = self._seq.next()
            return self._cur_val

    def get_cur(self):
        return self._cur_val


SequenceDPR = Sequence(256)
SequenceHPR = Sequence(8)


def generate_seq(method="dpr"):
    global SequenceHPR
    global SequenceDPR
    #TODO: Change seq file with global variable
    '''    
    sSeqPath = BASE_PATH + "\seq"
    try:
        f = open(sSeqPath, "r")
        seq = int(f.readline())
        f.close()
    except:

    new_seq = Sequence.next()
    if new_seq == 0:
        new_seq = 1
    
    try:
        # Writing new "seq" to file
        f = open(sSeqPath, "w")
        f.write("%d" % new_seq)
        f.close()
    except:
        log.write("Please, unset read only for sequence file %s" % sSeqPath , "debug")
    '''
    if method == "hpr":
        return SequenceHPR.get_new()
    else:
        return SequenceDPR.get_new()

def make_pgh_packet(type, data = '', message_id = 256):
    # Format: [SOM=0x0D] [Length] [ID = 2 bytes] [Type] [Data] [CS] [EOM=0x0AEB90]
    if (message_id == 0):
        message_id = generate_seq()

    packet = chr(message_id / 256) + chr(message_id % 256) + chr(type) + data
    #Counting length
    packet = chr(len(packet) + 4) + packet # 4 = last bytes: CS + EOM
    #Counting CS
    packet += checksum(packet)
    #Adding SoM
    packet = '\x0D' + packet
    #Adding EOM
    packet = packet + '\x0A\xEB\x90'

    return packet
def make_f0_packet(cmd, test, data=''):
    data = chr(test) + data
    packet = '\xF0' + chr(cmd) + '\x00\x00' + chr(len(data)) + data
    packet = '\x0D' + packet + num_to_chars(crc16_F0(packet), 2, 0) + '\x0A'
    return packet

def make_host_packet(type, data = '', wrap_with_f2 = True):
    # Format: LEN, TYP (0x00 - 0xFF), DATA, CS, EOM (0x0A)

    packet = chr(type) + data
    #print hexdump(packet)
    #Counting length
    packet = chr(len(packet) + 2) + packet # 2 = last bytes: CS + EOM
    #Counting CS
    packet += checksum(packet)
    #Adding EOM
    packet += '\x0A'

    #FIXME: Create config parameter to define if RF need to be sent via Auto protocol
    if (wrap_with_f2):
        packet = _make_f2_packet(packet, 0x09)

    return packet

# tldv_list -> [ {19:'\x7e\x03'}, {5:\x00} ] - without field size
def make_device_packet_multitldv(long_id, short_id, mcode, tldv_list, notification_period=0,\
     retry_protect=1, one_shot=1, ack_request=1, ack=0, protocol_type=4, sequence=-1):
    # sequence = -1 means that it is got automaticaly, any other  - sequence value
    # prepare device protocol
    if sequence == -1:
        dpr_seq = generate_seq('dpr')
    else:
        dpr_seq = sequence

    info = ((retry_protect<<7)&0xff) | ((one_shot<<6)&0xff) | ((ack_request<<5)&0xff) | ((ack<<4)&0xff) | (protocol_type&0x0f)
    ser_num = convert_longid(int(long_id))[:3]
    mdata = ''
    for value in tldv_list:
        mdata += chr(value.keys()[0]) + str_l(value.values()[0])
    mdata = chr(mcode) + str_l(mdata)
    device_packet = chr(info) + '\x00' + chr(dpr_seq) + ser_num + mdata

    # prepare host protocol
    #final_hop_info = '\x00' * 11
    final_hop_info = '\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00'
    relaying_repeater_ID = 0
    repeater_hop_info = '\x00' * 11
    #data = chr(short_id) + '\x01\xF8' + final_hop_info + chr(relaying_repeater_ID) + repeater_hop_info + str_l(device_packet)
    # data = chr(short_id) + '\x00' + chr(0x30 + notification_period) + final_hop_info + chr(relaying_repeater_ID) + repeater_hop_info + str_l(device_packet)
    data = chr(short_id) + chr(generate_seq('hpr')) + chr(0x30 + notification_period) + final_hop_info + chr(relaying_repeater_ID) + repeater_hop_info + str_l(device_packet)
    cmd = 0x30
    data = chr(cmd) + data
    cmd_l = 2 + len(data)
    data = chr(cmd_l) + data
    host_protocol_message = data + crc16(data)[0] + '\x0A'
    #TODO: Use "make_host_packet" function to create device packet
    #host_protocol_message = make_host_packet( 0x30,  data)

    #preparing packet to send
    #print hexdump(host_protocol_message)
    packet = host_protocol_message
    packet = _make_f2_packet( host_protocol_message )

    return packet


def make_device_packet(long_id, short_id, mcode, mdata_type, mdata_value, notification_period=0,\
     retry_protect=1, one_shot=1, ack_request=1, ack=0, protocol_type=4, sequence=-1):
    # sequence = -1 means that it is got automaticaly, any other  - sequence value
    # prepare device protocol
    if sequence == -1:
        dpr_seq = generate_seq('dpr')
    else:
        dpr_seq = sequence

    info = ((retry_protect<<7)&0xff) | ((one_shot<<6)&0xff) | ((ack_request<<5)&0xff) | ((ack<<4)&0xff) | (protocol_type&0x0f)
    ser_num = convert_longid(int(long_id))[:3]
    mdata = chr(mcode) + str_l( chr(mdata_type) + str_l(mdata_value) )
    device_packet = chr(info) + '\x00' + chr(dpr_seq) + ser_num + mdata

    # prepare host protocol
    #final_hop_info = '\x00' * 11
    final_hop_info = '\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00'
    relaying_repeater_ID = 0
    repeater_hop_info = '\x00' * 11
    #data = chr(short_id) + '\x01\xF8' + final_hop_info + chr(relaying_repeater_ID) + repeater_hop_info + str_l(device_packet)
    # data = chr(short_id) + '\x00' + chr(0x30 + notification_period) + final_hop_info + chr(relaying_repeater_ID) + repeater_hop_info + str_l(device_packet)
    data = chr(short_id) + chr(generate_seq('hpr')) + chr(0x30 + notification_period) + final_hop_info + chr(relaying_repeater_ID) + repeater_hop_info + str_l(device_packet)
    cmd = 0x30
    data = chr(cmd) + data
    cmd_l = 2 + len(data)
    data = chr(cmd_l) + data
    host_protocol_message = data + crc16(data)[0] + '\x0A'
    #TODO: Use "make_host_packet" function to create device packet
    #host_protocol_message = make_host_packet( 0x30,  data)

    #preparing packet to send
    #print hexdump(host_protocol_message)
    packet = host_protocol_message
    packet = _make_f2_packet( host_protocol_message )

    return packet

def make_device_packet_without_type(long_id, short_id, mcode, mdata_value, notification_period=0, listen_mode=0,\
     retry_protect=1, one_shot=1, ack_request=1, ack=0, protocol_type=4, sequence=-1):
    # sequence = -1 means that it is got automaticaly, any other  - sequence value
    # prepare device protocol
    if sequence == -1:
        dpr_seq = generate_seq('dpr')
    else:
        dpr_seq = sequence

    info = ((retry_protect<<7)&0xff) | ((one_shot<<5)&0xff) | ((ack_request<<5)&0xff) | ((ack<<4)&0xff) | (protocol_type&0x0f)
    ser_num = convert_longid(int(long_id))[:3]
    mdata = chr(mcode)  + str_l(mdata_value)
    device_packet = chr(info) + '\x00' + chr(dpr_seq) + ser_num + mdata

    # prepare host protocol
    #final_hop_info = '\x00' * 11
    final_hop_info = '\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00'
    relaying_repeater_ID = 0
    repeater_hop_info = '\x00' * 11
    #data = chr(short_id) + '\x01\xF8' + final_hop_info + chr(relaying_repeater_ID) + repeater_hop_info + str_l(device_packet)
    # data = chr(short_id) + '\x00' + chr(0x30 + notification_period) + final_hop_info + chr(relaying_repeater_ID) + repeater_hop_info + str_l(device_packet)
    data = chr(short_id) + chr(generate_seq('hpr')) + chr( 0xC0 + 0x30 + notification_period + (listen_mode<<3)) + final_hop_info + chr(relaying_repeater_ID) + repeater_hop_info + str_l(device_packet)
    cmd = 0x30
    data = chr(cmd) + data
    cmd_l = 2 + len(data)
    data = chr(cmd_l) + data
    host_protocol_message = data + crc16(data)[0] + '\x0A'
    #TODO: Use "make_host_packet" function to create device packet
    #host_protocol_message = make_host_packet( 0x30,  data)

    #preparing packet to send
    #print hexdump(host_protocol_message)
    packet = host_protocol_message
    packet = _make_f2_packet( host_protocol_message )

    return packet






def _make_f2_packet(data, f2_cmd = 9, protocol = 0xF2):
    packet = chr(protocol & 0xff) + chr(f2_cmd & 0xff) + '\x00\x00' + str_l(data)
    crc = crc16(packet)
    packet = '\x0D' + packet + crc + '\x0A'
    return packet


def corrupt_packet(packet, byte_num, value = 0x00):
    packet = packet[:byte_num] + chr(value) + packet[byte_num + 1:]
    return packet


if __name__ == "__main__":
    pass
