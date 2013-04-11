# 11 10 02 44 0B 14 00 DD 00 00 00 08 03 F1 03 00 62 0A
from collections import OrderedDict

def hexdump(s):
    if (type(s) is int):
        s = chr(s)
    return ' '.join(["%02X" % ord(i) for i in s ])
#descriptor ?
class OffValLen:

    def __init__(self, name, dict, data):
        self.structure = dict
        self.data = data
        self.name = name
    @property
    def offset(self):
        offset = 0
        for key in self.structure.keys():
            if self.name == key:
                break
            offset += self.structure[key]
        return offset
    @property
    def value(self):
        str = self.data[self.offset:self.offset + self.len]
        # if reversed == True:
        # str = str[::-1]
        value = 0
        pos = 0
        for byte in str:
            value += (ord(byte)<<(pos*8))
            pos += 1
        return value
    @property
    def len(self):    
        return self.structure[self.name]



class Packet: 
    def __init__(self, structure, packet):
        self._packet = packet
        self._structure = structure
        for key in structure.keys():
            self.__dict__[key] = OffValLen(key, structure, packet)    

    @property
    def data(self):
        # print "packet::data" + str(self._structure)
        if("data_len" in self._structure):
            return self._packet[self.data_len.offset + 1:\
                            self.data_len.offset + self.data_len.value + 1]


# descriptor to route to right class
# HPR_Packet().data
# Factory

def create_HPR_object(packet):
    if ord(packet[1]) == 0x10:
        return HPR_0x10_packet(packet)
    elif ord(packet[1]) == 0x26:
        return HPR_0x26_packet(packet)



class HPR_0x10_packet(Packet):
    _structure = OrderedDict([
            ('len',    1),
            ('type',    1),
            ('d0',      1),
            ('sid',     1),
            ('data_len',     1)
        ])

    def __init__(self, packet):

        # self._packet = packet
        Packet.__init__(self, self._structure, packet)
    

# 45 26 00 04 01 2E 0D 04 00 FF 00 00 00 04 05 3E 03 00 10 0E 01 2F 0D 04 00 FF 00 00 00 04 05 3E 03 00 10 0E 01 30 0D 04
# 00 FF 00 00 00 04 05 3E 03 00 10 0E 01 31 0D 04 00 FF 00 00 00 04 05 3E 03 00 10 0E 11 0A
class Record_0x26:
    
    def __init__(self, record):
        self.sids =  []
        self.sid_amount = ord(record[0])
        i = 0
        for i in range(self.sid_amount):
            self.sids.append(ord(record[i + 1]))
        self.dpr_len = ord(record[self.sid_amount + 1]) 
        self.dpr_offset = self.sid_amount + 2
        self.record = record

    @property        
    def data(self):
        # print self.dpr_offset + 1, self.dpr_offset + self.dpr_len + 1
        return self.record[self.dpr_offset: self.dpr_offset + self.dpr_len + 1]

class RecordIterator:
    def __init__(self, records):
        # print "iterator init:" + hexdump(records)
        self._records = records
        self.offset = 0

    def __iter__(self):
        return self

    def next(self):
        sid_amount = ord(self._records[self.offset])
        rec_end = self.offset + ord(self._records[sid_amount + 1]) + 1 + sid_amount
        if(rec_end > len(self._records)):
            raise StopIteration
            # break    
        else:
            record = self._records[self.offset: rec_end + 1]
            self.offset = rec_end + 1
            return Record_0x26(record)
            
            
    

class HPR_0x26_packet(Packet):
    # TODO : add parsing ?
    # record - iterator trough the messages
    # sids, dpr - in each message
    # record like a dpr
    # record.sids (next(), len()) , record.dpr 
    _structure = OrderedDict([
            ('plen',    1),
            ('type',    1),
            ('d0',      1),
            ('d1',     1),
            ('sid_amount',     1)
            # ('sid', '?prev')
            # ('data_len',)

        ])

    def __init__(self, packet):
        # self._packet = packet
        Packet.__init__(self, self._structure, packet)
        self.records = RecordIterator(packet[4:])


        
class DPR_Packet(Packet):
    _structure = OrderedDict([
            ('info',    2),
            ('snum',    1),
            ('id',      3),
            ('mcode',   1),
            ('data_len', 1)
        ])

    def __init__(self, packet):
        # self._packet = packet
        Packet.__init__(self, self._structure, packet)
     
class F0_packet(Packet):
    _structure = OrderedDict([
            ('stm', 1),
            ('protocol', 1),
            ('cmd', 1),
            ('unit_id', 1),
            ('type', 1),
            ('data_len', 1),
            ('test', 1)
        ])

    def __init__(self, packet):
        Packet.__init__(self, self._structure, packet)

                
if __name__ == "__main__":
    
    hpr = create_HPR_object("\x11\x10\x02\x44\x0B\x14\x00\xDD\x00\x00\x00\x08\x03\xF1\x03\x00\x62\x0A")
    dpr = DPR_Packet(hpr.data)
    # dpr = DPR_Packet("\x14\x00\xDD\x00\x00\x00\x08\x03\xF1\x03\x00\x62\x0A")
    assert (dpr.info.value == 0x14)
    assert (dpr.snum.value == 0xDD)
    assert (dpr.id.value == 0)
    assert (dpr.mcode.value == 8)
    assert (dpr.data_len.value == 3)
    assert (hexdump(dpr.data) == "F1 03 00")

    hpr10 = HPR_0x10_packet("\x11\x10\x02\x44\x0B\x14\x00\xDD\x00\x00\x00\x08\x03\xF1\x03\x00\x62\x0A")

    assert (hpr10.data == "\x14\x00\xDD\x00\x00\x00\x08\x03\xF1\x03\x00")

    hpr26 = HPR_0x26_packet("\x45\x26\x00\x04\x01\x2E\x0D\x04\x00\xFF\x00\x00\x00\x04\x05\x3E\x03\x00\x10\x0E\
\x01\x2F\x0D\x04\x00\xFF\x00\x00\x00\x04\x05\x3E\x03\x00\x10\x0F\x01\x30\x0D\x04\x00\xFF\x00\x00\x00\x04\x05\x3E\x03\x00\x10\x10\
\x01\x31\x0D\x04\x00\xFF\x00\x00\x00\x04\x05\x3E\x03\x00\x10\x11\x11\x0A")
    sids = []
    sids_exp = [46,47,48,49]
    recs = []
    recs_exp = ["\x04\x00\xFF\x00\x00\x00\x04\x05\x3E\x03\x00\x10\x0E", "\x04\x00\xFF\x00\x00\x00\x04\x05\x3E\x03\x00\x10\x0F",\
    "\x04\x00\xFF\x00\x00\x00\x04\x05\x3E\x03\x00\x10\x10" , "\x04\x00\xFF\x00\x00\x00\x04\x05\x3E\x03\x00\x10\x11"]
    for rec in hpr26.records:
        sids.extend(rec.sids)
        # print hexdump(rec.data)
        recs.append(rec.data)
    assert (sids == sids_exp)
    assert (recs == recs_exp)
    print "TEST PASSED"
