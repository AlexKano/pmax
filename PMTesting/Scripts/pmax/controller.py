
#TODO: Finish controller module
# Control Module class

import os
import sys
import threading
import config
import time

from common import devutils
from pmax.view import View
from pmax import procedures
from common.prutils import hexdump, fromhex, num_to_chars, str_to_chars, crc16
from common import log
from common.device_instance import Device
from common.filter import Filter, FilterMap

class _DeviceActions():
    _pool_dump_path = config.BASE_PATH + "devices.pool"
    _devices_pool = None # goes from Controller object

    def __init__(self, devices_pool):
        self._devices_pool = devices_pool

    def check_devices_modes(self, expected_mode):
        result = ''
        for device in self._devices_pool:
            mode = device.get_device_state()
            if mode.upper() != expected_mode.upper():
                log.write("Device [%d] mode = %s" % (device._short_id, mode))
                if result:
                    result += "," + str(device._short_id)
                else:
                    result = str(device._short_id)
        return result
    # def _send_response(self, short_id, seq):
    #     device = self._find_device(int(short_id, 0), 0)
    #     if (device):
    #         device.send_response(int(seq, 0))
    #         return True
    #     else:
    #         log.write("No such device was found")
    #         return False


    def update_all_devices(self):
        for device in self._devices_pool:
            self._Procedures.update(device._long_id, device._short_id)
            time.sleep(0.2)
         
    def _print_device_info(self, device):
        log.write("Device: {0} , sid={1}, lid={2}".format(device._dev_type,device._short_id, device._long_id))

    def get_all_devices(self):
        if len(self._devices_pool) == 0:
            log.write("No devices was registered")
            return None
        for device in self._devices_pool:
            self._print_device_info(device)
        return self._devices_pool

    def clear_device_pool(self):
        del self._devices_pool[:]
        devutils.save(self._devices_pool, self._pool_dump_path)

    def _add_device(self, Device):
        self._devices_pool.append(Device)
        devutils.save(self._devices_pool, self._pool_dump_path)

    def _load_devices(self):
        result = devutils.load(self._pool_dump_path)
        if (result != None):
            #Recreating Device objects to make them dynamic (start KA thread)
            for i in range(len(result)):
                device_data = result[i]
                self._devices_pool.append(Device(device_data._dev_type, device_data._long_id, device_data._short_id, device_data._dev_num, self._Procedures))

    def _find_device(self, short_id, long_id, dev_type=''):
        # device._short_id = 0 when called from enroll to check if device in pool
        for device in self._devices_pool:
            #print device._short_id
            if (long_id == 0 or device._long_id == long_id) and (short_id == 0 or device._short_id == short_id) and (dev_type == '' or device._dev_type == dev_type):
                return device
        return None

    def remove_device(self, short_id, long_id=0):
        short_id = int(short_id, 0)
        device = self._find_device(short_id, 0)
        if not device:
            log.write("Can't found such device")
            return False
        device.stop()
        result = self._Procedures.remove_device(short_id)
        self._devices_pool.remove(device)
        devutils.save(self._devices_pool, self._pool_dump_path)
        if not result:
            log.write("Can't delete device")
        return False

        #log.write("device_idx="  + str(device_idx))
        device.stop()
        #log.write("Device stoped, is alive = " + str(device._ka_thread.isAlive()))
        self._devices_pool.remove(device)
        del(device)
        devutils.save(self._devices_pool, self._pool_dump_path)
        return True
    
    def remove_all_devices(self):
        result = self._Procedures.remove_device(0xFF)
        for device in self._devices_pool:
            device.stop()
        self.clear_device_pool()
        devutils.save(self._devices_pool, self._pool_dump_path)

    def get_device_state(self, short_id):
        device = self._find_device(int(short_id, 0), 0)
        mode = device.get_device_state()
        if device:
            log.write(mode)
        return mode

#Automation commands
class _AUTO_API:

    def request_configuration_data(self, short_id, long_id, parameter):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        parameter = int(parameter, 0)
        self._Procedures.request_configuration_data(short_id, long_id, parameter)

    def send_auto_cmd(self, cmd, data=''):
        cmd = int(cmd, 0)
        self._Procedures.auto_cmd(cmd, data)

    def get_lcd(self):
        msg = '\xF2\x03\x00\x00\x00'
        msg = '\x0D' + msg + crc16(msg) + '\x0A'
        self._Procedures._Communicator.send(msg)
        ans = self._Procedures._Communicator.wait(0x01)
        if ans:
            log.write("get_lcd:%s" % self.extract_lcd(ans))                    
            return self.extract_lcd(ans)
        return ''

    def extract_lcd(self, msg):
        return  msg[6:22]

    def check_lcd(self, lcd, expected):
        log.write("check_lcd: %s != [%s]" % (lcd, expected))
        if lcd != expected:
            return False
        return True


    def send_key(self, name, plcd='', timeout=0.5):
        prev_lcd = plcd
        if prev_lcd == '':
            prev_lcd = self.get_lcd()
        log.write("send key:%s" % name)
        if name.isdigit():
            self.send_auto_cmd('1', name)
        elif name.upper() == 'NEXT':
            self.send_auto_cmd('1', '0x12')
        elif name.upper() == 'OK':
            self.send_auto_cmd('1', '0x10')
        elif name.upper() == 'AWAY':
            self.send_auto_cmd('1', '0x0A')
        elif name.upper() == 'HOME':
            self.send_auto_cmd('1', '0x0B')
        elif name.upper() == 'OFF':
            self.send_auto_cmd('1', '0x0C')
        elif name == '*':
            self.send_auto_cmd('1', '0x0D')
        elif name == '#':
            self.send_auto_cmd('1', '0x0E')
        elif name.upper() == 'BACK':
            self.send_auto_cmd('1', '0x0F')
        elif name.upper() == 'PANIC':
            self.send_auto_cmd('1', '0x11')
        elif name.upper() == 'RECORD_OFF':
            self.send_auto_cmd('1', '0x13')
        elif name.upper() == 'FIRE':
            self.send_auto_cmd('1', '0x14')
        elif name.upper() == 'EMERGENCY':
            self.send_auto_cmd('1', '0x15')
        else:
            return False
        # key_pressed = False
        # ans = self._Procedures._Communicator.wait(0x03, 0.2)
        # if ans and ord(ans[6]) == 14:
        #     log.write("key pressed")
        #     key_pressed = True


        # ans = self._Procedures._Communicator.wait(0x01, timeout)
        # if ans:
        #     if self.extract_lcd(ans) == prev_lcd: 
        #         ans = self._Procedures._Communicator.wait(0x01, 0.5) 
        #         if not ans:
        #             return self.send_key(name, prev_lcd)
        #     log.write("got lcd:%s" % self.extract_lcd(ans))                    
        #     return self.extract_lcd(ans)
        # else:
        #     if not key_pressed:
        #         return self.send_key(name, prev_lcd)
        #     else:
        #         ans = self._Procedures._Communicator.wait(0x01, 0.5)
        return





    


#RF commands
# FIXME : return value
class _RF_API:
     # virtual device wrapper, assumed that 1st parameter is short id, 2nd - long id
    def virtual_device_delay(cmd_function):
        def _wrapper(self, *params):
            device = self._find_device(int(params[0], 0), int(params[1],0))
            if(device):
                log.write("Waiting for transmitter delay end...")
                # this one is virtual device, check if it in transmitter delay now
                while device.get_transmitter_delay_flag() == True:
                    time.sleep(0.1)
                device.set_transmitter_delay()
            return cmd_function(self, *params)
        return _wrapper
    
    # @virtual_device_delay
    def send_response(self, short_id, long_id, seq, mcode='6', state='0', notification_period='0'):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        seq = int(seq, 0)
        mcode = int(mcode,0)
        notification_period = int(notification_period, 0)
        state = int(state, 0)
        result = self._Procedures.send_response(long_id, short_id, seq, mcode, state, notification_period)
        return result

    # @virtual_device_delay
    def violate(self, short_id, long_id):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        result = self._Procedures.passive_motion(long_id, short_id)
        return result

    # @virtual_device_delay
    def passive_occupation(self, short_id, long_id):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        result = self._Procedures.passive_occupation(long_id, short_id)
        return result
    
    # @virtual_device_delay
    def active_barrier(self, short_id, long_id):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        result = self._Procedures.active_barrier(long_id, short_id)
        return result


    # @virtual_device_delay
    def glass_break(self, short_id, long_id):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        result = self._Procedures.glass_break(long_id, short_id)
        return result

    def _switch_magnetic(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.switch_magnetic(long_id, short_id, open)

    # # @virtual_device_delay
    def open(self, short_id, long_id):
        self._switch_magnetic(short_id, long_id, 1)
        return None

    # # @virtual_device_delay
    def close(self, short_id, long_id):
        self._switch_magnetic(short_id, long_id, 0)
        return None

    def _smoke(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.smoke(long_id, short_id, open)
        return result

    # # @virtual_device_delay
    def open_smoke_alarm(self, short_id, long_id):
        return self._smoke(short_id, long_id, 1)

    # # @virtual_device_delay
    def close_smoke_alarm(self, short_id, long_id):
        return self._smoke(short_id, long_id, 0)


    def _heat_sensor(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.heat_sensor(long_id, short_id, open)

    # # @virtual_device_delay
    def open_heat_alarm(self, short_id, long_id):
        self._heat_sensor(short_id, long_id, 1)

    # # @virtual_device_delay
    def close_heat_alarm(self, short_id, long_id):
        self._heat_sensor(short_id, long_id, 0)


    def _co(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.co(long_id, short_id, open)

    # # @virtual_device_delay
    def open_co_alert(self, short_id, long_id):
        self._co(short_id, long_id, 1)

    # # @virtual_device_delay
    def close_co_alert(self, short_id, long_id):
        self._co(short_id, long_id, 0)

    def _gas(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.gas(long_id, short_id, open)

    # # @virtual_device_delay
    def open_gas_alert(self, short_id, long_id):
        self._gas(short_id, long_id, 1)

    # # @virtual_device_delay
    def close_gas_alert(self, short_id, long_id):
        self._gas(short_id, long_id, 0)


    def _flood(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.flood(long_id, short_id, open)

    # # @virtual_device_delay
    def open_flood(self, short_id, long_id):
        self._flood(short_id, long_id, 1)

    # # @virtual_device_delay
    def close_flood(self, short_id, long_id):
        self._flood(short_id, long_id, 0)


    def _aux(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.aux(long_id, short_id, open)

    # # @virtual_device_delay
    def open_aux(self, short_id, long_id):
        self._aux(short_id, long_id, 1)

    # # @virtual_device_delay
    def close_aux(self, short_id, long_id):
        self._aux(short_id, long_id, 0)


    def _temperature(self, short_id, long_id, temperature):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #temperature = float(temperature, 0)
        result = self._Procedures.temperature(long_id, short_id, temperature)

    # # @virtual_device_delay
    def set_temperature(self, short_id, long_id, Temperature = -40.0):
        self._temperature(short_id, long_id, Temperature)

    # # @virtual_device_delay
    def open_freezer(self, short_id, long_id):
        self._temperature(short_id, long_id, -10.5)

    # # @virtual_device_delay
    def close_freezer(self, short_id, long_id):
        self._temperature(short_id, long_id, 30)

    # # @virtual_device_delay
    def open_freezing(self, short_id, long_id):
        self._temperature(short_id, long_id, 6.5)

    # # @virtual_device_delay
    def close_freezing(self, short_id, long_id):
        self._temperature(short_id, long_id, 30)

    # # @virtual_device_delay
    def open_hot(self, short_id, long_id):
        self._temperature(short_id, long_id, 35.5)

    # @virtual_device_delay
    def close_hot(self, short_id, long_id):
        self._temperature(short_id, long_id, 20)

    # @virtual_device_delay
    def open_cold(self, short_id, long_id):
        self._temperature(short_id, long_id, 18)

    # @virtual_device_delay
    def close_cold(self, short_id, long_id):
        self._temperature(short_id, long_id, 20)



    def _panic_alarm(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.panic_alarm(long_id, short_id, open)

    # @virtual_device_delay
    def panic(self, short_id, long_id):
        self._panic_alarm(short_id, long_id, 1)

    def _fire_alarm(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.fire_alarm(long_id, short_id, open)

    # @virtual_device_delay
    def fire(self, short_id, long_id):
        self._fire_alarm(short_id, long_id, 1)

    # @virtual_device_delay
    def emergency(self, short_id, long_id):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.emergency(long_id, short_id, 1)

    def _tamper(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open)
        result = self._Procedures.tamper(long_id, short_id, open)

    # @virtual_device_delay
    def open_tamper(self, short_id, long_id):
        self._tamper(short_id, long_id, 1)

    # @virtual_device_delay
    def close_tamper(self, short_id, long_id):
        self._tamper(short_id, long_id, 0)

    def _low_battery(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.low_battery(long_id, short_id, open)

    # @virtual_device_delay
    def open_low_bat(self, short_id, long_id):
        self._low_battery(short_id, long_id, 1)

    # @virtual_device_delay
    def close_low_bat(self, short_id, long_id):
        self._low_battery(short_id, long_id, 0)

    def _ac_fail(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.ac_fail(long_id, short_id, open)

    # @virtual_device_delay
    def ac_fail(self, short_id, long_id):
        self._ac_fail(short_id, long_id, 1)

    # @virtual_device_delay
    def ac_rest(self, short_id, long_id):
        self._ac_fail(short_id, long_id, 0)

    def _masking(self, short_id, long_id, open = 1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.masking(long_id, short_id, open)

    # @virtual_device_delay
    def open_masking(self, short_id, long_id):
        self._masking(short_id, long_id, 1)

    # @virtual_device_delay
    def close_masking(self, short_id, long_id):
        self._masking(short_id, long_id, 0)

    def _heat_trouble(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.heat_trouble(long_id, short_id, open)

    # @virtual_device_delay
    def open_heat_trouble(self, short_id, long_id):
        self._heat_trouble(short_id, long_id, 1)

    # @virtual_device_delay
    def close_heat_trouble(self, short_id, long_id):
        self._heat_trouble(short_id, long_id, 0)

    def _smoke_trouble(self, short_id, long_id, open):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.smoke_trouble(long_id, short_id, open)

    # @virtual_device_delay
    def open_smoke_trouble(self, short_id, long_id):
        self._smoke_trouble(short_id, long_id, 1)

    # @virtual_device_delay
    def close_smoke_trouble(self, short_id, long_id):
        self._smoke_trouble(short_id, long_id, 0)


    def _jamming(self, short_id, long_id, open):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.jamming(long_id, short_id, open)

    # @virtual_device_delay
    def open_jamming(self, short_id, long_id):
        self._jamming(short_id, long_id, 1)

    # @virtual_device_delay
    def close_jamming(self, short_id, long_id):
        self._jamming(short_id, long_id, 0)

    def _probe_disconnected(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.probe_disconnected(long_id, short_id, open)

    # @virtual_device_delay
    def open_probe(self, short_id, long_id):
        self._probe_disconnected(short_id, long_id, 1)

    # @virtual_device_delay
    def close_probe(self, short_id, long_id):
        self._probe_disconnected(short_id, long_id, 0)

    def _co_sensor_trouble(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.co_sensor_trouble(long_id, short_id, open)

    # @virtual_device_delay
    def open_co_trouble(self, short_id, long_id):
        self._co_sensor_trouble(short_id, long_id, 1)

    # @virtual_device_delay
    def close_co_trouble(self, short_id, long_id):
        self._co_sensor_trouble(short_id, long_id, 0)

    def _gas_sensor_trouble(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.gas_sensor_trouble(long_id, short_id, open)

    # @virtual_device_delay
    def open_gas_trouble(self, short_id, long_id):
        self._gas_sensor_trouble(short_id, long_id, 1)

    # @virtual_device_delay
    def close_gas_trouble(self, short_id, long_id):
        self._gas_sensor_trouble(short_id, long_id, 0)

    # @virtual_device_delay
    def change_listen_mode(self, short_id, long_id, mode, timeout_sec):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        mode = int(mode, 0)
        timeout_sec = int(timeout_sec, 0)
        result = self._Procedures.change_listen_mode(long_id, short_id, mode, timeout_sec)

    # @virtual_device_delay
    def change_notification_period(self, short_id, long_id, mode, timeout_sec):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        mode = int(mode, 0)
        timeout_sec = int(timeout_sec, 0)
        result = self._Procedures.change_notification_period(long_id, short_id, mode, timeout_sec)

    # @virtual_device_delay
    def change_transmission_privileges(self, short_id, long_id, restricted_bitmap, timeout_sec):
        # restricted_bitmap - bitmap of restricted slots (8 bytes):
        #   0   - not restricted
        #   1   - slot is restricted for transmission
        # e.g. '10000110'
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        restricted_bitmap=str_to_chars(restricted_bitmap)
        timeout_sec = int(timeout_sec, 0)
        result = self._Procedures.change_transmission_privileges(long_id, short_id, restricted_bitmap, timeout_sec)

    # # @virtual_device_delay
    def hello(self, short_id, long_id, command):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        command = int(command, 0)
        result = self._Procedures.hello(long_id, short_id, command)

    def _change_panel_state(self, short_id, long_id, partition, action, user_code):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #convert partiton from number to bitmap
        partition = int(partition, 0)
        if(partition):
            part_bitmap = 1<<(partition - 1)
        else:
            part_bitmap = partition
        #action = int(action, 0)
        user_code = int(user_code, 0)
        log.write("part_bitmap=" + str(part_bitmap))
        result = self._Procedures.change_panel_state(long_id, short_id, part_bitmap, action, user_code)

    # partition = 0, 1, 2, 3
    # @virtual_device_delay
    def arm_away(self, short_id, long_id, user_code = '0xAAAA', partition = '0'):
        self._change_panel_state(short_id,long_id, partition, 3, user_code)

    # @virtual_device_delay
    def arm_home(self, short_id, long_id, user_code = '0xAAAA', partition = '0'):
        self._change_panel_state(short_id,long_id, partition, 2, user_code)

    # @virtual_device_delay
    def disarm(self, short_id, long_id, user_code = '0xAAAA', partition = '0'):
        self._change_panel_state(short_id,long_id, partition, 1, user_code)

    # @virtual_device_delay
    def arm_instant(self, short_id, long_id, user_code = '0xAAAA', partition = '0'):
        self._change_panel_state(short_id,long_id, partition, 8, user_code)

    # @virtual_device_delay
    def arm_latchkey(self, short_id, long_id, user_code = '0xAAAA', partition = '0'):
        self._change_panel_state(short_id,long_id, partition, 4, user_code)

    # @virtual_device_delay
    def arm_quick(self, short_id, long_id, user_code = '0xAAAA', partition = '0'):
        self._change_panel_state(short_id,long_id, partition, 6, user_code)

    # @virtual_device_delay
    def arm_home_quick(self, short_id, long_id, user_code = '0xAAAA', partition = '0'):
        self._change_panel_state(short_id,long_id, partition, 7, user_code)

    # @virtual_device_delay
    def _prox(self, short_id, long_id, tag_id, action, partition):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        tag_id = int(tag_id, 0)
        #TODO: Decode partition from number to bit mask
        partition_bitmap = int(partition, 0)
        action = int(action, 0)
        result = self._Procedures.prox(long_id, short_id, tag_id, action, partition_bitmap)

    
    def tag_away(self, tag_id, short_id, long_id, partition='0'):
        self._prox(short_id, long_id, 3, partition)

    def tag_home(self, tag_id, short_id, long_id, partition='0'):
        self._prox(short_id, long_id, 2, partition)

    def tag_disarm(self, tag_id, short_id, long_id,partition='0'):
        self._prox(short_id, long_id, 1, partition)

    def tag_away_latchkey(self, tag_id, short_id, long_id, partition='0'):
        self._prox(short_id, long_id, 4, partition)

    def tag_arm_instant(self, tag_id, short_id, long_id, partition='0'):
        self._prox(short_id, long_id, 8, partition)

    def tag_arm_part(self, tag_id, short_id, long_id, partition='0'):
        self._prox(short_id, long_id, 5, partition)

    def tag_quick_away(self, tag_id, short_id, long_id, partition='0'):
        self._prox(short_id, long_id, 6, partition)

    def tag_quick_home(self, tag_id, short_id, long_id, partition='0'):
        self._prox(short_id, long_id, 7, partition)

    #panel need to be in enrolling mode
    def tag_enroll(self, tag_id, short_id, long_id):
        self._prox(short_id, long_id, 3 , '0')

    def _aux_simple(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.aux_simple(long_id, short_id, open)

    # @virtual_device_delay
    def aux_button(self, short_id, long_id):
        self._aux_simple(short_id, long_id, 1)

    # @virtual_device_delay
    def volume(self, short_id, long_id, level):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        level = int(level, 0)
        result = self._Procedures.volume(long_id, short_id, level)

    def _supervision(self, short_id, long_id, open=1):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        #open = int(open, 0)
        result = self._Procedures.supervision(long_id, short_id, open)

    # @virtual_device_delay
    def open_supervision(self, short_id, long_id):
        self._supervision(short_id, long_id, 1)

    # @virtual_device_delay
    def close_supervision(self, short_id, long_id):
        self._supervision(short_id, long_id, 0)

    # @virtual_device_delay
    def partition(self, short_id, long_id, partition_bitmap = 0):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        partition_bitmap = int(partition_bitmap, 0)
        result = self._Procedures.partition(long_id, short_id, partition_bitmap)

    # @virtual_device_delay
    def show_locally_link_quality(self, short_id, long_id, enable):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        enable = int(enable, 0)
        result = self._Procedures.show_locally_link_quality(long_id, short_id, enable)

    # @virtual_device_delay
    def device_type(self, short_id, long_id, type, subtype):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        type = int(type, 0)
        subtype = int(subtype, 0)
        result = self._Procedures.device_type(long_id, short_id, type, subtype)

    # @virtual_device_delay
    def power_mode(self, short_id, long_id, mode):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        mode = int(mode, 0)
        result = self._Procedures.power_mode(long_id, short_id, mode)


    # @virtual_device_delay
    def clear_alarm_memory(self, short_id, long_id):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        result = self._Procedures.clear_alarm_memory(long_id, short_id)

    # # @virtual_device_delay
    def update(self, short_id, long_id):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        result = self._Procedures.update(long_id, short_id)
        return None

    # @virtual_device_delay
    def keepalive (self, short_id, long_id):
        long_id = int(long_id, 0)
        short_id = int(short_id, 0)
        result = self._Procedures.keepalive(short_id, long_id)
        return result
        
    def enroll (self, dev_type, long_id):
        # TODO: enroll using F0 protocol if zone number is set
        long_id = int(long_id, 0)
        result = self._Procedures.enroll(long_id, dev_type)
        if result:
            #log.write("Device was enrolled: short id = %d, device num = %d")
            EnrolledDevice = Device(dev_type, long_id, result[0], result[1], self._Procedures, 240)
            self._add_device(EnrolledDevice)
            return result[0]

    def back_to_factory_defaults(self):
        self._Procedures.reset_to_factory_defaults()
        for device in self._devices_pool:
            device.stop()
        self.clear_device_pool()
        devutils.save(self._devices_pool, self._pool_dump_path)
        return True

    def open_automation(self, port):
        return self._Procedures.open_automation(port)
		
		
_TIME_between_press_release_key = 0.5
_TIME_after_release_key = 0.1
_TIME_between_card1_card2 = 0.1

class _RELAY_API:
	
	#self._RelayCommunicator.send('\x00')

	
	def dec_to_bin(self, x):
		n1 = "0000000000000000000000000"
		n = ""
		if x==0:
			return n1 
		while x> 0:
			y = str(x % 2)
			n = y +n 
			x = int (x/2)
		return n1+n
	def bin_to_hex(self, binstr):
		dec = int(binstr,2)
		hex1 = hex(dec)
		hex1 = hex1[2:4]
		if len (hex1)<2:
			hex1 = "0"+hex1
		return hex1
			
			
	def dec_to_2hex(self, dec): 
		sbin =  self.dec_to_bin(dec)
		lens = len(sbin)
		bit38 = sbin[lens-24:lens-16]
		bit28 = sbin[lens-16:lens-8]
		bit18 = sbin[lens-8:lens]
		dec_bit28 = int(bit28,2)
		dec_bit18 = int(bit18,2)
		dec_bit38 = int(bit38,2)
		
		hex_bit28 = hex(dec_bit28)
		hex_bit18 = hex(dec_bit18)
		hex_bit38 = hex(dec_bit38)
		
		hex_bit28 = hex_bit28[2:4]
		hex_bit18 = hex_bit18[2:4]
		hex_bit38 = hex_bit38[2:4]
		
		if len (hex_bit28)<2:
			hex_bit28 = "0"+hex_bit28
		if len (hex_bit18)<2:
			hex_bit18 = "0"+hex_bit18
		if len (hex_bit38)<2:
			hex_bit38 = "0"+hex_bit38
			
		return hex_bit18,hex_bit28,hex_bit38
		
	
	def relay1(Num,state):
			s = '5508'+state+Num+'01000024'
		#print s
			for i in range(len(s)/2):
					c = chr(int(s[i*2:i*2+2],16))
					self._RelayCommunicator.send(c)

		#return 1
		
	def relay(self, hex1_8,hex9_16,state,num_card):
		s = '5508'+state+hex9_16+hex1_8+num_card+'000024'
		#print s
		for i in range(len(s)/2):
			c = chr(int(s[i*2:i*2+2],16))
			self._RelayCommunicator.send(c)
		return 1

	def dec_relay(relay1_16,state, num_card ="01"):
		relay1_8,relay9_16 = dec_to_2hex(relay1_16)
		s = '5508'+state+relay9_16+relay1_8+num_card+'000024'
		#print s
		for i in range(len(s)/2):
			c = chr(int(s[i*2:i*2+2],16))
			self._RelayCommunicator.send(c)

		return 1
	def bin_relay(relay_1_8,relay_9_16,state, num_card ="01"):
		bin = relay_9_16 + relay_1_8
		dec = int(bin,2)
		print dec
		relay1_8,relay9_16,x = dec_to_2hex(dec)
		s = '5508'+state+relay9_16+relay1_8+num_card+'000024'
		#print s
		for i in range(len(s)/2):
			c = chr(int(s[i*2:i*2+2],16))
			self._RelayCommunicator.send(c)
		return 1
		
	def relaykey(self, dec,state,time1=_TIME_after_release_key):
		hex1_8,hex9_16,hex17_24 = self.dec_to_2hex(int(dec))
		hex24_32 = "00" 
		if state == "open":
			state1 = "01"
		if state == "close":
			state1 = "02"
		ts = 0
		if hex1_8 != "00" or hex9_16 != "00":	
			self.relay(hex1_8,hex9_16,state1,"01") #press 1 key on card 1
			ts = _TIME_between_card1_card2
		if hex17_24 != "00":
			time.sleep(ts)
			self.relay(hex17_24,hex24_32,state1,"02") #press 1 key on card 2
		
		time.sleep(float(time1))
		#print ">> Pressing "+str(dec)+" key"
		
	def relaykey_b(self, bit1_8,bit9_16,bit17_24,state,time1=_TIME_after_release_key):
		hex1_8 = self.bin_to_hex(bit1_8)
		hex9_16 =self.bin_to_hex(bit9_16)
		hex17_24 = self.bin_to_hex(bit17_24)
		hex24_32 = "00" 
		if state == "open":
			state1 = "01"
		if state == "close":
			state1 = "02"
		ts = 0
		if hex1_8 != "00" or hex9_16 != "00":	
			relay(hex1_8,hex9_16,state1,"01") #press 1 key on card 1
			ts = _TIME_between_card1_card2
		if hex17_24 != "00":
			time.sleep(ts)
			relay(hex17_24,hex24_32,state1,"02") #press 1 key on card 2
		
		time.sleep(float(time1))
		#print ">> Pressing "+bit17_24 +" "+bit9_16+" "+bit1_8+" key"
	def relaykey_b32(self, bit1_8,bit9_16,bit17_24,bit25_32,state,time1=_TIME_after_release_key):
		hex1_8 = self.bin_to_hex(bit1_8)
		hex9_16 = self.bin_to_hex(bit9_16)
		hex17_24 = self.bin_to_hex(bit17_24)
		hex24_32 = self.bin_to_hex(bit25_32)
		if state == "open":
			state1 = "01"
		if state == "close":
			state1 = "02"
		ts = 0
		if hex1_8 != "00" or hex9_16 != "00":	
			relay(hex1_8,hex9_16,state1,"01") #press 1 key on card 1
			ts = _TIME_between_card1_card2
		if hex17_24 != "00"or hex24_32 != "00":
			time.sleep(ts)
			relay(hex17_24,hex24_32,state1,"02") #press 1 key on card 2
		
		time.sleep(float(time1))
		#print ">> Pressing "+bit17_24 +" "+bit9_16+" "+bit1_8+" key"

	def key(self,dec,time1=_TIME_between_press_release_key ,time2=_TIME_after_release_key ):
		hex1_8,hex9_16,hex17_24 = self.dec_to_2hex(dec)
		hex24_32 = "00" 
		ts = 0
		if hex1_8 != "00" or hex9_16 != "00":
			relay(hex1_8,hex9_16,'01',"01") #press 1 key on card 1
			ts = _TIME_between_card1_card2
		if hex17_24 != "00":
			time.sleep(ts)
			self.relay(hex17_24,hex24_32,'01',"02") #press 1 key on card 2
		ts = 0
		time.sleep(time1)
		#print ">> Pressing "+str(dec)+" key"
		if hex1_8 != "00" or hex9_16 != "00":
			self.relay(hex1_8,hex9_16,'02',"01") #release 1 key on card 1
			ts = _TIME_between_card1_card2
		if hex17_24 != "00":
			time.sleep(ts)
			self.relay(hex17_24,hex24_32,'02',"02") #release 1 key on card 2
		time.sleep(time2)
		return 1
		
	def key_b(self,bit1_8,bit9_16,bit17_24="0",time1=_TIME_between_press_release_key ,time2=_TIME_after_release_key):
		hex1_8 = self.bin_to_hex(bit1_8)
		hex9_16 = self.bin_to_hex(bit9_16)
		hex17_24 =  self.bin_to_hex(bit17_24)
		hex24_32 = "00" 
		ts = 0
		if hex1_8 != "00" or hex9_16 != "00":
			self.relay(hex1_8,hex9_16,'01',"01") #press 1 key on card 1
			ts = _TIME_between_card1_card2
		if hex17_24 != "00":
			time.sleep(ts)
			self.relay(hex17_24,hex24_32,'01',"02") #press 1 key on card 2

		#print time1	
		time.sleep(int(time1))
		#print ">> Pressing "+bit17_24 +" "+bit9_16+" "+bit1_8+" key"
		ts = 0
		if hex1_8 != "00" or hex9_16 != "00":
			self.relay(hex1_8,hex9_16,'02',"01") #release 1 key on card 1
			ts = _TIME_between_card1_card2
		if hex17_24 != "00":
			time.sleep(ts)
			self.relay(hex17_24,hex24_32,'02',"02") #release 1 key on card 2
		#print time2
		time.sleep(float(time2))
		return 1

	def key_b32(self,bit1_8,bit9_16,bit17_24="0",bit25_32="0",time1=_TIME_between_press_release_key ,time2=_TIME_after_release_key):
		hex1_8 = self.bin_to_hex(bit1_8)
		hex9_16 = self.bin_to_hex(bit9_16)
		hex17_24 =  self.self.bin_to_hex(bit17_24)
		hex24_32 = self.bin_to_hex(bit25_32)
		ts = 0
		if hex1_8 != "00" or hex9_16 != "00":
			self.relay(hex1_8,hex9_16,'01',"01") #press 1 key on card 1
			ts = _TIME_between_card1_card2
		if hex17_24 != "00"or hex24_32 != "00":
			time.sleep(ts)
			self.relay(hex17_24,hex24_32,'01',"02") #press 1 key on card 2

		#print time1	
		time.sleep(int(time1))
		#print ">> Pressing "+bit17_24 +" "+bit9_16+" "+bit1_8+" key"
		ts = 0
		if hex1_8 != "00" or hex9_16 != "00":
			self.relay(hex1_8,hex9_16,'02',"01") #release 1 key on card 1
			ts = _TIME_between_card1_card2
		if hex17_24 != "00"or hex24_32 != "00":
			time.sleep(ts)
			self.relay(hex17_24,hex24_32,'02',"02") #release 1 key on card 2
		#print time2
		time.sleep(float(time2))
		return 1
	
		
		
class _API(_RF_API, _RELAY_API, _AUTO_API, _DeviceActions):
    SIMULATOR_VERSION = "1.2.1"

    _Procedures = None
    _SnifferCommunicator = None

    def __init__(self, AutoProcedures, RelayCommunicator, device_pool):
        _DeviceActions.__init__(self, device_pool)
        self._Procedures = AutoProcedures
        self._RelayCommunicator = RelayCommunicator
        
        

    def version(self):
        log.write("Version: " + self.SIMULATOR_VERSION)
        return self.SIMULATOR_VERSION


    def _convert_result(self, value):
        if (value):
            # Packet received
            return hexdump(value)
        # Returning 'None' or 'False' values
        return value

    #Method to handle all requests from XML-RPC Server and Console
    def _dispatch(self, command, params):
        #Checking if "timeout" or "ack" parameters were given
		#print '*********************' + command, params
        command_params = []
        set_params = {"ack" : None,
                      "timeout" : None}
        for param in params:
            found_set_param = False
            for key in set_params.keys():
                if (param.find(key + "=") == 0):
                    set_params[key] = int(param.split("=")[1])
                    found_set_param = True
            if (not found_set_param):
                command_params.append(param)
        log.write('%s %s' % (command, ' '.join(params)) , 'debug')

        # Passing set_params dictionary to Communicator class
        self._Procedures._Communicator.SET_PARAMS = set_params
        if(self._SnifferCommunicator):
            self._SnifferCommunicator.SET_PARAMS = set_params
        # Removing all entries from Reader.Pool
        # If "wait" command is specified, no need to clear_pool (to be able to catch previous data)
        if (command not in ["wait", "sniffer_wait"]):
            # log.write("Communicator: clear pool")
            self._Procedures._Communicator.clear_pool()
        if (config.DEBUG_MODE):
            result = getattr(self, command)(*command_params)
            log.write("XMLRPC return value: " + str(result), "debug")
            return result
        else:
            try:
                return getattr(self, command)(*params)
            except SystemExit, e:
                sys.exit(e)
            except Exception:
                log.write("Incorrect command specified")
                return False

    # General commands

    def wait(self, command, timeout = 10):
        result = self._Procedures._Communicator.wait(int(command, 0), int(timeout))
        result = self._convert_result(result)
        return result

    def sniffer_wait(self, command, timeout = 10):
        result = self._SnifferCommunicator.wait(int(command, 0), int(timeout))
        result = self._convert_result(result)
        return result

    def send(self, *packet):
        packet = ' '.join([str(byte) for byte in packet ]).strip()
        packet = fromhex(packet)
        result = self._Procedures._Communicator.send(packet)
        result = self._convert_result(result)
        return result

    def get_packet(self, command, *params):
        result = self._Procedures.get_packet(command, params)
        result = self._convert_result(result)
        return result

class Controller():
    _devices_pool = None
    _Procedures = None

    _View = None
    _API = None
    _PoolListener = None
    _SnifferCommunicator = None


    def __init__(self, Communicator, RelayCommunicator):
        self._Procedures = procedures.RF(Communicator)
        self._devices_pool = []
        self._RelayCommunicator = RelayCommunicator
        #listen sniffer port
        self._API = _API(self._Procedures, self._RelayCommunicator, self._devices_pool)
        self._API._load_devices()
        # if SnifferCommunicator:
        #    self._SnifferCommunicator = SnifferCommunicator
        #   self._PoolListener = devutils.PoolListener(SnifferCommunicator._message_pool, self._devices_pool)
            #add there filters you need to redirect custom messages to devices
        #    self._PoolListener.add_filter(0, [(1,'\x26')])
        #    self._PoolListener.add_filter(1, [(1,'\x10')])
        #    self._PoolListener.start()
        self.start()

    def start(self):
        #Starting View
        self._View = View(self._API)
        #self._PoolListener.start()

