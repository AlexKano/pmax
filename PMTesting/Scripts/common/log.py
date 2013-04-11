#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import config
import threading
import thread
import sys, time

class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

        # print 'sing'

    def __call__(cls,*args,**kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
            cls.instance.start()
        return cls.instance

# singleton class for output to console in own thread
class Logger (threading.Thread):
    __metaclass__ = Singleton

    _buffer = []
    _stop_needed = False
    _got_filename = None

    def __init__(self, file_path_name=None):
        threading.Thread.__init__(self)
        # print 'logg: {0}'.format( file_path_name )
        if (file_path_name is not None) and self._got_filename is None:
            self._got_filename = True
        else:
            self._got_filename = False
            return 
        logging.basicConfig(level=logging.DEBUG,
        #logging.basicConfig(level=logging.INFO,
                            #format='%(asctime)s %(levelname)s %(message)s',
                            format='%(asctime)s %(message)s',
                            filename=file_path_name
                            #,filemode='w'
                           )

    def out(self, msg):
        self._buffer.append(msg)
        # print "logger::out %d" % len(self._buffer)


    def run(self):
        # print "logger::run"
        # print not self._stop_needed , len(self._buffer)
        while (not self._stop_needed) or len(self._buffer):
            # print "logger::run:%d" % len(self._buffer)
            if len(self._buffer):
                msg = self._buffer.pop(0)
                
                # if it is a prompt
                if (len(msg) > 1) and (msg[len(msg) - 2] == '>'):
                    sys.stdout.write(msg)
                else:
                    sys.stdout.write( msg + '\n')
            time.sleep(0.01)


def open(file_path_name):
    Logger(file_path_name)

def write(message, level = "console"):
    logger = Logger()
    if logger._got_filename == False:
        close()
        return False 
    # print 'logger::write'
    if level != "nolog":
        time = datetime.now().strftime("%d/%m/%y %H:%M:%S")
        microseconds = datetime.now().strftime("%f")
        time += "." + microseconds[:3]
        #logging.debug('{0} {1}'.format(time, message))
        logging.debug('{0}'.format(message))
    #sys.stdout.write(message)
    if (config.VERBOSE) or (level == "console") or (level == "nolog"):
        #print(message)
        logger.out(message)
    return True

def close():
    # print "logger close"
    logger = Logger()
    logger._stop_needed = True
    logger.join()


         
if __name__ == "__main__":
    pass
    