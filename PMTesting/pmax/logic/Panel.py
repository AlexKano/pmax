__author__ = 'KANO'
#import logging
import xmlrpclib
from pmax.data.Constants import Constants
from pmax.core.Cache import GlobalStorage


class PanelActions:
    NEXT = "next"
    PREV = "back"
    OK = "ok"

    BTN_0 = "0"
    BTN_1 = "1"
    BTN_2 = "2"
    BTN_3 = "3"
    BTN_4 = "4"
    BTN_5 = "5"
    BTN_6 = "6"
    BTN_7 = "7"
    BTN_8 = "8"
    BTN_9 = "9"

    AWAY = "away"
    HOME = "home"
    DISARM = "off"
    DIES = "#"
    LOG = "*"

    EMRG = "emergency"
    PANIC = "panic"
    FIRE = "fire"

    LOGIN_TO_INST = "Login To Instance"
    LOGIN_TO_USER = "Login To User"
    CUSTOM_ACTIONS_LIST = [LOGIN_TO_INST, LOGIN_TO_USER]

    RUN_CUSTOM = "custom"


class Panel:
    PANEL_CACHE_KEY_TYPE = "PANEL_CACHE_KEY_"

    _navigator = None
    Devices = []
    Type = None
    Action = None
    CustomActions = {}

    def __init__(self, panel_type):
        self.Type = self.__getType(panel_type)

        self.__initCustomActions()
        self._navigator = xmlrpclib.ServerProxy('http://127.0.0.1:50000')

    def GetScreen(self):
        return self._navigator.get_lcd()

    def Show_time(self):
        self._navigator.start_vkp_mode()
    
    def GetDeviceByZone(self, zoneId):
        for d in self.Devices:
            if d.ZoneId == zoneId:
                return d
        return None

    def InvokeAction(self):
        if self.Action == PanelActions.RUN_CUSTOM:
            self.__runCustomAction()
        else:
            self._navigator.send_key(self.Action)

    @classmethod
    def GetByType(cls, panel_type):
        return GlobalStorage.Panels.get(cls.PANEL_CACHE_KEY_TYPE + panel_type)
        # return cache.get(cls.PANEL_CACHE_KEY_TYPE + panel_type)

    @classmethod
    def SetByType(cls, panel):
        GlobalStorage.Panels[cls.PANEL_CACHE_KEY_TYPE + panel.Type] = panel
        # cache.set(cls.PANEL_CACHE_KEY_TYPE + panel.Type, panel)


    ######## private methods ########
    def __getType(self, panel_type):
        return Constants.POWER_MAX_10 if panel_type == Constants.POWER_MAX_10 else Constants.POWER_MAX_30

    def __initCustomActions(self):
        if not self.CustomActions:
            self.CustomActions = {PanelActions.LOGIN_TO_INST: self.__logToInst,
                                  PanelActions.LOGIN_TO_USER: self.__logToUser}

    def __runCustomAction(self):
        self.CustomActions[self.Action](self)

    def __logToInst(self):
        self._navigator.login('9999')

    def __logToUser(self):
        self._navigator.loginToUserSettings('1111')