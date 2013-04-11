#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from common import prutils, log, prutils

#cmd_folder = os.path.dirname(os.path.abspath(__file__))
#sys.path.append( cmd_folder+'\..' )

#class HPR:

def ack(status):
    # status:
    #   0x00: Message Legal
    #   0x01: Message not Recognized
    #   0x02: Message Data Invalid
    #   0x03: -unused-
    #   0x04: Buffer Full
    #   0x05: -unused-
    #   0x06: Notification Error
    #   0x07: One-Way Network
    #   0x08: Message Length Error
    #   0x09: Network Unavailable
    #   0x0A: Node Busy
    packet = prutils.make_host_packet(0x01, chr(status) + chr(0x00))
    return packet


def send_unicast_message(enable_retries, short_id, message_data_hex):
    # enable_retries:
    #   0 - MAC ACK and Retries Disabled
    #   1 - MAC ACK and  Retries Enabled
    packet = prutils.make_host_packet(0x01, chr(enable_retries) + chr(short_id) + chr(len(message_data_hex) + message_data_hex))
    return packet

def send_diagnostics(short_id, long_id, seq):
    #22 3F 0A 01 30 00 08 B5 0C 95 28 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 53 06 00 00 81 0A
    #53 06 00 00 - Supervision message (06 00 - Long ID)
    #Long is 13 bits of the real Long ID: [LSB] [MSB], 2100 = [0x34] [0x08]
    #long_id_packed = chr(long_id % 256) + chr(long_id &0xff00)/ 256
    
    long_id_packed = prutils.num_to_chars(long_id, 0, 0)[:2]
    data = chr(short_id) + chr(seq) +'\x30\x00\x08\xB5\x0C\x95\x28\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x53' + long_id_packed + '\x00'
    packet = prutils.make_host_packet(0x3F, data)
    return packet

def open_detector():
    #packet = prutils.make_host_packet(0x30, chr(enable_retries) + chr(short_id) + chr(len(message_data_hex) + message_data_hex))
    packet = "\x29\x30\x0A\x04\x3C\x00\x88\xBE\x16\x84\x0F\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0B\xE4\x00\x8E\x06\x00\x00\x05\x03\x08\x01\x01\x2A\x0A"
    return packet

def close_detector():
    packet = "\x29\x30\x0A\x06\xFC\x00\x9E\x5A\x17\x84\x05\x03\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0B\xE4\x00\x96\x06\x00\x00\x05\x03\x08\x01\x00\xAC\x0A"
    #packet = prutils.make_host_packet(0x01, chr(enable_retries) + chr(short_id) + chr(len(message_data_hex) + message_data_hex))
    return packet

def send_response_to_get_system_time():
    time = '\x89\xB8'
    packet = prutils.make_host_packet(0x43, time + '\x20')
    return packet


def update(long_id, short_id):
    packet = prutils.make_device_packet(long_id, short_id, 5, 253, chr(0))
    return packet


def association_request(long_id):
    # Real packet: 20 40 06 00 00 00 13 00 00 00 08 01 03 29 03 14 03 00 08 01 01 00 02 07 00 70 09 28 03 08 01 88 0A
    long_id = prutils.convert_longid(long_id)
    rssi = '\x13'
    tx_power = '\x00'
    request_data = '\x00'
    attached_device_information = '\x00\x08\x01\x03\x29\x03\x14\x03\x00\x08'
    manufacturing_information = '\x01\x01\x00'
    rf_module_information = '\x02\x07\x00\x70\x09\x28\x03\x08\x01'

    data = long_id + rssi + tx_power + request_data + attached_device_information + manufacturing_information + rf_module_information
    packet = prutils.make_host_packet(0x40, data)
    return packet
'''
COM2[RX]:29 26 00 06 04 2E 2F 30 31 0D 04 00 FF 00 00 00 04 05 3E 03 00 DC 05 04 2E 2F 30 31 0B 24 00 97 00 00 00 05 03 40 01 00 23 0A
09/11/12 13:29:12.523 parse 0x26:ret = {48: ['\x04\x00\xff\x00\x00\x00\x04\x05>\x03\x00\xdc\x05',
            '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00', '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00',
            '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00', '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00'],
    49: ['\x04\x00\xff\x00\x00\x00\x04\x05>\x03\x00\xdc\x05','$\x00\x97\x00\x00\x00\x05\x03@\x01\x00',
            '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00', '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00',
            '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00'],
    46: ['\x04\x00\xff\x00\x00\x00\x04\x05>\x03\x00\xdc\x05', '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00', '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00', '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00', '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00'], 47: ['\x04\x00\xff\x00\x00\x00\x04\x05>\x03\x00\xdc\x05', '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00', '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00', '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00', '$\x00\x97\x00\x00\x00\x05\x03@\x01\x00']}
'''

def extract_0x26_data(packet):
    sids = []
    dprs = []
    offset = 0
    sid_amount = ord(packet[offset])
    # print "sid amount %d" % sid_amount
    offset += 1
    for i in range(sid_amount):
        # print "sid = %02X" % ord(packet[offset])
        sids.append(ord(packet[offset])) 
        offset += 1
    length = ord(packet[offset])
    # print "data len: %d" % length
    dpr_ofst = offset + 1
    # print "first DPR: %02X" % ord(packet[dpr_ofst])
    offset = offset + length # dpr msg ends there
    tldv_len = ord(packet[dpr_ofst + 7])
    # print "tldv len: %d" % tldv_len
    if (dpr_ofst + tldv_len + 7) == offset:
        value = packet[dpr_ofst: dpr_ofst + 8 + tldv_len]
        # print "tldv = %s" % hexdump(value)
        # dprs.append(value)
        dprs.append(value)
        # dprs['seq'] = ord(packet[dpr_ofst + 2])
        # log.write("ret=%s" % str((sids, dprs)))
        return (sids, dprs)
    else:
        # print "Parse error! %d = %d" % (dpr_ofst + tldv_len + 7, offset)
        return False

def parse_0x26_cmd(packet):
    result = True
    packet = packet[4:]
    dprs_dict = {}     
    while(len(packet) >= 5):    
        # log.write("len = %d" % len(packet))
        sid_amount = ord(packet[0])
        rec_end = ord(packet[sid_amount + 1]) + 1 + sid_amount
        result = extract_0x26_data(packet)
        # log.write("result = %s" % str(result))
        if not result:
            # print "***parse error"
            continue
        packet = packet[rec_end + 1:]
        for sid in result[0]:
            # log.write("add for sid = %d" % sid)
            if not(sid in dprs_dict.keys()):
                # log.write("parse 0x26: add sid = %02X" % sid)
                dprs_dict[sid] = result[1][:]
            else:   
                dprs_dict[sid].extend(result[1])
    # log.write("parse 0x26:ret = %s" % str(dprs_dict), "debug")   
    return dprs_dict

def parse_hpr_cmd(packet):
    # return dict: {sid:[dpr1, dpr2, dpr3 ..]}
    # dpr : ['\xA4\x00\x8E\x00\x00\x00\x04\x03\xF1\x01\x02','\x04\x00\xFF\x00\x00\x00\x04\x05\x3E\x03\x00\x84\x03']
    if (ord(packet[1]) == 0x10) and (len(packet) > 4):
        ans = dict({ord(packet[3]):[packet[5:-2]]})
        # log.write("parse_hpr_cmd returned: %s" % ans)
        return ans

    elif ord(packet[1]) == 0x26:
        return parse_0x26_cmd(packet)

if __name__ == "__main__":
    pass