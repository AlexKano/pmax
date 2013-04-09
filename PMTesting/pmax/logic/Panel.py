__author__ = 'KANO'
#import random
#import logging
import xmlrpclib

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
    navigator = xmlrpclib.ServerProxy('http://127.0.0.1:8000')
    Action = None
    CustomAction = None

    # _actions = {}
    # _actionKeyDict = {}

    def __init__(self, params):
        self.Action = params.get('action', None)
        self.CustomAction = params.get('custom_action', None)
        #pass
        #self.__initActions()
        #logging.basicConfig(filename='example.log', level=logging.INFO)

    def GetScreen(self):
        #s = ["READY", "STEADY", "XYU", "AI", "LOS", "BENITO"]
        #return s[random.randint(0, len(s) - 1)]
        return self.navigator.get_lcd()

    #def LogToInst(self, event):
       # navigator.login('9999')
    #
    #def LogToUser(self, event):
        #self.navigator.loginToUserSettings('1111')

    def InvokeAction(self):
	    #pass
        #logging.info(self.Action)
        if self.Action == PanelActions.RUN_CUSTOM:
            self.__runCustomAction()
        else:
            self.navigator.send_key(self.Action)
