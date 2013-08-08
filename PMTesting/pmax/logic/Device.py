__author__ = 'KANO'
import xmlrpclib

class DeviceActions:
    ENROLL = "enroll"
    TAMPER = "tamper"
    OPEN = "open"
    STOP = "stop"


class DeviceType:
    CONTACT = "Contact"
    MOTION = "Motion"


class Device:
    Action = None
    ZoneId = 0
    Location = None
    ZoneType = None
    Partition = None
    Type = None

    _tamperOpen = False
    _contactOpen = False

    _actions = {}
    card = xmlrpclib.ServerProxy('http://127.0.0.1:50000')

    _enrollParameters = [("0", "10000", "0", 4, 1),
                         ("0", "1", "0", 4, 1),
                         ("10000", "0", "0", 4, 1),
                         ("1", "0", "0", 4, 1),
                         ("0", "0", "10000", 4, 1)]
    
    _tamperParameters = [(8192, "close" if _tamperOpen else "open", 0.1),
                         (512, "close" if _tamperOpen else "open", 0.1),
                         (32, "close" if _tamperOpen else "open", 0.1),
                         (2, "close" if _tamperOpen else "open", 0.1),
                         ("0", "0", "100000", "0", "close" if _tamperOpen else "open", 0.1)]

    _openParameters = [(16384, "close" if _contactOpen else "open", 0.1),
                         (1024, "close" if _contactOpen else "open", 0.1),
                         (64, "close" if _contactOpen else "open", 0.1),
                         (4, "close" if _contactOpen else "open", 0.1),
                         ("0","0","1000000","0", "close" if _contactOpen else "open", 0.1)]

    def __init__(self, zoneId, location, zone_type, partition, device_type):
        self.ZoneId = zoneId
        self.Location = location
        self.ZoneType = zone_type
        self.Partition = partition
        self.Type = device_type

        self.__initActions()

    def __initActions(self):
        self._actions = {DeviceActions.ENROLL: self.__enroll,
                         DeviceActions.TAMPER: self.__tamper,
                         DeviceActions.OPEN: self.__open}

    def InvokeAction(self):
        self._actions[self.Action](self)

    def Update(self, post_params):
        self.Location = int(post_params.get("location"))
        self.ZoneType = int(post_params.get("zone_type"))
        self.Partition = int(post_params.get("partition"))

    def __enroll(self):
        card.key_b(self._enrollParameters[self.ZoneId])
        return "enrolled"

    def __tamper(self):
        if self.ZoneId == 5:
            card.relaykey_b32(self._tamperParameters[self.ZoneId])
        else:
            card.relaykey(self._tamperParameters[self.ZoneId])
        self._tamperOpen = not self._tamperOpen
        return "tampered"

    def __open(self):
        if self.ZoneId == 5:
            card.relaykey_b32(self._openParameters[self.ZoneId])
        else:
            card.relaykey(self._openParameters[self.ZoneId])
        self._contactOpen = not self.__contactOpen
        return "open smth"
