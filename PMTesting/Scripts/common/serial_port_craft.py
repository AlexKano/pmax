#!/usr/bin/python
# -*- coding: utf-8 -*-

# serial port for security panel unit by YuriyR

import serial
import threading
import time
#import Queue
import log
from prutils import hexdump

class COM():
    _bufer = None 

    def __init__(self, COMPort, BaudRate = 9600):
        self.COMPort = COMPort

        # self.ev = {}
        self._bufer = ''
        # create stop event
        self.stop_event = threading.Event()
        # create queue
        #self.queue = Queue.Queue()

        self.open_serial_port(BaudRate)

    def open_serial_port(self, BaudRate):
        try:
            self.ser = serial.Serial( self.COMPort, BaudRate, timeout=0.1 )
            self.ser.setDTR(False)
            self.ser.setRTS(False)
        except:
            raise Exception("Serial port: " + str(self.COMPort) + " cannot be opened")


    def get_serial_port(self):
        return self.ser


    def send_packet(self, packet):
        self.ser.read(self.ser.inWaiting())

        log.write('={0}= [TX]: {1}'.format(self.COMPort, hexdump(packet)), "debug")
        self.ser.write(packet)

    
    ### for virtual serial port (com0com)

    def get_row_data(self):
        if len(self._bufer) != 0:
            data = self._bufer
            self._bufer = ''
        else:
            buffer_data_size = self.ser.inWaiting()
            if buffer_data_size == 0:
                return None
            data = self.ser.read(buffer_data_size)
            # log.write('[{0}] [RX]: {1}'.format(self.COMPort, hexdump(data)), "debug")
        return data

    def read_packet(self, Protocol, timeout = 10):
        packet = ''
        # self._bufer = ''
        stop_time = time.time() + timeout
        while time.time() < stop_time:
            data = self.get_row_data()
            if data is None:
                # problem with fake packet end:
                # 19 26 00 03 01 0A 11 A4 00 99 00 00 00 04 09 AA 07 02 80 4D 02 03 A1 0A D8 0A
                time.sleep(0.09)
                continue
            #Reading 1st byte
            packet = packet + data
            # if (len(packet) >= Protocol.MIN_PACKET_LEN) and (packet.rfind(Protocol.EOM) == len(packet) - len(Protocol.EOM)):
                #Found EOM = 0x0A and packets length is more than packet_type.MIN_PACKET_LEN
                #Checking if packet is correct
            for char_index in range(len(packet) - Protocol.MIN_PACKET_LEN):
                offset = self._check_packet(packet[char_index:], Protocol.NAME)
                if type(offset) is not bool:
                    self._bufer = packet[offset:]
                    packet = packet[char_index:char_index + offset]
                    # log.write('bufer=%s' % hexdump(self._bufer))
                    log.write('={0}= [RX]: {1}'.format(self.COMPort, hexdump(packet)), "debug")

                    return packet

                #Packet is incorrect. No byte found that corresponds to packet length
                #Continue collecting data
        #print '(def read_packet) Output due to a timeout {0} sec.'.format( timeout )
        return None

    def _check_packet(self, packet, protocol_name):
        # log.write('checking: {0}, for {1}'.format(hexdump(packet), protocol_name), "debug")
        # 0D F2 0B 00 00 0A 01 05 E9 03 00 00 0A 03 01 08 0F 02 0A
        #\x0D\xF2\x0B\x00\x00\x0A\x01\x05\x01\x00\x00\x00\x0A\x01\x01\x08\x22\x01\x0A 
        if (protocol_name == "AUTO"):
        #Protocol structure: [0x0D] [0xF2] [CMD] [0x00] [0x00] [LEN] [DATA] [CS_LOW] [CS_HI] [EOM=0x0A]
            pos = 0
            if (ord(packet[0]) != 0x0D) or (ord(packet[1]) != 0xF2):
                return False

            while pos < len(packet): # try to find all 0x0A
                offset = packet[pos:].find('\x0A')
                if offset > 0:
                    packet_end = offset + pos
                    if packet_end - 8 == ord(packet[5]):
                        # log.write("Found %s at %d" % (protocol_name, packet_end))
                        return packet_end + 1
                    pos = packet_end + 1
                else:
                    break

        #\x0D\x0A\xFC\x0B\x01\x01\x00\x00\x13\x0A\xEB\x90\x0D\x09\xFC\x00\x12\x00\x04\x1B\x0A\xEB\x90
        elif (protocol_name == "PGH"):
            #Protocol structure: [0x0D] [LEN] [ID - 2 bytes] [TYPE] [DATA] [CS] [EOM = 0x0AEB90]
            packet_end = packet.find('\x0A\xEB\x90') # 9
            if packet_end >= 0:
                packet_end += 3 # end EOM len
                if (ord(packet[0]) == 0x0D) and ((packet_end - 2) == ord(packet[1])):
                    # log.write("Found %s at %d" % (protocol_name, packet_end))
                    return packet_end
        elif (protocol_name == "RF"):
        #\x05\x01\x00\x00\x06\x0A
        #\x15\x26\x00\x05\x01\x0B\x0D\xA4\x00\x94\x00\x00\x00\x04\x05\xB9\x03\x01\x00\x00\x57\x0A
            pos = 0 
            while pos < len(packet): # try to find all 0x0A
                offset = packet[pos:].find('\x0A')
                if offset >=0:
                    packet_end = offset + pos
                #Checking if 1st byte is packet length
                    if ord(packet[0]) == (packet_end):
                        # log.write("Found %s at %d" % (protocol_name, packet_end))
                        return packet_end + 1
                    pos = packet_end + 1
                else:
                   break

        else:
            raise Exception
        # log.write("REJECTED", 'debug')
        return False


if __name__ == "__main__":
    pass
