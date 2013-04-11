#!/usr/bin/python
# -*- coding: utf-8 -*-

from common import prutils
from pmax.protocols import dpr
from pmax.protocols import hpr
from pmax.protocols.dpr import _DeviceType
from common import log
import time
import config


class RF:
    _Communicator = None

    def __init__(self, RFCommunicator):
        self._Communicator = RFCommunicator

    def is_AUTO_port_ready(self):
        if self._Communicator:
            return True
        else:
            log.write("Automation port hasn't been opened")
            return False
        
    def request_configuration_data(self, short_id, long_id, parameter):
        if (not self.is_AUTO_port_ready()): return
        final_hop_info = '\x00\x00\x00\x00\x80\x00\x84\x00\x00\x00\x00'
        repeater_hop_info = '\x00' * 12
        dpr_seq = prutils.generate_seq('dpr')
        hpr_seq = prutils.generate_seq('hpr')
        if parameter == 0x46:
            data = chr(short_id) + chr(hpr_seq) + chr(0xF8) + final_hop_info  + repeater_hop_info\
                + prutils.str_l('\x64\x00' + chr(dpr_seq) + prutils.num_to_chars(long_id, 3, 0) + "\x02\x02" + chr(parameter) + '\x00')
        else:    
            data = chr(short_id) + chr(hpr_seq) + chr(0x30) + final_hop_info  + repeater_hop_info\
                + prutils.str_l('\x64\x00' + chr(dpr_seq) + prutils.num_to_chars(long_id, 3, 0) + "\x02\x02" + chr(parameter) + '\x00')

        packet = prutils.make_host_packet(0x30, data) 
        self._Communicator.send(packet)

    def auto_cmd(self, cmd, data):
        data = prutils.num_to_chars(data)
        packet = prutils._make_f2_packet(data, cmd)
        self._Communicator.send(packet)

    def set_pgm(self, long_id, short_id, number, state):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.set_pgm(long_id, short_id, number, state)
        self._Communicator.send(packet)        

    def set_x10(self, long_id, short_id, number, state):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.set_x10(long_id, short_id, number, state)
        self._Communicator.send(packet)        

        
    def keepalive(self, short_id, long_id, seq=1):
        if (not self.is_AUTO_port_ready()): return False
        diagnostics_packet =  hpr.send_diagnostics(short_id, long_id, seq)
        self._Communicator.send( diagnostics_packet, 10, 0.2)
        
    def passive_motion(self, long_id, short_id):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.passive_motion(long_id, short_id)
        return self._Communicator.send(packet)

    def passive_occupation(self, long_id, short_id):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.passive_occupation(long_id, short_id)
        return self._Communicator.send(packet)

    def active_barrier(self, long_id, short_id):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.active_barrier(long_id, short_id)
        return self._Communicator.send(packet)

    def glass_break(self, long_id, short_id):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.glass_break(long_id, short_id)
        return self._Communicator.send(packet)

    def switch_magnetic(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.switch_magnetic(long_id, short_id,  open)
        return self._Communicator.send(packet)

    def smoke(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.smoke(long_id, short_id,  open)
        return self._Communicator.send(packet)

    def heat_sensor(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.heat_sensor(long_id, short_id,  open)
        return self._Communicator.send(packet)

    def co(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.co(long_id, short_id,  open)
        return self._Communicator.send(packet)

    def gas(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.gas(long_id, short_id,  open)
        return self._Communicator.send(packet)

    def flood(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.flood(long_id, short_id,  open)
        return self._Communicator.send(packet)

    def aux(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.aux(long_id, short_id,  open)
        return self._Communicator.send(packet)

    def temperature(self, long_id, short_id, temperature):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.temperature(long_id, short_id, temperature)
        return self._Communicator.send(packet)

        '''iMinTemp = 0x05
        iMaxTemp = 0xF0
        aTemp = [iMaxTemp, iMinTemp]
        def freezer(self, long_id, short_id, open=1): # <-10
        def freezing(self, long_id, short_id, open=1): # < 7
        def cold(self, long_id, short_id, open=1): # < 19
        def hot(self, long_id, short_id, open=1): # > 28(35)
        '''
    
    def panic_alarm(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.panic_alarm(long_id, short_id, open)
        return self._Communicator.send(packet)

    def fire_alarm(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.fire_alarm(long_id, short_id, open)
        return self._Communicator.send(packet)


    def emergency(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.emergency(long_id, short_id, open)
        return self._Communicator.send(packet)

    def tamper(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.tamper(long_id, short_id, open)
        return self._Communicator.send(packet)

    def low_battery(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.low_battery(long_id, short_id, open)
        return self._Communicator.send(packet)

    def ac_fail(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.ac_fail(long_id, short_id, open)
        return self._Communicator.send(packet)

    def masking(self, long_id, short_id, open = 1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.masking(long_id, short_id, open)
        return self._Communicator.send(packet)

    def heat_trouble(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.heat_trouble(long_id, short_id, open)
        return self._Communicator.send(packet)

    def smoke_trouble(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.smoke_trouble(long_id, short_id, open)
        return self._Communicator.send(packet)

    def jamming(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.jamming(long_id, short_id, open)
        return self._Communicator.send(packet)

    def probe_disconnected(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.probe_disconnected(long_id, short_id, open)
        return self._Communicator.send(packet)

    def co_sensor_trouble(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.co_sensor_trouble(long_id, short_id, open)
        return self._Communicator.send(packet)

    def gas_sensor_trouble(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.gas_sensor_trouble(long_id, short_id, open)
        return self._Communicator.send(packet)

    def change_listen_mode(self, long_id, short_id, mode, timeout_sec):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.change_listen_mode(long_id, short_id, mode, timeout_sec)
        return self._Communicator.send(packet)

    def change_notification_period(self, long_id, short_id, mode, timeout_sec):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.change_notification_period(long_id, short_id, mode, timeout_sec)
        return self._Communicator.send(packet)

    def change_transmission_privileges(self, long_id, short_id, restricted_bitmap, timeout_sec):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.change_transmission_privileges(long_id, short_id, restricted_bitmap, timeout_sec)
        return self._Communicator.send(packet)

    def hello(self, long_id, short_id, command, notification_period=0):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.hello(long_id, short_id, command, notification_period)
        return self._Communicator.send(packet)

    def change_panel_state(self, long_id, short_id, part_bitmap, action, user_code):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.change_panel_state(long_id, short_id, part_bitmap, action, user_code)
        return self._Communicator.send(packet)

    def prox(self, long_id, short_id, tag_id = 0, action = 3, partition_bitmap = 0):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.prox(long_id, short_id, tag_id, action, partition_bitmap)
        return self._Communicator.send(packet)

    def aux_simple(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.aux_simple(long_id, short_id,  open)
        return self._Communicator.send(packet)

    def volume(self, long_id, short_id, level):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.volume(long_id, short_id, level)
        return self._Communicator.send(packet)
    
    def supervision(self, long_id, short_id, open=1):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.supervision(long_id, short_id,  open)
        return self._Communicator.send(packet)

    def partition(self, long_id, short_id, partition_bitmap = 0):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.partition(long_id, short_id, partition_bitmap = 0)
        return self._Communicator.send(packet)

    def show_locally_link_quality(self, long_id, short_id, enable):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.show_locally_link_quality(long_id, short_id, enable)
        return self._Communicator.send(packet)

    def device_type(self, long_id, short_id, type, subtype):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.device_type(long_id, short_id, type, subtype)
        return self._Communicator.send(packet)

    def power_mode(self, long_id, short_id, mode):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.power_mode(long_id, short_id, mode)
        return self._Communicator.send(packet)

    def clear_alarm_memory(self, long_id, short_id):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.clear_alarm_memory(long_id, short_id)
        return self._Communicator.send(packet)

    def update(self, long_id, short_id):
        if (not self.is_AUTO_port_ready()): return False
        packet = dpr.update(long_id, short_id)
        return self._Communicator.send(packet)

    # TODO : F0 enroll
    def enroll(self, long_id, dev_type, customer_mid = 0, customer_did = 0):
        if (not self.is_AUTO_port_ready()): return False
        #Algorithm:
        #    1. Send enroll packet (0x13)
        #    2. Wait answer packet (0x11)

        enroll_packet = dpr.enroll(long_id, dev_type, customer_mid, customer_did)

        self._Communicator.send(enroll_packet)

        answer_packet = self._Communicator.wait(11)

        if (answer_packet):
            if len(answer_packet) < 15:
                log.write("EnrollFailed. Invalid answer")
                return None
            # Answer packet: 0D F2 0B 00 00 0A 01 05 36 08 00 00 0F 03 02 08 67 01 0A
            # [0x0D] [0xF2] [0x0B] [0x00] [0x00] [LEN = 0x0A] [OK/REJECT] [N/A] [LongID = 4 bytes] [DEV_NUM] [N/A = 3 bytes] [CS = 2 bytes] [0x0A]
            #print "Answer packet: " + hexdump(answer_packet)
            enroll_result = ord(answer_packet[6])
            if (not enroll_result):
                log.write("EnrollFailed. PowerMaster rejected device")
                return None
            short_id = ord(answer_packet[12])
            dev_num  = '%02d' % ord(answer_packet[14])
            dev_type = ord(answer_packet[13])
            log.write('After wait cmd #11. short_id: {0}, DevType: {1}, DevNum: {2}'.format( short_id, dev_type, dev_num ))
            return [short_id, dev_num]
        else:
            log.write("EnrollFailed. No CMD=11 received")
            return None

    def association_request(self, long_id):
        if (not self.is_AUTO_port_ready()): return False
        packet = hpr.association_request(long_id)
        self._Communicator.send(packet)

    def send_response(self, long_id, short_id, dpr_seq, mcode=0x06, state=0, notification_period=0):
        #log.write('RESPONSE')
        # state: 0 - OK, 1 .. see device protocol
        # prepare device protocol
        # mcode = 0x06
        #print type(state)
        state = chr(state)
        seq = prutils.generate_seq("hpr")
        ser_num = prutils.convert_longid(int(long_id))[:3]
        mdata_value = chr(mcode) + chr(len(state)) + state
        device_packet = '\x14\x00' + chr(dpr_seq) + ser_num + mdata_value

        # prepare host protocol
        #final_hop_info = '\x00' * 11
        final_hop_info = '\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00'
        relaying_repeater_ID = 0
        repeater_hop_info = '\x00' * 11
        data = chr(short_id) + chr(seq) + chr(0x30 + notification_period) + final_hop_info + chr(relaying_repeater_ID)\
         + repeater_hop_info + prutils.str_l(device_packet)
        cmd = 0x30
        data = chr(cmd) + data
        cmd_l = 2 + len(data)
        data = chr(cmd_l) + data
        host_protocol_message = data + prutils.crc16(data)[0] + '\x0A'
     
        packet = prutils._make_f2_packet( host_protocol_message )

        #self._Procedures._Communicator.add_to_queue(packet, 0, 5)
        self._Communicator.send(packet)


    def report_camera_detection_event(self, long_id, short_id, index, timerexpired=True):
        # send report and wait for reply
        if timerexpired:
            packet = dpr.passive_motion_with_index_and_timer(long_id, short_id, index, 0)
        else:
            packet = dpr.passive_motion_with_index(long_id, short_id, index)
        self._Communicator.send(packet)
        # activity timer tldv?
    

    def report_film_info(self, long_id, short_id, film_id, index, files_amount=15, zone=255, time_stamp=0):
        # default values
        pre_alarm_length = 2
        post_alarm_length = 5
        film_status = 3 # closed
        film_type = 0   # jpeg
        frame_rate = 5
        # zone = 255 # self triggered

        packet = dpr.film_info(long_id, short_id, film_id, film_status, film_type, pre_alarm_length, post_alarm_length,
                    frame_rate, time_stamp, index, zone, files_amount)
        self._Communicator.send(packet)

    def report_file_info(self, long_id, short_id, film_type, film_id, file_size, row, prime_file_id, frame_number,\
            crc, index, zone=255, time_stamp=0, sequence=-1):

        file_status = 2 # closed
        secondary_file_id = 0
        file_type = 0


        packet = dpr.file_info(long_id, short_id, film_id, row, file_status,  prime_file_id, secondary_file_id, frame_number, file_type,\
        film_type, time_stamp, crc, index, zone, file_size, sequence)
        self._Communicator.send(packet)

    def send_file_body(self, long_id, short_id, image_data, film_id, row, sequence=-1): # reply with file body
        file_block = 0
        if not image_data:
            return False

        chunk_size = 176 # packet size  = 0xC0
        offset = 0
        # sent_data = ''
        while(offset < len(image_data)):
            if len(image_data) - offset > chunk_size:
                bytes_to_send = chunk_size
            else:
                bytes_to_send = len(image_data) - offset

            packet = dpr.file_block(long_id, short_id, image_data[offset: offset + bytes_to_send], film_id, row, file_block, sequence)
            # sent_data += image_data[offset: offset + bytes_to_send]

            file_block += 1
            offset += bytes_to_send
            self._Communicator.send(packet)
            log.write("File block[%d], size:%d" % (file_block, bytes_to_send))
        # assert(sent_data == image_data)
            # time.sleep(0.02)


    '''
    # F0 protocol actions
    #
    '''
    def open_test_mode(self):
        if (not self.is_AUTO_port_ready()): return False
        ack = "\x0D\xF0\x01\x43\x00\x00\x80\x40\x0A"
        open_test  = '\x0D\xF0\x05' + ('\x00'*3) + '\x53\x11\x0A'
        retry = 3
        while retry:
            self._Communicator.send(open_test)
            retry -= 1
            result = self._Communicator.wait(0x01, 3)
            if result == ack:
                #log.write("Can't set panel to test mode")
                return True
        else:
            return False

    def close_test_mode(self):
        if (not self.is_AUTO_port_ready()): return False
        ack = "\x0D\xF0\x01\x43\x00\x00\x80\x40\x0A"
        close_test = '\x0D\xF0\x06' + ('\x00'*3) + '\x46\x2C\x0A'
        retry = 3
        while retry:
            self._Communicator.send(close_test)
            retry -= 1
            result = self._Communicator.wait(0x01, 3)
            if result == ack:
                #log.write("Can't set panel to work mode")
                return True
        else:
            return False
    

    def remove_device(self,  short_id):
        remove_result = False
        if (not self.is_AUTO_port_ready()): return False
        remove_packet = prutils.make_f0_packet(2, 54, chr(short_id))
        #log.write(prutils.hexdump(remove_packet))

        if not (self.open_test_mode()):
            log.write("Can't open test mode")
            return False

        self._Communicator.send(remove_packet)
        result = self._Communicator.wait(0x01, 3)
        if result :
            #0D F0 04 43 00 02 36 01 09 91 0A
            result = self._Communicator.wait(0x04, 3)
            if result and (ord(result[6]) == 54):
                if(ord(result[7]) == 1):
                    remove_result = True
                    #pc_ack = "\xF0\x01\x00\x00\x00"
                    #pc_ack = '\x0D' + pc_ack + prutils.num_to_chars(prutils.crc16_F0(remove_packet), 2, 0) + '\x0A'
                    #self._Communicator.send(ack) 
                    #log.write("ACK")
        time.sleep(1)
        self.close_test_mode()
        return remove_result


    def reset_to_factory_defaults(self):
        if (not self.is_AUTO_port_ready()): return False
        result = False
        if not (self.open_test_mode()):
            log.write("Can't open test mode")
            return False
        # cmd = 2, test = 47
        packet = prutils.make_f0_packet(2,47)
        self._Communicator.send(packet)
        time.sleep(5)
        result = self._Communicator.wait(0x04, 3, 5)
        if result and ord(result[6]) == 47:
            result = True
        time.sleep(1)
        self.close_test_mode()
        return result

    def open_automation(self, port_number):
        if (not self.is_AUTO_port_ready()): return False
        # 1 - UART 0 (GSM)
        # 2 - UART 1 (PLink)
        if port_number.upper() == "GSM":
            port_number = 1
        elif port_number.upper() == "PLINK":
            port_number = 2
        else:
            log.write("Wrong port")
            return False

        if not (self.open_test_mode()):
            log.write("Can't open test mode")
            return False
        packet = prutils.make_f0_packet(2, 55, "\x00\x3B\xFF\x01\x00\x00\x00" + chr(port_number))
        self._Communicator.send(packet)
        result = self._Communicator.wait(0x01, 3)
        if result:
            result = self._Communicator.wait(0x04, 3, 5)
            if result and ord(result[6]) == 55:
                result = True
        time.sleep(1)
        self.close_test_mode()
        return result


if __name__ == "__main__":
    pass

