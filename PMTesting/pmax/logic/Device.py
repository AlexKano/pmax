__author__ = 'KANO'


class DeviceActions:
    ENROLL = "enroll"
    TAMPER = "tamper"
    OPEN = "open"
    STOP = "stop"


class Device:
    ZoneId = 0
    Location = None
    ZoneType = None
    Partition = None
    Action = None

    _tamperOpen = False
    _contactOpen = False

    _updateScreen = False

    _actions = {}

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

    def __init__(self, params=None):
        if params is None:
            return

        self.ZoneId = int(params.get('zone', 0))
        # self.Location = params.get('location')
        # self.ZoneType = params.get('zone_type')
        # self.Partition = params.get('partition')
        self.Action = params.get('action')

        # self.__initActions()

    def __initActions(self):
        self._actions = {DeviceActions.ENROLL: self.__enroll,
                         DeviceActions.TAMPER: self.__tamper,
                         DeviceActions.OPEN: self.__open}

    def InvokeAction(self):
        self._actions[self.Action](self)

    def __enroll(self):
        #card.key_b(self._enrollParameters[self.ZoneId])
        return "enrolled"

    def __tamper(self):
        # if self.ZoneId == 5:
        #     card.relaykey_b32(self._tamperParameters[self.ZoneId])
        # else:
        #     card.relaykey(self._tamperParameters[self.ZoneId])
        # self._tamperOpen = not self._tamperOpen
        return "tampered"

    def __open(self):
        # self._contactOpen = not self.__contactOpen
        return "open smth"
