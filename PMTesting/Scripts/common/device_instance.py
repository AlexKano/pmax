#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import log
import threading
from time import gmtime, strftime
import itertools
from common import prutils
from common.packets import DPR_Packet
from pmax.protocols.dpr import _DeviceConfigGroups, _DeviceNames, _DeviceType, DEVICE_CONFIG_TYPE, FAKE_IMAGE


def CreateDevice(dev_type, long_id, short_id, dev_num, Procedures, ka_time_sec = 240, update_needed = 0):
    if dev_type.upper() == _DeviceNames[3]: #motion camera
        return MotionCamera(long_id, short_id, dev_num, Procedures, ka_time_sec, update_needed)
    else:
        return Device(dev_type, long_id, short_id, dev_num, Procedures, ka_time_sec, update_needed)

class KeepAlive(threading.Thread):
    _ka_time_sec = None
    #_ka_time_changed = 0
    _stop_needed = 0
    _short_id = None
    _long_id = None
    _Procedures = None


    def __init__(self, ka_time_sec, short_id, long_id, Procedures):
        threading.Thread.__init__(self)
        self._ka_time_sec = ka_time_sec
        self._short_id = short_id
        self._long_id = long_id
        self._Procedures = Procedures

    def run (self):
        #Get new packet
        while (not self._stop_needed):
            self._send_ka_message()
            self._wait_till_next_ka()
        # log.write("Shutdown %s" % repr(self))


    def _wait_till_next_ka(self):
        start_time = time.time()
        while (start_time + self._ka_time_sec > time.time()):
            if self._stop_needed:
                break #immediately stop if requested
            time.sleep(0.02)

    def _send_ka_message(self):
        if (self._Procedures.keepalive(self._short_id, self._long_id, prutils.generate_seq("hpr")) != False):
            log.write(strftime("%H:%M:%S", time.localtime()) +  " ** KA from [" + str(self._short_id) + ";" + str(self._long_id) + "] **" )
        #self._AutoProcedures.send_response_to_get_system_time()

    def _sync_ka_time(self):
        if (self._ka_time_changed):
            self._ka_time_changed = 0

    def stop(self):
        self._stop_needed = 1

class Device:
    _ka_time_sec = None
    _dev_type = None
    _short_id = None
    _long_id = None
    _dev_num = None
    _config_types = None
    _state = None

    _auto_response = True
    #TODO: Define correct states for detectors
    _states_dict = ["N/A", "Default", "Set", "Unset", "Shabat", "Walk-test", "Remote diagnostic", "Restore to set", "Restore to unset", "Local diagnostic"]

    _ka_thread = None
    _Procedures = None

    def __init__(self, dev_type, long_id, short_id, dev_num, Procedures, ka_time_sec = 240, update_needed = 0):
        # log.write('Instantiating device %s' % repr(self)) 
        self._dev_type = dev_type
        self._long_id = long_id
        self._short_id = short_id
        self._dev_num = dev_num
        self._state = 0 # Not ready
        self._Procedures = Procedures
        self.set_ka_time(ka_time_sec)
        self._ka_activity = 1
        self._dpr_seq = itertools.cycle(range(256))
        # links device type and sub-type with configuration data
        # '\x03\x01' : [0x0001, 0x0016]
        self._dev_type_code = _DeviceType[self._dev_type.upper()]
        self._config_types = _DeviceConfigGroups[self._dev_type_code]

        self.start()

    # Fix needed to be able to pickle current class (removing _ka_thread from __dict__)
    def __getstate__(self):
        updated_dict = dict(self.__dict__)
        del updated_dict['_Procedures']
        del updated_dict['_ka_thread']
        # del updated_dict['_seq']
        del updated_dict['_dpr_seq']
        return updated_dict

    def _get_config_type(self, cfg_code):
        # print "input = 0x%04X" % cfg_code 
        for lst in DEVICE_CONFIG_TYPE.values():
            if(lst[0] == cfg_code):
                return lst
        return None

    def get_network_data(self, integrity=False):
        supervision_period = 0x2D0
        enrollment_sate = 1
        data = prutils.num_to_chars(self._long_id, 4, 0) + self._dev_type_code + \
            chr(self._short_id) + chr(enrollment_sate) # + prutils.num_to_chars(supervision_period, 2, 0)
        # data = prutils.str_l(data)
        log.write("network data = %s" % prutils.hexdump(data))
        if integrity:
            return prutils.crc_PGH_20(data)
        return data

    def get_application_data(self, fn_sniffer_wait, integrity=False):
        # use request to get configuration according to device type
        config_cache = {} 
        cur_seq = 0xff
        snum = 0xff
        data = ''
        for cfg in self._config_types:
            device_config_template = self._get_config_type(cfg)
            if device_config_template is None:
                log.write("Don't know how to get the 0x%04X device configuration" % cfg) 
                return None
            dpr_type = device_config_template[1]
            # log.write("ASK FOR dpr_type = %x" % dpr_type)
            if dpr_type in config_cache.keys():
                packet = config_cache[dpr_type]
            else:
                packet = self._Procedures.request_configuration_data(self._short_id, self._long_id, dpr_type)

                # filter out retransmittions
                while snum == cur_seq:
                    packet = fn_sniffer_wait(0x10)
                    if packet == False:
                        break
                    packet = packet[5:]  # dpr only
                    dprp = DPR_Packet(packet) 
                    snum = dprp.snum.value
                    if snum == 0xff:
                        break # special case

                cur_seq = snum
                if packet :
                    config_cache[dpr_type] = packet
                    self.send_response(0x07, dprp.snum.value)

            if packet:
                dprp = DPR_Packet(packet) 
                rcv_dpr_type = ord(packet[8])
                # if dpr_type != rcv_dpr_type:
                    # log.write("wrong TLDV:%d != %d" % (dpr_type, rcv_dpr_type))
                value_len_off = dprp.data_len.offset + 2
                value_len = ord(packet[value_len_off])
                # add config to cash
                # log.write("len = %d " % value_len)
                
                add = prutils.num_to_chars(cfg, 2, 0)
                # add +=  prutils.num_to_chars(cfg, 2, 0)
                # BF [07 05 01 00 01 00 08 20]
                if len(device_config_template) > 2 :
                    # extract the tldv parameter
                    offset = device_config_template[2][0]
                    size = device_config_template[2][1]
                    tldv_data = dprp.data[offset + 2: offset + size + 2]
                    # log.write("template:%s" % device_config_template)
                    # log.write("dpr data = %s" % prutils.hexdump(dprp.data))
                    # log.write("0x%X:%d extraction: %s" % (offset, size, prutils.hexdump(tldv_data)))
                    add += chr(len(tldv_data)) + tldv_data
                # log.write("TLDV:%s => %s" % (prutils.hexdump(packet[8:11]), prutils.hexdump(add)))
                else:
                    add += chr(value_len)
                    add += packet[value_len_off + 1: value_len_off + value_len + 1]

                data += add
                # data = chr(len(data)) + data
                time.sleep(0.3)
            else:
                return None
        log.write("application data = %s" % prutils.hexdump(data))
        if integrity == True:
            if len(self._config_types) != 0:
                data = prutils.crc_PGH_20(data)
            else:
                data = 0x0000
        return data


    def set_ka_activity(self, mode):
        self._ka_activity = mode
        if self._ka_activity == 0:
            self.stop()
        else:
            self.start()

    def set_ka_time(self, ka_time_sec):
        if (self._ka_thread != None) and (self._ka_thread.isAlive()):
            self._ka_thread._ka_time_sec = ka_time_sec
            #self._ka_thread._ka_time_changed = 1
        self._ka_time_sec = ka_time_sec

    def get_ka_time(self):
        return self._ka_time_sec


    def start(self):
        self._ka_thread = KeepAlive(self._ka_time_sec, self._short_id, self._long_id, self._Procedures)
        self._ka_thread.start()
        # log.write("Starting  %s" % repr(self._ka_thread))


    def get_device_state(self):
        return self._states_dict[self._state]


    def get_device_params(self):
        #Returns [LongID, ShortID, DeviceNumber]
        return [self._long_id, self._short_id, self._dev_num]


    def stop(self):
        if (self._ka_thread.isAlive()):
            # log.write("Stopping device [%d:%d]" % (self._short_id, self._long_id))
            self._ka_thread.stop()
            self._ka_thread.join()
            # log.write("thread alive?:%s" % self._ka_thread.isAlive())

    def set_autoresponse_activity(self, auto_response):
        self._auto_response = auto_response
        # print "set_autoresponse_activity:%s" % self._auto_response

    def dispatch_message(self, dpr_list):
        if not self._auto_response:
            return None
        # log.write('Device::dispatch_message')
        # dpr_list : ['\xA4\x00\x8E\x00\x00\x00\x04\x03\xF1\x01\x02','\x04\x00\xFF\x00\x00\x00\x04\x05\x3E\x03\x00\x84\x03']        
        response_amount = 0
        for dpr_msg in dpr_list:
            seq = ord(dpr_msg[2])
            mcode = ord(dpr_msg[6])
            tldv_len = ord(dpr_msg[7])
            tldv = dpr_msg[7 : 8 + tldv_len]
            log.write("device [%d:%d] got mcode[%d] type=%02X, tldv = %s, seq = %d" % \
                (self._short_id, self._long_id, mcode, ord(tldv[1]), prutils.hexdump(tldv), seq), "debug")
            if mcode == 0x04:
                # response_amount += 1
                if tldv[1] == '\xF1':
                    # log.write("set device state")
                    self._state = prutils.chars_to_int(tldv[3:].strip())
                    self.send_response(0x06, seq) #, response_amount)
                    # log.write("device [%d:%d]:state = %d, seq = %d" % (self._short_id, self._long_id, self._state, seq))
                elif tldv[1] == '\x3E':
                    # log.write("set notification period")
                    response_amount -= 1
                    notification_period = ord(tldv[3])
                    #log.write('** hello from [%d:%d] **' % (self._short_id, self._long_id))
                    self.send_hello(seq, notification_period)
                    #self._Procedures.hello(self._long_id, self._short_id, 0, notification_period)
                elif tldv[1] == '\xFC':
                    # log.write("set update config")
                    self.send_response(0x06, seq) #, response_amount)
                    # response comes first !!!
                    #response_amount -= 1
                    log.write('** update from [%d:%d] **' % (self._short_id, self._long_id))
                    self._Procedures.update(self._long_id, self._short_id)
                else:
                    # other set commands
                    self.send_response(0x06, seq) # , response_amount)
                # if response_amount > 0:
                    
            elif mcode == 5:
                if tldv[1] == '\x40': # hello
                    self.send_hello()
                # confirm to report
                self.send_response(0x07, seq)



    def send_response(self, mcode, seq=0xFF, amount=1, notification_period=0, state=0, return_packet=False):
        if(mcode == 0x06):
            log.write('** response from [%d:%d] **' % (self._short_id, self._long_id))
        elif(mcode == 0x07):
            log.write('** confirm from [%d:%d] **' % (self._short_id, self._long_id))
        if amount > 1:
            log.write("--multiply--: %d" % amount)
        # state: 0 - OK, 1 .. see device protocol
        # prepare device protocol
        #print type(state)
        state = chr(state)
        if seq == 0xFF:
            seq = self._dpr_seq.next()
        ser_num = prutils.convert_longid(int(self._long_id))[:3]
        mdata_value = ''
        # mdata_value = chr(mcode) + chr(len(state)) + state
        for i in range(amount):
            mdata_value += chr(len(state)) + state
        mdata_value = chr(mcode) + mdata_value

        device_packet = '\x14\x00' + chr(seq) + ser_num + mdata_value

        # prepare host protocol
        #final_hop_info = '\x00' * 11
        final_hop_info = '\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00'
        relaying_repeater_ID = 0
        repeater_hop_info = '\x00' * 11
        data = chr(self._short_id) + chr(prutils.generate_seq("hpr")) + chr(0x30 + notification_period) + final_hop_info + chr(relaying_repeater_ID)\
         + repeater_hop_info + prutils.str_l(device_packet)
        cmd = 0x30
        data = chr(cmd) + data
        cmd_l = 2 + len(data)
        data = chr(cmd_l) + data
        host_protocol_message = data + prutils.crc16(data)[0] + '\x0A'
     
        packet = prutils._make_f2_packet( host_protocol_message )

        #self._Procedures._Communicator.add_to_queue(packet, 0, 5)
        if return_packet == False:
            # self.prepare_transmitter()
            self._Procedures._Communicator.send(packet)
        else:
            return packet

    def send_hello(self, seq=0xFF, notification_period=0):
        log.write('** hello from [%d:%d] **' % (self._short_id, self._long_id))

        self._Procedures.hello(self._long_id, self._short_id, 0, notification_period)
        return 
        ser_num = prutils.convert_longid(int(self._long_id))[:3]
        mcode = 5
        mdata_type = 64
        mdata_value = chr(0)
        if seq == 0xFF:
            seq = self._dpr_seq.next()
        mdata = chr(mcode) + prutils.str_l( chr(mdata_type) + prutils.str_l(mdata_value) )
        device_packet = '\xE4\x00' + chr(seq) + ser_num + mdata

        # prepare host protocol
        #final_hop_info = '\x00' * 11
        final_hop_info = '\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00'
        relaying_repeater_ID = 0
        repeater_hop_info = '\x00' * 11
        #data = chr(short_id) + '\x01\xF8' + final_hop_info + chr(relaying_repeater_ID) + repeater_hop_info + str_l(device_packet)
        data = chr(self._short_id) + chr(prutils.generate_seq('hpr')) + chr(0x30 + notification_period) + final_hop_info + chr(relaying_repeater_ID) + repeater_hop_info + prutils.str_l(device_packet)
        cmd = 0x30
        data = chr(cmd) + data
        cmd_l = 2 + len(data)
        data = chr(cmd_l) + data
        host_protocol_message = data + prutils.crc16(data)[0] + '\x0A'
        #TODO: Use "make_host_packet" function to create device packet
        #host_protocol_message = make_host_packet( 0x30,  data)

        #preparing packet to send
        #print hexdump(host_protocol_message)
        packet = host_protocol_message
        packet = prutils._make_f2_packet( host_protocol_message )
        # self.prepare_transmitter()
        self._Procedures._Communicator.send(packet, 9)

class MotionCamera(Device):

    film_id = 12
    film_type = 0
    index = 0x7d
    message_confirmed = False 
    time_stamp = 0
    prev_seq = 0

    def __init__(self, long_id, short_id, dev_num, Procedures, ka_time_sec, update_needed):
        self._dev_type = _DeviceNames[3]
        Device.__init__(self, self._dev_type, long_id, short_id, dev_num, Procedures, ka_time_sec, update_needed)
        # delete source device
        # if device._dev_type != _DeviceNames[MOTION_CAMERA]:
        #     log.write("Incorrect device for motion camera")
        self.image_data = FAKE_IMAGE
        self.crc16 = prutils.chars_to_int(prutils.crc16(self.image_data)) # !!!??
        self.file_size = len(self.image_data)
        self.row = 1
        self.zone = 255
        self.files_amount = 10


    def report_camera_detection_event(self, index):
        log.write("Camera reports event: index = 0x%02X" % index)
        self._Procedures.report_camera_detection_event(self._long_id, self._short_id, index)

    def report_film_info(self, film_id, index, files_amount=15, zone=255, time_stamp=0):
        log.write("Camera reports FILM info: film_id = 0x%02X, index = 0x%02X" % (film_id, index))
        self._Procedures.report_film_info(self._long_id, self._short_id, self.film_id, self.index, self.files_amount, self.zone, self.time_stamp)

    def report_file_info(self, film_type, film_id, file_size, row, crc, index, zone=255, time_stamp=0, sequence=-1):
        log.write("Camera reports FILE info: film_id = 0x%02X, index = 0x%02X, row = 0x%02X" % (film_id, index, row))
        self._Procedures.report_file_info(self._long_id, self._short_id, self.film_type, self.film_id, file_size , self.row, self.row, self.row - 1, crc, self.index, self.zone, 0, sequence)

    def send_file_body(self, image_data, row): # reply with file body
        log.write("Camera sends file body: row = 0x%02X" % row)
        self._Procedures.send_file_body(self._long_id, self._short_id, self.image_data, self.film_id, row)

    def prepare_film(self, film_id, index, files_amount, zone):
        self.files_amount = files_amount
        self.zone = zone
        self.film_id = film_id
        self.index = index
        # self.message_confirmed = False
        self.report_camera_detection_event(self.index)
        # while (not self.message_confirmed):
        #     pass
        # log.write("Event report from camera [%d:%d] confirmed" % (self._short_id, self._long_id))

        time.sleep(10)
        self.report_film_info(self.film_id, self.index, self.files_amount, self.zone, self.time_stamp)
        self.set_autoresponse_activity(True)

    def prepare_any_film(self):
        inc = lambda p: ((p + 1) & 0xff) 

        self.index = inc(self.index)
        self.film_id = inc(self.film_id)
        self.time_stamp = int(time.time())
        self.report_camera_detection_event(self.index)
        time.sleep(10)
        self.send_hello()
        self.report_film_info(self.film_id, self.index, self.files_amount, self.zone, self.time_stamp)

    def report_last_film_info(self):
        self.report_film_info(self.film_id, self.index, self.files_amount, self.zone, self.time_stamp)        

    def dispatch_message(self, dpr_list):
        # 24 00 00 00 00 00 02 04 B5 02 0D 01
        if not self._auto_response:
            return None
        # log.write('got [%d] dpr  messages: %s' % (len(dpr_list), dpr_list),  "console")
        for dpr_msg in dpr_list:
            # if len(dpr_msg) < 3 : return None
            seq = ord(dpr_msg[2])
            # filter out wrong messages
            if seq !=0 and seq == self.prev_seq:
                log.write('Got repetition of command')
                # continue
            seq = self.prev_seq

            mcode = ord(dpr_msg[6])
            tldv_len = ord(dpr_msg[7])
            tldv = dpr_msg[7 : 8 + tldv_len]
            tldv_type = ord(tldv[1])
            log.write("camera [%d:%d] got mcode[%d] type=%02X, tldv = %s, seq = %d" % \
                (self._short_id, self._long_id, mcode, tldv_type, prutils.hexdump(tldv), seq))
            # FIXME: snum !!!!
            if mcode    == 2: # GET 
                if tldv_type == 0xB5:   # file info
                    requested_film_id = ord(tldv[3])
                    requested_row = ord(tldv[4])
                    log.write("Requested file info:film id=0x%02X, row=0x%02X" % (requested_film_id, requested_row))
                    self.report_file_info(self.film_type, self.film_id, self.file_size, self.row, self.crc16, self.index, self.zone, 0, seq)
                    dpr_list.remove(dpr_msg)

            elif mcode  == 9: # file request - ONLY IF File info request was before
                requested_film_id = ord(tldv[1])
                requested_row = ord(tldv[2])
                log.write("Requested for FILE, film id=%d, row=%d" % (requested_film_id, requested_row))
                requested_chunk_size = ord(tldv[3])
                if self.film_id != requested_film_id:
                    log.write("Wrong requested film id:%d" % requested_film_id)
                self.send_file_body(self.image_data, requested_row)
                self.row += 1
                if self.row == self.files_amount:
                    self.set_autoresponse_activity(False)
                    self.row = 0
                dpr_list.remove(dpr_msg)

            elif mcode  == 7: # confirm
                if tldv_len == 1 and ord(tldv[1]) == 0x00: # OK
                    # Confirmationion must be check on HPR sequence level
                    log.write("Confirmation")
                    self.message_confirmed = True
                dpr_list.remove(dpr_msg)


        # if message not processed run default dispatcher 
        if(len(dpr_list)):
            Device.dispatch_message(self, dpr_list)




if __name__ == "__main__":
    pass