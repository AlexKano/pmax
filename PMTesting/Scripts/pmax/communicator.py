#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, threading, serial, sys
import heapq
import itertools

#from common import serial_port_craft as SP
from common.prutils import hexdump, checksum, chars_to_int , Protocol, _describe_command, _make_f2_packet
from common import log
from common.protoparser import ProtoParser


'''
class EventReader(threading.Thread):
    _stop_needed = 0
    _SP = None
    _pool = None
    _Protocol = None
    def __init__(self, serial_port, pool, protocol):
        threading.Thread.__init__(self)
        #self._HPR = Protocols.host.HPR(serial_port)
        self._SP = serial_port
        #self._serial_port = serial_port
        self._pool= pool
        self._Protocol = protocol


    def run (self):
        #self._SP.ser_virt = None
        #self._SP.ser_virt = SP.serial.Serial( 'COM9', 9600, timeout=0.1 )
        #Get new packet
        while (not self._stop_needed):
            packet = self._SP.read_packet(self._Protocol)
            if (packet != None):

                self._pool.append(packet)
'''
class MessageWriter(threading.Thread):
    _stop_needed = 0
    _out_pool = None
    _port = None
    _lock = None 

    def __init__(self, serial_port, msg_pool):
        self._out_pool = msg_pool
        self._port = serial_port
        self._lock = threading.Lock()
        threading.Thread.__init__(self)

    def run(self):
        while not (self._stop_needed):
            try:
                priority, index, packet, delay_after = heapq.heappop(self._out_pool)
            except IndexError:
                time.sleep(0.01)
            else:
                #with self._lock:
                log.write("in queue: %d, pr = %d" % (len(self._out_pool), priority), "debug")
                log.write ("{0} *[TX]*: {1}".format(self._port.port, hexdump(packet)), "debug")
                self._port.write(packet)

                if delay_after:                    
                     time.sleep(delay_after)
        print 'Message Writer - End of RUN cycle'



class Reader():
    _Serial = None
    _message_pool = None
    _EventReader = None
    _Protocol = None

    def __init__(self):
        self._message_pool = []
    '''
    def start(self):
        #Checking if Reader already started
        if  (self._EventReader) and (self._EventReader.is_alive()):
            return
        self._Serial.get_serial_port().flushInput()

        #Create new empty queue
        self._message_pool = []

        #Starting listening on the port for new messages
        self._EventReader = EventReader (self._Serial, self._message_pool, self._Protocol)
        self._EventReader.start()


    def stop(self):
        if (self._EventReader.isAlive()):
            self._EventReader._stop_needed = 1
            self._EventReader.join()

        #TODO: Check if closing port and removing pool are needed
        #Closing serial port
        #self._Serial.get_serial_port().close()

        #Removing pool
        #if (self._message_pool.count > 0):
        #    del self._message_pool
    '''

    def pop_message(self, message_id = 0):
        #FIFO approach if message_id = 0
        if (self._message_pool.count <= message_id):
            return None

        return self._message_pool.pop(message_id)


    def pool_size(self):
        return len(self._message_pool)


    def get_all_messages(self):
        return self._message_pool


    def remove_message(self, index):
        self._message_pool.pop(index)

    def get_message(self, index):
        return self._message_pool[index]

    def clear_pool(self):
        del self._message_pool[:]

    #def __del__(self):
        #self.stop()
        #pass


class Writer():
    _Serial = None
    _out_pool = None
    _MessageWriter = None
    #_Protocol = None
    _stop_needed = 0

    _msg_index = None
    
    def start(self):
        #Checking if Reader already started
        if (self._MessageWriter) and (self._MessageWriter.is_alive()):
            return
        self._out_pool = []
        self._MessageWriter = MessageWriter (self._Serial, self._out_pool)
        self._MessageWriter.start()

    def stop(self):
        if (self._MessageWriter.isAlive()):
            self._MessageWriter._stop_needed = 1
            self._MessageWriter.join()
            print 'Writer stoped'

    def __init__(self):
        self._msg_index = itertools.count()
        # add lock for write operations on serial port
        # because of device instanses which send keep-alive in own thread
        self._write_lock = threading.Lock()    

    #TODO: Remove all instances of calling "write" function. Use "send" instead
    def write(self, packet):
        #TODO: Check if it works and create thread if needed
        #self._Serial.send_packet(packet)
        self._Serial.write(packet)
        log.write ("{0} [TX]: {1}".format(self._port_name, hexdump(packet)), "debug")
        # there is now description for AUTOMATION protocol for now
        # _describe_command(packet, self._Protocol.NAME, None)

    def send(self, packet, priority, delay_after):
        #with self._write_lock:
        #    self.write(packet)
        #    time.sleep(0.05)
        self.add_to_queue(packet, priority, delay_after)

    def add_to_queue(self, packet, priority, delay_after=0.5):
        if self._MessageWriter.isAlive():
            heapq.heappush(self._out_pool, (priority, self._msg_index.next(), packet, delay_after))
            return True
        log.write("Can't add message to queue - writer thread haven't been ran", "debug")    
        return False
  


# class Communicator(Reader, Writer):
class Communicator(Reader):
    SET_PARAMS = None #Dictionary of parameters to be set for different functions ("ack", "timeout", e.t.c)
    _Serial = None
    _Serial_repeater = None
    _port_name = None
    _Protocol = None
    _ProtoParser = None

    def __init__(self, serial_port, baud_rate, protocol, repiater_port = None, repiater_rate = None):
        # protocol: RF / AUTO / PGH
        #self._Serial = SP.COM(serial_port, baud_rate)
        Reader.__init__(self)
        # Writer.__init__(self)
        self._port_name = serial_port
        self._Serial = serial.Serial(serial_port, baud_rate, timeout=0.1)
        self._Serial.setRTS(False)
        self._Serial.setRTS(False)

        self._Serial.flushInput()
        self._Protocol = Protocol(protocol.upper())
        if repiater_port != None:   
            self._Serial_repeater = serial.Serial(repiater_port, repiater_rate, timeout=0.1)
        self._ProtoParser = ProtoParser(self._message_pool, self._Serial, log.write, self._Serial_repeater)

        # Writer.start(self)        
        if self._Protocol.NAME == "AUTO":
            self._ProtoParser.add_proto_handler(self.get_F2_packet)
            self._ProtoParser.add_proto_handler(self.get_F0_packet)

        if self._Protocol.NAME == "RF":
            self._ProtoParser.set_stm(0)
            self._ProtoParser.add_proto_handler(self.get_host_packet)

        self._ProtoParser.start()
        
        #TODO: Decide if auto start is needed
        #Reader.start(self)
    def stop(self):
        Writer.stop(self)
        self._ProtoParser.stop()
        self._ProtoParser.join()


    def get_F2_packet(self, bufer):
        packet = None
        if (len(bufer) >= 9):
            data_len = ord(bufer[5])
            if (data_len + 8) < (len(bufer)):
                #print("len = %d:%02X ,%02X, %02X" % (data_len, ord(bufer[0]), (ord(bufer[1]) ), (ord(bufer[data_len + 8]))))
                if (ord(bufer[0]) == 0x0D) and (ord(bufer[1]) == 0xF2) and  (ord(bufer[data_len + 8]) == 0x0A):
                    packet = bufer[:data_len + 8 + 1]
                    #log.write("{0} proto=F2 [RX]: {1}".format(self._port_name, hexdump(packet)))
                    return packet
        return None

    def get_F0_packet(self, bufer) :
        
        ack = "\x0D\xF0\x01\x43\x00\x00\x80\x40\x0A"
        # "\x0D\xF0\x02\x00\x00\x02\x36\xFF\x95\xA5\x0A"
        packet = None
        if (len(bufer) >= 9):
            if(ord(bufer[1]) == 0xF0):
                if(ord(bufer[2]) == 1):
                    #ack
                    end_byte = bufer.find('\x0A') + 1
                    if(end_byte):
                        packet = bufer[:end_byte]
                    else:
                        return None
                else:
                    #other than ack
                    data_len = ord(bufer[5])
                    if(ord(bufer[data_len + 5 + 3]) == 0x0A):
                        packet = bufer[:data_len + 5 + 3 + 1]
                        self.send(ack)
                #log.write("{0} proto=F0 [RX]: {1}".format(self._port_name, hexdump(packet)), "debug")                        
                return packet
        
        return None
#23 26 00 06 01 0C 0D 04 00 FF 00 00 00 04 05 3E 03 00 84 03 01 0C 0B A4 00 AD 00 00 00 04 03 F1 01 05 A4 0A
    def get_host_packet(self, bufer):
        packet_end = bufer.find("\x0A")
        #log.write("pgh_handler |msg:%s" % hexdump(bufer))
        if (packet_end != -1):
            #log.write("pgh_handler |EOM found")
            #packet_end += 2 # set on x90 byte
            last_byte = ord(bufer[0])
            #log.write("pgh_handler |last byte: %02X" % ord(bufer[last_byte]))
            if  (len(bufer) > last_byte) and (bufer[last_byte] == '\'):
                packet = bufer[:last_byte + 1]
                # log.write("{0} proto=HPR [RX]: {1}".format(self._port_name, hexdump(packet)), "debug")                        
                return packet
        return None



    def wait(self, commands, default_timeout = 2, not_occurences = True):
        # not_occurences - defines which result will be sent back:answer packet or command occurence counter
        if type(commands) is not list:
            #support for multiple commands to wait
            commands = [commands]
        # if cmd_byte == 0:
        cmd_byte = self._Protocol.CMD_BYTE
        timeout = default_timeout
        #Setting parameters that were passed with the function call
        if (self.SET_PARAMS != None):
            if (self.SET_PARAMS["ack"] != None):
                not_occurences = self.SET_PARAMS["ack"]
                self._EventReader._ack_needed = 0
            elif not_occurences == False:
                # we want to count packet occurences only,
                # so disable acknowledge mechanism
                self.SET_PARAMS["ack"] = False
            if(self.SET_PARAMS["timeout"] != None):
                timeout = self.SET_PARAMS["timeout"]

        if (timeout <= 0):
            return False

        log.write("Waiting for command " + ', '.join([hexdump(x) for x in commands]) +". Timeout = " + str(timeout) + " seconds")
        start_time = time.time()
        index = 0
        packet_occurences = 0
        while(time.time() - start_time < timeout):
            while (index < self.pool_size()):
                #Checking message - optional, depend on protocol
                current_message = self.get_message(index)
                #Checking if correct command found
                if (ord(current_message[cmd_byte - 1]) in commands):
                    log.write("Correct packet found: " + hexdump(current_message))
                    #_describe_command(current_message, self._Protocol.NAME, None)
                    #Removing current packet from pool
                    packet = self.pop_message(index)
                    packet_occurences += 1

                    if (not_occurences):
                        return packet
                #else:
                index += 1
            #Waiting for next message
            time.sleep(0.1)

        if (not_occurences):
            log.write("Failed to receive command [" + ', '.join([hexdump(x) for x in commands]) + "]")
            return False
        else:
            log.write("Packet [" + ', '.join([hexdump(x) for x in commands]) + "] was received: " + str(packet_occurences) + " times")
            return packet_occurences

    def send(self, packet, priority = 0, delay_after=0.2):   
        # Writer.send(self, packet, priority, delay_after)
        self._ProtoParser.send_message(packet)
        #return None


if __name__ == "__main__":
    pass

