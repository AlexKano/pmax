#from common import log
class Filter:
    
    def __init__(self, filter_data):
    #list of tuples:[(0,'\x0D'),(1,'\xF2'), (2,'\x09')]
        self._filter_data = filter_data
        
    def apply(self, message):
        if len(message)>= len(self._filter_data):
            for byte_num, byte_val in self._filter_data:
                if (byte_num >= len(message)) or (message[byte_num] != byte_val):
                    break
            else:
                #cycle wasn't broken,all filter values was matched 
                return True
            return False
    '''
    def _apply(self, message):
        message_data = [(tup[0], message[tup[0]]) for tup in self._filter_data]
        print "message=" + str(message_data)
        print "filter=" + str(self._filter_data)
        if set(message_data) & set(self._filter_data):
            return True
        else:
            return False
    '''

class FilterMap:

#    filters:= {<filter_id>, <filter>}

    def add(self, filter_id, _filter):
        self._filters[filter_id] = _filter
        self._curr_item = self._filters.items()[0]
    
    def remove(self, filter_id):
        self._filters.remove(filter_id)
        
    def get_ids(self):
        return self._filters.keys()
    
    def get_curr_id(self):
        if self._curr_item != None:
            return self._curr_item[0]
        else:
            return None
    def get_curr_filter_data(self):
            if self._curr_item != None:
                return self._curr_item[0]._filter_data
    
    def __init__(self):
        self._filters = {}
        self._iterator = None
        self._curr_item = None
    
    def __iter__(self):
        return self
    
    def __len__(self):
        return len(self._filters)

    def next(self):
        if self._iterator == None:
            self._iterator = self._filters.iteritems()
            #print "init iterator:%s" % self._iterator
        try:    
            self._curr_item = self._iterator.next()
        except:
            self._iterator = None
            raise StopIteration
        else:
            return self._curr_item[1]
        
             
if __name__ == "__main__":            
    
    fs = FilterMap()
    fs.add(1,Filter([(0,'\x0D'),(1,'\x0F')]))
    fs.add(2,Filter([(0,'\x0E'),(1,'\x0F')]))
    fs.add(3,Filter([(0,'\x0F'),(1,'\x0F')]))
    fs.add(4,Filter([(0,'\x0A'),(1,'\x0F')]))

    msg = "\x0F\x0F"
    for fl in fs:
        print "filter for %s : %s" % (fs.get_curr_id(), fl.apply(msg))
    print "==================================="    
    for fl in fs:
        print "filter for %s : %s" % (fs.get_curr_id(), fl.apply(msg))