import threading, time
from prutils import hexdump
from filter import Filter, FilterMap

class ProtoParser(threading.Thread):

    _STM = '\x0D'
    _EOM = '\x0A'

    _pool = None
    # _handlers = [] - same for each instanse of class !!!!
    _handlers = None 
    _stop_listening = False
    _port = None
    _bufer = ''
    _is_runned = False

#TODO: add repeate mode for com0com
# implement write function
# enclose port instanse in class

    def __init__(self, msg_pool, port, logger_function = None, repeater_port = None, show_unparsed=False):
        threading.Thread.__init__(self)
        self._handlers = []
        self._pool = msg_pool
        self._pool_out = []
        self._port = port
        self._port.read(self._port.inWaiting())
        # self._port.flushInput()
        # self._port.flushOutput()
        self._repeater_port = repeater_port
        self._show_unparsed = show_unparsed
        self._logger = logger_function
        # self.log("protoparser::init for %s" % self._port.port, "debug")

    def set_stm(self, data):
        self._STM = data

    def set_eom(self, data):
        self._EOM = data

    def log(self, msg, mode = "console"):
        if self._logger:
            self._logger(msg, mode)
        elif self._show_unparsed == True:
            print msg 

    def stop(self):
        while len(self._pool_out):
            pass
        self._stop_listening = 1


    def add_proto_handler(self, proto_handler):
        self._handlers.append(proto_handler)
        # self.log("protoparser::add handler for %s" % (self._port.port), "debug")

    def send_message(self, msg):
        self._pool_out.append(msg)
        # self.log("{0}[TX] {1}".format(self._port.port, hexdump(msg)), "debug")
        # self._port.write(msg)

# FIX ME: add write function to avoid problem with async write operations !!!
# Use port with monopoly access
# Hold out message pool
    def run(self):
        packet_found = False
        packet = ''
        offset = 0
        while(not self._stop_listening):
            if(self._port.inWaiting() > 0):
                self._is_runned = True
                data_size = self._port.inWaiting()
                add = self._port.read(data_size)
                self._bufer += add
                # self.log("raw {0}[RX] {1}".format(self._port.port, hexdump(add)), "debug")
                if self._repeater_port:
                    self._repeater_port.write(add)
     
            else:
                if self._repeater_port and (self._repeater_port.inWaiting() > 0):
                    data = self._repeater_port.read(self._repeater_port.inWaiting())
                    self._port.write(data)
                    
                if len(self._pool_out) > 0:
                    msg = self._pool_out.pop(0)
                    self.log("{0}[TX] {1}".format(self._port.port, hexdump(msg)), "debug")
                    self._port.write(msg)
                else:
                    time.sleep(0.01)
                continue
            offset = 0
            # self.log('bufer = %s for %s' % (hexdump(self._bufer), self._port.port))
            while offset < len(self._bufer):
                # seek to STM
                # STM = 0 means any byte
                # print "fist byte=%02x" % ord(self._bufer[offset])
                while (self._STM != 0) and (self._bufer[offset] != self._STM):
                    offset += 1
                    # print "seeking for STM: %d" % offset
                    if offset == len(self._bufer):
                        break
                else:
                    #STM found
                    if(self._bufer.find(self._EOM) != -1):
                        # print "EOM found " 
                        #print "buf[%d]: %s" % (len(self._bufer),hexdump(self._bufer))
                        for handler in self._handlers:
                            #self.log("protoparser::handler_run %s (%s)" % (handler, self._port.port))
                            #print "handlers:%d for %s" % (len(self._handlers), self)
                            packet = handler(self._bufer[offset:])
                            if (packet != None):
                                self._pool.append(packet)
                                self.log("{0}[RX] {1}".format(self._port.port, hexdump(packet)), "debug")
                                #crop bufer
                                self._bufer = self._bufer[len(packet) + offset:]
                                # self.log("croped bufer = %s" % hexdump(self._bufer), "debug")
                                # offset = 0
                                break
                        else:
                            offset += 1
                    else:
                        break
            if self._bufer and self._show_unparsed: pass
                # self.log("UNP[%d](%s): %s" % (threading.current_thread().ident,self._port.port, hexdump(self._bufer)))
            #self._bufer = ''
        self._is_runned = False
        # print "ProtoParser - end of RUN cycle"
                       

class MessagePool(threading.Thread):
    # TODO : extend to handle several counters for severa users
    _filters = None
    _stop_listening = False


    def add_filter(self, filter_data, filter_id=''):
         # filter_data: list of tuples:[(0,'\x0D'),(1,'\xF2'), (2,'\x09')]
        self._filters.add(filter_id, Filter(filter_data))
        

    def get_message(self, move=False):
        if(len(self._pool) > 0):
            if(move):
                return self._pool.pop(0)
            else:
                return self._pool[0]
        return None

    def get_filtered_message(self):
        if(len(self._filtered_messages) > 0):
            #print "msg pop up"
            return self._filtered_messages.pop(0)
        return None

    def __init__(self):
        threading.Thread.__init__(self)
        self._filters = FilterMap()
        self._pool = []
        self._filtered_messages = []
        self._index = 0
        self._lock = threading.Lock()

    def reset_pool(self):
        self._index = 0
        del self._filtered_messages[:]
        del self._pool[:]
        

    def run(self):
        #look for pool and do filtering
        while not self._stop_listening:
            #print "pool[%s] = %s" % (self, self._pool)
            while self._index < len(self._pool):
                #if (self._index):
                #    print "[%s]LEN=%d, idx=%d" % (self, len(self._pool), self._index)
                for flt in self._filters:
                    #print "appling filter (%s) for %s " % (self._filters.get_curr_id(), hexdump(self._pool[self._index]))
                    if(flt.apply(self._pool[self._index])):
                        self._filtered_messages.append(self._pool[self._index])
                        #self._filtered_messages.append(msg)
                        #print "added by filter"
                    #else:
                    #    time.sleep(0.1)
                self._index += 1
            time.sleep(0.1)

            
            if(len(self._pool) > 1000):
                with self._lock:
                    #print "RESET on %d" % len(self._pool)
                    # self.reset_pool()
                    pass
                    

    def wait(self, value, position, timeout, realtime=0):
        # print "waiting for 0x%02x at %d" % (value, position)
        i = 0
        time_stop = time.time() + timeout 
        while time.time() < time_stop: 
            while i < len(self._pool):
                msg = self._pool[i]
                # print "chk %d/%d:%s" % (i + 1, len(self._pool), hexdump(msg))
                if msg and position < len(msg):
                    if ord(msg[position]) == value:
                        self._pool.remove(msg)
                        #debug_out("msg removed:%s" % hexdump(msg))
                        # print "msg returned"
                        return msg
                i += 1
        # print "None returned"
        return None