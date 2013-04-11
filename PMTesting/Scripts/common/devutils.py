#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import log
import cPickle
import threading
from common import log
from common.prutils import hexdump
from common.filter import FilterMap, Filter
from pmax.protocols import hpr
def save(data, path):
    '''
    try:
        dump_file = open(path, "w")
        cPickle.dump(data, dump_file)
    except:
        log.write("Cannot write to file: " + path + " to pickle: " + str(data))
    '''
    dump_file = open(path, "w")
    cPickle.dump(data, dump_file)
    dump_file.close()

def load(path):
    if os.path.exists(path):
        try:
            dump_file = open(path, "r")
            return cPickle.load(dump_file)
        except:
            log.write("Error occured while trying to pickle data")
            return None
    else:
        log.write("Cannot open path: " + path + " to load pickled data")

class PoolListener(threading.Thread):
    _msg_pool = None
    _dev_pool = None
    _msg_index = 0
    _DeviceActions = None
    _Filters = None
    _stop_needed = 0
    
    def __init__(self, pool, dev_pool): # devices_pool
        threading.Thread.__init__(self)
        self._msg_pool = pool
        self._dev_pool = dev_pool
        self._Filters = FilterMap()
 
    def add_filter(self, device_id, filter_data):
        self._Filters.add(device_id, Filter(filter_data))
    
    def remove_filter(self, device_id):
        self._Filters.remove(device_id)

    def reset_pool_counter(self):
        # reset pool counter whenever main pool is cleared, runned synchronously with Communicator.clear_pool
        self._msg_index = 0
        # log.write("PoolListener::reset_pool_counter to %d" % self._msg_index, "debug")

    def find(self, sid):
        for device in self._dev_pool:
            if device._short_id == sid:
                return device
        return None
        
                              
#It is for event processing purpose        
    def run(self):
        self._msg_index = 0
        # filter incoming messages and route to appropriate device in pool
        while (not self._stop_needed):
            # log.write("idx = %d of %d" % (self._msg_index, len(self._msg_pool)),"debug")
            if self._Filters != None:
                if self._msg_index == len(self._msg_pool):
                    # log.write("No new messages","debug")
                    time.sleep(0.05)
                    continue
    
                while self._msg_index < len(self._msg_pool):
                    message  = self._msg_pool[self._msg_index]
                    # log.write("PoolListener:: processing message %s at %d" % (hexdump(message), self._msg_index), "debug")
                    for _filter in self._Filters:
                        if _filter.apply(message):
                            # log.write("poollistener::filter match %s " % (hexdump(message)), "debug")
                            values = hpr.parse_hpr_cmd(message)
                            if values:
                                for sid in values.keys():
                                    destination_device = self.find(sid)
                                    if(destination_device):
                                        destination_device.dispatch_message(values[sid])
                                        # log.write("poollistener::send msg %s to %d is %s" % (values, sid, destination_device))
                                    # else:
                                        # log.write("No such device")
                            # self._msg_pool.pop(self._msg_index)
                            #log.write("PLS[RM]:%s" % hexdump(message), "debug")
                                    
                    self._msg_index += 1


if __name__ == "__main__":
    pass
