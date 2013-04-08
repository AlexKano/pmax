#!/usr/bin/python
# -*- coding: utf-8 -*-
# PMTT.py

# import wx
# import select
# import threading
# import sys
#
# sys.path.append('./Modules')
# sys.path.append('./../PowerMaster')
# import serial
# import os
# import time
# import datetime
# import devices
# import random
# import card
# import out
# import navigator
# import com
# import serial_port_craft
#import ssh
#import KP140
from time import strftime


card.relaykey_b32("11111111", "11111111", "11111111", "11111111", "close", 0.1)


class BackToFactoryDefault(wx.Dialog):
    def __init__(self, parent, title):
        super(BackToFactoryDefault, self).__init__(parent=parent, title=title, size=(250, 230))
        ContactZ1 = wx.Button(self, 80, 'Contact  Z1', (85, 20), (70, -1))
        self.Bind(wx.EVT_BUTTON, self.Zone1, id=80)
        ContactZ2 = wx.Button(self, 81, 'Contact  Z2', (85, 50), (70, -1))
        self.Bind(wx.EVT_BUTTON, self.Zone2, id=81)
        ContactZ3 = wx.Button(self, 82, 'Contact  Z3', (85, 80), (70, -1))
        self.Bind(wx.EVT_BUTTON, self.Zone3, id=82)
        ContactZ4 = wx.Button(self, 83, 'Contact  Z4', (85, 110), (70, -1))
        self.Bind(wx.EVT_BUTTON, self.Zone4, id=83)
        ContactZ5 = wx.Button(self, 84, 'Contact  Z5', (85, 140), (70, -1))
        self.Bind(wx.EVT_BUTTON, self.Zone5, id=84)
        Keyfobb = wx.Button(self, 85, 'Keyfob', (85, 170), (70, -1))
        self.Bind(wx.EVT_BUTTON, self.Keyfobb, id=85)

    def Zone1(self, event):
        card.key_b("0", "10000", "0", 10, 1)

    def Zone2(self, event):
        card.key_b("0", "1", "0", 10, 1)

    def Zone3(self, event):
        card.key_b("10000", "0", "0", 10, 1)

    def Zone4(self, event):
        card.key_b("1", "0", "0", 10, 1)

    def Zone5(self, event):
        card.key_b("0", "0", "10000", 10, 1)

    def Keyfobb(self, event):
        card.key_b("0", "0", "1000", 5.5, 0.1)
        card.key_b("0", "0", "1000", 1, 0.1)
        card.key_b("0", "0", "1000", 6, 0.1)


global framex, framey
framex = 750
framey = 289
global string1
string1 = ''


class EnrollAllDevs(wx.Dialog):
    def __init__(self, parent, title):
        super(EnrollAllDevs, self).__init__(parent=parent, title=title, size=(270, 130))
        self.gauge = wx.Gauge(self, range=96, size=(250, 25), pos=(5, 30))
        self.Status = wx.StaticText(self, 1111, 'Status: Ready to enroll', (20, 10), (290, -1))
        self.StartBtn = wx.Button(self, 1112, 'Start Enrolling', (85, 70), (90, -1))
        self.Bind(wx.EVT_BUTTON, self.StartEnroll, id=1112)

    def CheckEnroll(self, count, RelleMask, EnrolingTime):
        string1 = "DEVICE ENROLLED"
        timeout = 7
        res = False
        cc = 0
        while res == False:
            for k in range(timeout * 3):
                LCD1 = navigator.read()
                res = string1 in LCD1
                time.sleep(0.33)
                res1 = "ALREADY" in LCD1
                if res1:
                    cc += 1
                    navigator.send_key_fast('ok', 0.5)
                    if cc == 2:
                        return
                if res == True:
                    return
            card.key_b(RelleMask[0][count - 1], RelleMask[1][count - 1], RelleMask[2][count - 1], EnrolingTime, 1)


    def SetOption(self, option):

        test = navigator.read()
        if (option in test):
            time.sleep(0.5)
        else:
            while not (option in test):
                navigator.send_key_fast("next", 0.5)
                test = navigator.read()
        navigator.send_key_fast('ok', 0.1)

    #time.sleep(0.5)

    def StartEnroll(self, event):
        self.StartBtn.Disable()
        navigator.login('9999')
        navigator.search_menu('DEVICES')
        navigator.send_key_fast('ok', 0.1)
        navigator.send_key_fast('ok', 0.1)
        RelleMask = [['0', '0', '10000', '1', '0', '0'], ['10000', '1', '0', '0', '0', '0'],
                     ['0', '0', '0', '0', '10000', '1000']]
        ZoneTypes = ['Interior', 'Inter-Follow', 'Perim-Follow']
        for i in range(6):
            c = i + 1
            EnrolingTime = 4 if c <= 5 else 6
            EnrollStatus = "Status: {0}st magnet is Enrolling".format(c) if c <= 5 else  "Status: keyfob is Enrolling"
            self.Status.SetLabel(EnrollStatus)
            card.key_b(RelleMask[0][i], RelleMask[1][i], RelleMask[2][i], EnrolingTime, 1)
            self.CheckEnroll(c, RelleMask, EnrolingTime)
            GuageNumber = c * 8 + i * 8
            self.gauge.SetValue(GuageNumber)
            navigator.send_key_fast('ok', 0.5)
            self.Status.SetLabel("Status: Configuring")
            if c > 1 and c < 5:
                navigator.send_key_fast('ok', 0.5)
                navigator.search_menu('ZONE TYPE')
                navigator.send_key_fast('ok', 0.1)
                self.SetOption(ZoneTypes[c - 2])
                navigator.send_key_fast('home', 0.1)
                time.sleep(1)
                navigator.send_key_fast('home', 0.1)
            elif c == 1 or c == 5:
                navigator.send_key_fast('home', 0.1)
                navigator.send_key_fast('ok', 0.1)
            GuageNumber += 8
            self.gauge.SetValue(GuageNumber)
            if c == 6:
                navigator.send_key_fast('ok', 0.5)
                time.sleep(0.5)
                navigator.send_key_fast('ok', 0.1)
                navigator.send_key_fast('ok', 0.1)
                self.SetOption('Skip')
                time.sleep(1)
                navigator.send_key_fast('away', 1)
                navigator.send_key_fast('ok', 0.1)
                self.gauge.SetValue(96)
                self.Status.SetLabel('All devices has been enrolled successfully!!!')


class PowerMaster(wx.Frame):
    def __init__(self, parent, ID, title):
        wx.Frame.__init__(self, parent, ID, title, size=(framex, framey))


        ##############GUI########################
        panel = wx.Panel(self, size=(750, 400))
        ###############################################################PanelKeyBoard#######################

        btn1 = wx.Button(panel, 200, '1', (280, 232), (40, -1))
        btn2 = wx.Button(panel, 201, '2', (322, 232), (40, -1))
        btn3 = wx.Button(panel, 202, '3', (364, 232), (40, -1))
        btn4 = wx.Button(panel, 203, '4', (280, 262), (40, -1))
        btn5 = wx.Button(panel, 204, '5', (322, 262), (40, -1))
        btn6 = wx.Button(panel, 205, '6', (364, 262), (40, -1))
        btn7 = wx.Button(panel, 206, '7', (280, 292), (40, -1))
        btn8 = wx.Button(panel, 207, '8', (322, 292), (40, -1))
        btn9 = wx.Button(panel, 208, '9', (364, 292), (40, -1))
        btn0 = wx.Button(panel, 209, '0', (322, 322), (40, -1))
        btnlog = wx.Button(panel, 210, '*|log', (280, 322), (40, -1))
        btnds = wx.Button(panel, 211, '#', (364, 322), (40, -1))
        btnemerg = wx.Button(panel, 212, 'Emerg', (280, 352), (40, -1))
        btnpanic = wx.Button(panel, 213, 'Panic', (322, 352), (40, -1))
        btnfire = wx.Button(panel, 214, 'Fire', (364, 352), (40, -1))

        self.Bind(wx.EVT_BUTTON, self.btn1, id=200)
        self.Bind(wx.EVT_BUTTON, self.btn2, id=201)
        self.Bind(wx.EVT_BUTTON, self.btn3, id=202)
        self.Bind(wx.EVT_BUTTON, self.btn4, id=203)
        self.Bind(wx.EVT_BUTTON, self.btn5, id=204)
        self.Bind(wx.EVT_BUTTON, self.btn6, id=205)
        self.Bind(wx.EVT_BUTTON, self.btn7, id=206)
        self.Bind(wx.EVT_BUTTON, self.btn8, id=207)
        self.Bind(wx.EVT_BUTTON, self.btn9, id=208)
        self.Bind(wx.EVT_BUTTON, self.btn0, id=209)
        self.Bind(wx.EVT_BUTTON, self.btnlog, id=210)
        self.Bind(wx.EVT_BUTTON, self.btnds, id=211)
        self.Bind(wx.EVT_BUTTON, self.btnemerg, id=212)
        self.Bind(wx.EVT_BUTTON, self.btnpanic, id=213)
        self.Bind(wx.EVT_BUTTON, self.btnfire, id=214)

        ###############################################################PanelKeyBoard#######################

        wx.StaticText(panel, -1, 'Zone #', (25, 20))
        wx.StaticText(panel, -1, 'Zone #', (25, 50))
        wx.StaticText(panel, -1, 'Zone #', (25, 80))
        wx.StaticText(panel, -1, 'Zone #', (25, 110))
        wx.StaticText(panel, -1, 'Zone #', (25, 140))
        wx.StaticText(panel, -1, 'Location', (125, 3))
        wx.StaticText(panel, -1, 'Zone Type', (220, 3))
        wx.StaticText(panel, -1, 'Partition', (305, 3))

        wx.StaticBox(panel, -1, 'Write string to option', (415, 234), size=(230, 46), style=10)
        wx.TextCtrl(panel, 2001, 'www.djuice.com.ua', (420, 252), (150, -1))
        self.Bind(wx.EVT_TEXT, self.TexttoEnter, id=2001)
        WriteToPanelBtn = wx.Button(panel, 2000, 'WriteToPanel', (572, 252), (70, -1))
        BreakUARTPlink = wx.Button(panel, 2100, 'AUTTESTAUT = Plink', (502, 320), (110, -1))
        BreakUARTgsm = wx.Button(panel, 2110, 'AUTTESTAUT = GSM', (502, 350), (110, -1))
        self.PowerUPP = wx.Button(panel, 2111, 'Power OFF', (622, 350), (100, -1))
        self.Bind(wx.EVT_BUTTON, self.WriteStrToPanel, id=2000)
        CreateMaxUsers = wx.Button(panel, 2002, 'Create 48 Users', (502, 290), (85, -1))
        self.Bind(wx.EVT_BUTTON, self.CreateMaxUsers, id=2002)
        self.ReleasePorts = wx.Button(panel, 2003, 'Releas port', (502, 375), (85, -1))
        self.Bind(wx.EVT_BUTTON, self.ReleasePort, id=2003)

        #Keyfob gui
        wx.StaticBox(panel, -1, 'KeyFob', (680, 2), size=(52, 200))
        Away = wx.Button(panel, 70, 'Away', (686, 17), (40, -1))
        Home = wx.Button(panel, 71, 'Home', (686, 47), (40, -1))
        Disarm = wx.Button(panel, 72, 'Disarm', (686, 77), (40, -1))
        Auxb = wx.Button(panel, 73, '*', (686, 107), (40, -1))
        Enroll = wx.Button(panel, 74, 'Enroll', (686, 137), (40, -1))
        Panic = wx.Button(panel, 75, 'Panic', (686, 167), (40, 30))

        self.Bind(wx.EVT_BUTTON, self.PowerUP, id=2111)
        self.Bind(wx.EVT_BUTTON, self.BreakThruUARTp, id=2100)
        self.Bind(wx.EVT_BUTTON, self.BreakThruUARTg, id=2110)
        self.Bind(wx.EVT_BUTTON, self.Away, id=70)
        self.Bind(wx.EVT_BUTTON, self.Home, id=71)
        self.Bind(wx.EVT_BUTTON, self.Disarm, id=72)
        self.Bind(wx.EVT_BUTTON, self.Auxb, id=73)
        self.Bind(wx.EVT_BUTTON, self.Enroll, id=74)
        self.Bind(wx.EVT_BUTTON, self.Panicf, id=75)
        self.sc = wx.SpinCtrl(panel, -1, '', (65, 17), (42, -1))
        self.sc.SetRange(1, 64)
        self.sc.SetValue(1)
        self.sc = wx.SpinCtrl(panel, -1, '', (65, 47), (42, -1))
        self.sc.SetRange(1, 64)
        self.sc.SetValue(2)
        self.sc = wx.SpinCtrl(panel, -1, '', (65, 77), (42, -1))
        self.sc.SetRange(1, 64)
        self.sc.SetValue(3)
        self.sc = wx.SpinCtrl(panel, -1, '', (65, 107), (42, -1))
        self.sc.SetRange(1, 64)
        self.sc.SetValue(4)
        self.sc = wx.SpinCtrl(panel, -1, '', (65, 137), (42, -1))
        self.sc.SetRange(1, 64)
        self.sc.SetValue(5)

        Partitions = ['1', '2', '3', '1+2', '1+3', '1+2+3', '2+3']
        ZoneNames = ['Front door', 'Garage', 'Garage door', 'Back door', 'Child room', 'Guest room', 'Hall', 'Kitchen',
                     'Laundry room', 'Living room', 'Master bath', 'Master Bdrm', 'Office', 'Upstairs', 'Utility room',
                     'Yard', 'Custom 1', 'Custom 2', 'Custom 3', 'Custom 4', 'Custom 5', 'Attic', 'Basement',
                     'Bathroom', 'Bedroom', 'Closet', 'Den', 'Dining room', 'Downstairs', 'Emergency', 'Fire']
        ZoneTypes = ['Entry Delay1', 'Entry Delay2', 'Interior', 'Inter-follow', 'Perimeter', 'Perim-follow',
                     'Home-Delay', 'Arming Key', 'Emergency', 'Guard Keybox', 'Non-alarm', '24h silent', '24h audible']
        wx.ComboBox(panel, 100, pos=(202, 17), value=ZoneTypes[0], size=(90, -1), choices=ZoneTypes,
                    style=wx.CB_READONLY)
        wx.ComboBox(panel, 101, pos=(202, 47), value=ZoneTypes[2], size=(90, -1), choices=ZoneTypes,
                    style=wx.CB_READONLY)
        wx.ComboBox(panel, 102, pos=(202, 77), value=ZoneTypes[3], size=(90, -1), choices=ZoneTypes,
                    style=wx.CB_READONLY)
        wx.ComboBox(panel, 103, pos=(202, 107), value=ZoneTypes[5], size=(90, -1), choices=ZoneTypes,
                    style=wx.CB_READONLY)
        wx.ComboBox(panel, 104, pos=(202, 137), value=ZoneTypes[4], size=(90, -1), choices=ZoneTypes,
                    style=wx.CB_READONLY)

        wx.ComboBox(panel, -1, pos=(110, 17), value=ZoneNames[0], size=(90, -1), choices=ZoneNames,
                    style=wx.CB_READONLY)
        wx.ComboBox(panel, -1, pos=(110, 47), value=ZoneNames[1], size=(90, -1), choices=ZoneNames,
                    style=wx.CB_READONLY)
        wx.ComboBox(panel, -1, pos=(110, 77), value=ZoneNames[2], size=(90, -1), choices=ZoneNames,
                    style=wx.CB_READONLY)
        wx.ComboBox(panel, -1, pos=(110, 107), value=ZoneNames[3], size=(90, -1), choices=ZoneNames,
                    style=wx.CB_READONLY)
        wx.ComboBox(panel, -1, pos=(110, 137), value=ZoneNames[4], size=(90, -1), choices=ZoneNames,
                    style=wx.CB_READONLY)

        wx.ComboBox(panel, -1, pos=(294, 17), value=Partitions[0], size=(60, -1), choices=Partitions,
                    style=wx.CB_READONLY)
        wx.ComboBox(panel, -1, pos=(294, 47), value=Partitions[0], size=(60, -1), choices=Partitions,
                    style=wx.CB_READONLY)
        wx.ComboBox(panel, -1, pos=(294, 77), value=Partitions[0], size=(60, -1), choices=Partitions,
                    style=wx.CB_READONLY)
        wx.ComboBox(panel, -1, pos=(294, 107), value=Partitions[0], size=(60, -1), choices=Partitions,
                    style=wx.CB_READONLY)
        wx.ComboBox(panel, -1, pos=(294, 137), value=Partitions[0], size=(60, -1), choices=Partitions,
                    style=wx.CB_READONLY)

        EnrollButton1 = wx.Button(panel, 11, 'Enroll', (357, 17), (40, -1))
        EnrollButton2 = wx.Button(panel, 12, 'Enroll', (357, 47), (40, -1))
        EnrollButton3 = wx.Button(panel, 13, 'Enroll', (357, 77), (40, -1))
        EnrollButton4 = wx.Button(panel, 14, 'Enroll', (357, 107), (40, -1))
        EnrollButton5 = wx.Button(panel, 15, 'Enroll', (357, 137), (40, -1))

        self.Bind(wx.EVT_BUTTON, self.Enroll1, id=11)
        self.Bind(wx.EVT_BUTTON, self.Enroll2, id=12)
        self.Bind(wx.EVT_BUTTON, self.Enroll3, id=13)
        self.Bind(wx.EVT_BUTTON, self.Enroll4, id=14)
        self.Bind(wx.EVT_BUTTON, self.Enroll5, id=15)

        self.OpenTamper1 = wx.Button(panel, 21, 'Open Tamper', (401, 17), (80, -1))
        self.OpenTamper2 = wx.Button(panel, 22, 'Open Tamper', (401, 47), (80, -1))
        self.OpenTamper3 = wx.Button(panel, 23, 'Open Tamper', (401, 77), (80, -1))
        self.OpenTamper4 = wx.Button(panel, 24, 'Open Tamper', (401, 107), (80, -1))
        self.OpenTamper5 = wx.Button(panel, 25, 'Open Tamper', (401, 137), (80, -1))
        self.OpenTamper1.Bind(wx.EVT_BUTTON, self.TampOpen1, id=21)
        self.OpenTamper2.Bind(wx.EVT_BUTTON, self.TampOpen2, id=22)
        self.OpenTamper3.Bind(wx.EVT_BUTTON, self.TampOpen3, id=23)
        self.OpenTamper4.Bind(wx.EVT_BUTTON, self.TampOpen4, id=24)
        self.OpenTamper5.Bind(wx.EVT_BUTTON, self.TampOpen5, id=25)

        self.Open1 = wx.Button(panel, 41, 'Open', (496, 17), (50, -1))
        self.Open2 = wx.Button(panel, 42, 'Open', (496, 47), (50, -1))
        self.Open3 = wx.Button(panel, 43, 'Open', (496, 77), (50, -1))
        self.Open4 = wx.Button(panel, 44, 'Open', (496, 107), (50, -1))
        self.Open5 = wx.Button(panel, 45, 'Open', (496, 137), (50, -1))
        Stop1 = wx.Button(panel, 51, 'Stop', (602, 17), (50, -1))
        Stop2 = wx.Button(panel, 52, 'Stop', (602, 47), (50, -1))
        Stop3 = wx.Button(panel, 53, 'Stop', (602, 77), (50, -1))
        Stop4 = wx.Button(panel, 54, 'Stop', (602, 107), (50, -1))
        Stop5 = wx.Button(panel, 55, 'Stop', (602, 137), (50, -1))

        wx.StaticLine(panel, -1, (15, 43), (645, 1))
        wx.StaticLine(panel, -1, (15, 73), (645, 1))
        wx.StaticLine(panel, -1, (15, 103), (645, 1))
        wx.StaticLine(panel, -1, (15, 133), (645, 1))
        wx.StaticLine(panel, -1, (15, 163), (645, 1))

        self.Bind(wx.EVT_BUTTON, self.Start1, id=41)
        self.Bind(wx.EVT_BUTTON, self.Stop1, id=51)
        self.Bind(wx.EVT_BUTTON, self.Start2, id=42)
        self.Bind(wx.EVT_BUTTON, self.Stop2, id=52)
        self.Bind(wx.EVT_BUTTON, self.Start3, id=43)
        self.Bind(wx.EVT_BUTTON, self.Stop3, id=53)
        self.Bind(wx.EVT_BUTTON, self.Start4, id=44)
        self.Bind(wx.EVT_BUTTON, self.Stop4, id=54)
        self.Bind(wx.EVT_BUTTON, self.Start5, id=45)
        self.Bind(wx.EVT_BUTTON, self.Stop5, id=55)

        self.statusbar = self.CreateStatusBar(5)
        self.statusbar.SetStatusText('Zone #1 is Closed', 0)
        self.statusbar.SetStatusText('Zone #2 is Closed', 1)
        self.statusbar.SetStatusText('Zone #3 is Closed', 2)
        self.statusbar.SetStatusText('Zone #4 is Closed', 3)
        self.statusbar.SetStatusText('Zone #5 is Closed', 4)

        BacktoFactoryrDefault = wx.Button(panel, 77, 'BacktoFactory', (20, 168), (90, -1))
        NextPanelBut = wx.Button(panel, 78, '>>', (322, 168), (40, -1))
        PrewPanelBut = wx.Button(panel, 79, '<<', (280, 168), (40, -1))
        OKPanelBut = wx.Button(panel, 26, 'OK', (364, 168), (40, -1))
        LogToInst = wx.Button(panel, 27, 'LogToInst', (20, 200), (60, -1))
        EnrollAll = wx.Button(panel, 48, 'EnrollAllDevs', (144, 200), (70, -1))
        LogToUser = wx.Button(panel, 28, 'LogToUser', (82, 200), (60, -1))
        Awayp = wx.Button(panel, 36, 'Away', (475, 200), (35, -1))
        Homep = wx.Button(panel, 37, 'Home', (511, 200), (35, -1))
        Disarmp = wx.Button(panel, 38, 'Disarm', (547, 200), (39, -1))

        self.Bind(wx.EVT_BUTTON, self.NextPanelBut, id=78)
        self.Bind(wx.EVT_BUTTON, self.EnrollAllDev, id=48)
        self.Bind(wx.EVT_BUTTON, self.PrewPanelBut, id=79)
        self.Bind(wx.EVT_BUTTON, self.OKPanelBut, id=26)
        self.Bind(wx.EVT_BUTTON, self.LogToInst, id=27)
        self.Bind(wx.EVT_BUTTON, self.LogToUser, id=28)
        self.Bind(wx.EVT_BUTTON, self.BacktoFact, id=77)
        self.Bind(wx.EVT_BUTTON, self.Awayp, id=36)
        self.Bind(wx.EVT_BUTTON, self.Homep, id=37)
        self.Bind(wx.EVT_BUTTON, self.Disarmp, id=38)

        self.scr = wx.StaticBox(panel, -1, '', (245, 190), size=(220, 40), style=10)
        self.Screen = wx.StaticText(panel, 100, '', (250, 200), (100, -1), wx.ALIGN_CENTER)
        self.Screen.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD))
        #self.statusbar.SetStatusText(self.State, 5)
        self.cb = wx.CheckBox(panel, 29, 'Show Panel Screen', (130, 172))
        self.cb.SetValue(False)
        wx.EVT_CHECKBOX(panel, 29, self.ScreenShow)


        ###############################Stopwatch1################################
        self.mutex = threading.Lock()
        self.timestr = '00:00:00'
        self.starter = [1, 1, 1, 1, 1]
        self.timing = '00:00:0'
        self.ThrId = [0, 0, 0, 0, 0]
        self.ThrId1 = [0, 0, 0, 0, 0]
        self.ThreadActinity = 0
        #self.statusbar.SetStatusText(self.timestr)
        '''self.TimeFields = []
		self.TimeFields.append(wx.StaticText(panel, 3, self.timing, (552, 20), (50, -1)))
		self.TimeFields.append(wx.StaticText(panel, 4, self.timing, (552, 52), (50, -1)))
		self.TimeFields.append(wx.StaticText(panel, 5, self.timing, (552, 84), (50, -1)))
		self.TimeFields.append(wx.StaticText(panel, 6, self.timing, (552, 112), (50, -1)))
		self.TimeFields.append(wx.StaticText(panel, 7, self.timing, (552, 142), (50, -1)))'''
        self.Timer1 = wx.StaticText(panel, 3, self.timing, (552, 20), (50, -1))
        self.Timer2 = wx.StaticText(panel, 4, self.timing, (552, 52), (50, -1))
        self.Timer3 = wx.StaticText(panel, 5, self.timing, (552, 84), (50, -1))
        self.Timer4 = wx.StaticText(panel, 6, self.timing, (552, 112), (50, -1))
        self.Timer5 = wx.StaticText(panel, 7, self.timing, (552, 142), (50, -1))
        wx.Button(panel, 1, 'Exit', (615, 167), (60, 35))

        self.Bind(wx.EVT_BUTTON, self.ExitDialog, id=1)
        #self._start = 0.0
        self._elapsedtime = 0.0
        self._running1 = 0
        #self.starter = 1
        self.k1, self.k2, self.k3, self.k4, self.k5, self.oc1, self.oc2, self.oc3, self.oc4, self.oc5 = 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
        self.PowerFlag = 0
        self.PortFlag = 0
        #panel.SetFocus()
        self.Centre()
        self.Show()

    def ReleasePort(self, event):
        if self.PortFlag == 0:
            devices.s.close()
            self.ReleasePorts.SetLabel('Open port')
            self.PortFlag = 1
            time.sleep(2)
            self.Screen.SetForegroundColour(wx.Colour(255, 0, 0))
            self.Screen.SetLabel('COM IS CLOSED')
        else:
            devices.s = serial.Serial('COM1', 9600, timeout=0)
            time.sleep(0.2)
            self.ReleasePorts.SetLabel('Release port')
            self.PortFlag = 0
            self.Screen.SetForegroundColour(wx.Colour(0, 0, 0))

    def BreakThruUART(self, MediaChannel='gsm'):
        devices.s.close()
        time.sleep(0.5)
        strCom = 'COM1'
        com_thr = serial_port_craft.COM_thr()
        com_thr.open_serial_port(strCom, 9600, 'PortAuto')
        BreakPakages = {'plink': '\x0D\xF0\x02\x00\x00\x09\x37\x00\x3B\xFF\x01\x00\x00\x00\x02\x27\x9B\x0A',
                        'gsm': '\x0D\xF0\x02\x00\x00\x09\x37\x00\x3B\xFF\x01\x00\x00\x00\x01\x44\xAB\x0A'}
        com_thr.ser.write('\x0D\xF0\x05\x37\x01\x00\x40\xA1\x0A') # open UART
        time.sleep(3)
        com_thr.ser.write(BreakPakages[MediaChannel])              # send 'change media' command
        time.sleep(3)
        com_thr.ser.write('\x0D\xF0\x06\x37\x01\x00\x25\x9B\x0A') # close UART
        time.sleep(3)
        com_thr.stop_event.set()
        com_thr.join()
        com_thr.close_serial_port()
        time.sleep(0.2)
        strCom = com.ComPanel()

        devices.s = serial.Serial(strCom, 9600, timeout=0)
        time.sleep(0.2)
        print 'UART has been cracked successfully!'

    def PowerUP(self, event):
        if self.PowerFlag == 0:
            card.relaykey_b32("1000", "0", "0", "0", "open", 0.1)
            self.PowerUPP.SetLabel('Power ON')
            self.PowerFlag = 1
        else:
            card.relaykey_b32("1000", "0", "0", "0", "close", 0.1)
            #self.statusbar.SetForegroundColour (wx.Colour (255, 255, 0))
            self.PowerUPP.SetLabel('Power OFF')
            self.PowerFlag = 0


    def TexttoEnter(self, event):
        global string1
        string1 = event.GetString()


    def BreakThruUARTp(self, event):
        self.BreakThruUART(MediaChannel='plink')

    def BreakThruUARTg(self, event):
        self.BreakThruUART(MediaChannel='gsm')

    def CreateMaxUsers(self, event):
        navigator.loginToUserSettings('1111')
        navigator.send_key_fast('ok')
        UsersNumber = 48
        self.AddUsers(UsersNumber)
        navigator.send_key_fast('away')
        time.sleep(0.5)
        navigator.send_key_fast('ok')


    def AddUsers(self, usersnumber):
        for i in range(2, usersnumber + 1):
            navigator.send_key_fast('next')
            navigator.send_key_fast('ok')
            navigator.send_key_fast('0')
            navigator.send_key_fast('0')
            if i < 10:
                navigator.send_key_fast('0')
                navigator.send_key_fast(str(i))
            else:
                i = str(i)
                navigator.send_key_fast(i[0])
                navigator.send_key_fast(i[1])
                print i
            navigator.send_key_fast('ok')
            navigator.send_key_fast('ok')
            time.sleep(0.5)


    def WriteStrToPanel(self, event):
        global string1
        string = string1
        if len(string) == 0:
            string = 'www.djuice.com.ua'
        navigator.send_key_fast("off", 0.5)
        lens = len(string)
        n = 0
        for char in string:
            for i in range(150):
                key = '2' if char in '@.' else '8'
                navigator.send_key_fast(key, 0.1)
                lcd = navigator.read()
                n_lcd = n if n < 15 else 15
                if char == '@' and ord(lcd[n_lcd]) == 7:
                    break
                if char == lcd[n_lcd]:
                    break
            navigator.send_key_fast("next", 0.5)
            n = n + 1
        navigator.send_key_fast("back", 0.5)
		navigator.send_key_fast("ok",3)	

	def BacktoFact(self, event):
		bcktf = BackToFactoryDefault(None, title='Back to factory default for devices')
		bcktf.ShowModal()
		bcktf.Destroy()

	def EnrollAllDev(self, event):
		ead = EnrollAllDevs(None, title='Enrolling dialog')
		ead.ShowModal()
		ead.Destroy()

	def ScreenShow(self, event):
		if self.cb.GetValue():
			self.t2 = threading.Thread(target = self.ScreenShow1, args=("",))
			self.t2.daemon = True
			self.t2.start()
		else:
			self.t2._Thread__stop()
			time.sleep(0.7)
			self.Screen.SetLabel('')

	def ScreenShow1(self, PM):
		while self.t2.isAlive():
			State = "{0}{1}".format(PM,navigator.read())
			with self.mutex:
				self.Screen.SetLabel(State)
			time.sleep(0.5)

		
			
			
			
	#######################################MY TIMER##########################################
	def StartThread(self, mutex):
		if self.starter[0] == 1:
			self.ThrId[0] = 1
			self.ThreadActinity = 1
			mstimer = 0
			self.Timer21 = threading.Thread(target = self.MyTimer, args=(mstimer,mutex))
			self.Timer21.start()

	def MyTimer(self, mstimer,mutex):
		while(self.starter[0] ==1):
			mstimer +=1
			mtimer =  int(mstimer/600)
			stimer = int(mstimer - mtimer*600)/10
			htimer = int(mstimer - mtimer*600 - stimer*10)
			timing = '%02d:%02d:%02s' % (mtimer, stimer, htimer)
			wx.GetApp().Yield(True)
			time.sleep(0.088)
			#wx.CallAfter(self.TimerLabel(timing))
			self.TimerLabel(timing,mutex)

	def TimerLabel(self, timing,mutex):
		with mutex:
			self.Timer1.SetLabel(timing)
		time.sleep(0.01)
	#________________________________________________________________________________
	def StartThread1(self,mutex):
		if self.starter[1] == 1:
			mstimer1 = 0
			self.ThrId[1] = 1
			self.ThreadActinity = 1
			self.Timer22 = threading.Thread(target = self.MyTimer1, args=(mstimer1,mutex))
			self.Timer22.start()

	def MyTimer1(self, mstimer1,mutex):
		while(self.starter[1] ==1):
			mstimer1 +=1
			mtimer1 =  int(mstimer1/600)
			stimer1 = int(mstimer1 - mtimer1*600)/10
			htimer1 = int(mstimer1 - mtimer1*600 - stimer1*10)
			timing1 = '%02d:%02d:%02s' % (mtimer1, stimer1, htimer1)
			time.sleep(0.088)
			wx.GetApp().Yield(True)
			self.TimerLabel1(timing1,mutex)
			
	def TimerLabel1(self, timing1,mutex):
		with mutex:
			self.Timer2.SetLabel(timing1)
		time.sleep(0.01)
	#________________________________________________________________________________
	def StartThread2(self,mutex):
		if self.starter[2] == 1:
			mstimer2 = 0
			self.ThrId[2] = 1
			self.ThreadActinity = 1
			self.Timer23 = threading.Thread(target = self.MyTimer2, args=(mstimer2,mutex))
			self.Timer23.start()

	def MyTimer2(self, mstimer2,mutex):
		while(self.starter[2] ==1):
			mstimer2 +=1
			mtimer2 =  int(mstimer2/600)
			stimer2 = int(mstimer2 - mtimer2*600)/10
			htimer2 = int(mstimer2 - mtimer2*600 - stimer2*10)
			timing2 = '%02d:%02d:%02s' % (mtimer2, stimer2, htimer2)
			time.sleep(0.088)
			wx.GetApp().Yield(True)
			self.TimerLabel2(timing2,mutex)

	def TimerLabel2(self, timing2, mutex):
		with mutex:
			self.Timer3.SetLabel(timing2)
		time.sleep(0.01)
	#________________________________________________________________________________
	def StartThread3(self,mutex):
		if self.starter[3] == 1:
			mstimer3 = 0
			self.ThrId[3] = 1
			self.ThreadActinity = 1
			self.Timer24 = threading.Thread(target = self.MyTimer3, args=(mstimer3,mutex))
			self.Timer24.start()

	def MyTimer3(self, mstimer3,mutex):
		while(self.starter[3] ==1):
			mstimer3 +=1
			mtimer3 =  int(mstimer3/600)
			stimer3 = int(mstimer3 - mtimer3*600)/10
			htimer3 = int(mstimer3 - mtimer3*600 - stimer3*10)
			timing3 = '%02d:%02d:%02s' % (mtimer3, stimer3, htimer3)
			time.sleep(0.088)
			wx.GetApp().Yield(True)
			self.TimerLabel3(timing3,mutex)

	def TimerLabel3(self, timing3, mutex):
		with mutex:
			self.Timer4.SetLabel(timing3)
		time.sleep(0.01)
	#________________________________________________________________________________
	def StartThread4(self,mutex):
		if self.starter[4] == 1:
			mstimer4 = 0
			self.ThrId[4] = 1
			self.ThreadActinity = 1
			self.Timer25 = threading.Thread(target = self.MyTimer4, args=(mstimer4,mutex))
			self.Timer25.start()

	def MyTimer4(self, mstimer4,mutex):
		while(self.starter[4] ==1):
			mstimer4 +=1
			mtimer4 =  int(mstimer4/600)
			stimer4 = int(mstimer4 - mtimer4*600)/10
			htimer4 = int(mstimer4 - mtimer4*600 - stimer4*10)
			timing4 = '%02d:%02d:%02s' % (mtimer4, stimer4, htimer4)
			time.sleep(0.088)
			wx.GetApp().Yield(True)
			self.TimerLabel4(timing4,mutex)

	def TimerLabel4(self, timing4, mutex):
		with mutex:
			self.Timer5.SetLabel(timing4)
		time.sleep(0.01)
	#######################################MY TIMER##########################################

	def Stop1(self, event):
		self.starter[0] = 0
		self.ThrId1[0] = 0
	def Stop2(self, event):
		self.starter[1] = 0
		self.ThrId1[1] = 0
	def Stop3(self, event):
		self.starter[2] = 0
		self.ThrId1[2] = 0
	def Stop4(self, event):
		self.starter[3] = 0
		self.ThrId1[3] = 0
	def Stop5(self, event):
		self.starter[4] = 0
		self.ThrId1[4] = 0

			#####################################StopWatch ends
	def Away(self, event):
		card.key_b("0", "0", "1", 1, 0.1);
	def Home(self, event):
		card.key_b("0", "0", "10", 1, 0.1);
	def Disarm(self, event):
		card.key_b("0", "0", "100", 1, 0.1);
	def Auxb(self, event):
		card.key_b("0", "0", "1000", 1, 0.1);
	def Enroll(self, event):
		card.key_b("0", "0", "1000", 6, 0.1);
	def Panicf(self, event):
		card.key_b("0", "0", "11", 2, 0.1);


	def NextPanelBut (self, event):
		navigator.send_key_fast('next')
	def PrewPanelBut (self, event):
		navigator.send_key_fast('back')
	def OKPanelBut (self, event):
		navigator.send_key_fast('ok')
	def LogToInst (self, event):
		navigator.login('9999')
	def LogToUser(self, event):
		navigator.loginToUserSettings('1111')
	def Awayp (self, event):
		navigator.send_key_fast('away')
	def Homep (self, event):
		navigator.send_key_fast('home')
	def Disarmp (self, event):
		navigator.send_key_fast('off')


	def Enroll1 (self, event):
		card.key_b("0", "10000", "0", 4, 1)
	def Enroll2 (self, event):
		card.key_b("0", "1", "0", 4, 1)
	def Enroll3 (self, event):
		card.key_b("10000", "0", "0", 4, 1)
	def Enroll4 (self, event):
		card.key_b("1", "0", "0", 4, 1)
	def Enroll5 (self, event):
		card.key_b("0", "0", "10000", 4, 1)

	def Start1 (self, event):
		if self.oc1==0:
			card.relaykey(16384, "close",0.1)
			self.statusbar.SetStatusText('Zone #1 is Closed', 0)
			self.Open1.SetLabel('Open')
			self.oc1=1
		else:
			if self.ThrId1[0] == 0:
				self.starter[0] = 1
				self.StartThread(self.mutex)
			card.relaykey(16384, "open",0.1)
			self.statusbar.SetStatusText('Zone #1 is --OPENED--', 0)
			self.statusbar.SetForegroundColour (wx.Colour (255, 255, 0))
			self.Open1.SetLabel('Close')
			self.oc1=0
			self.ThrId1[0] = 1


	def Start2 (self, event):
		if self.oc2==0:
			card.relaykey(1024, "close",0.1)
			self.statusbar.SetStatusText('Zone #2 is Closed', 1)
			self.Open2.SetLabel('Open')
			self.oc2=1
		else:
			if self.ThrId1[1] == 0:
				self.starter[1] = 1
				self.StartThread1(self.mutex)
			card.relaykey(1024, "open",0.1)
			self.statusbar.SetStatusText('Zone #2 is --OPENED--', 1)
			self.Open2.SetLabel('Close')
			self.oc2=0
			self.ThrId1[1] = 1
	def Start3 (self, event):
		if self.oc3==0:
			card.relaykey(64, "close",0.1)
			self.statusbar.SetStatusText('Zone #3 is Closed', 2)
			self.Open3.SetLabel('Open')
			self.oc3=1
		else:
			if self.ThrId1[2] == 0:
				self.starter[2] = 1
				self.StartThread2(self.mutex)
			card.relaykey(64, "open",0.1)
			self.statusbar.SetStatusText('Zone #3 is --OPENED--', 2)
			self.Open3.SetLabel('Close')
			self.oc3=0
			self.ThrId1[2] = 1
	def Start4 (self, event):
		if self.oc4==0:
			card.relaykey(4, "close",0.1)
			self.statusbar.SetStatusText('Zone #4 is Closed', 3)
			self.Open4.SetLabel('Open')
			self.oc4=1
		else:
			if self.ThrId1[3] == 0:
				self.starter[3] = 1
				self.StartThread3(self.mutex)
			card.relaykey(4, "open",0.1)
			self.statusbar.SetStatusText('Zone #4 is --OPENED--', 3)
			self.Open4.SetLabel('Close')
			self.oc4=0
			self.ThrId1[3] = 1
	def Start5 (self, event):
		if self.oc5==0:
			card.relaykey_b32("0","0","1000000","0","close", 0.1)
			self.statusbar.SetStatusText('Zone #5 is Closed', 4)
			self.Open5.SetLabel('Open')
			self.oc5=1
		else:
			if self.ThrId1[4] == 0:
				self.starter[4] = 1
				self.StartThread4(self.mutex)
			card.relaykey_b32("0","0","1000000","0","open", 0.1)
			self.statusbar.SetStatusText('Zone #5 is --OPENED--', 4)
			self.Open5.SetLabel('Close')
			self.oc5=0
			self.ThrId1[4] = 1
			
	def TampOpen1 (self, event):
		if self.k1==0:
			card.relaykey(8192, "close", 0.1)
			self.OpenTamper1.SetLabel('Open Tamper')
			self.OpenTamper1.SetForegroundColour (wx.Colour (0, 0, 0))
			self.k1=1
		else:
			card.relaykey(8192, "open", 0.1)
			self.OpenTamper1.SetLabel('Close Tamper')
			self.OpenTamper1.SetForegroundColour (wx.Colour (255, 0, 0))
			self.k1=0

	def TampOpen2 (self, event):
		if self.k2==0:
			card.relaykey(512, "close", 0.1)
			self.OpenTamper2.SetLabel('Open Tamper')
			self.OpenTamper2.SetForegroundColour (wx.Colour (0, 0, 0))
			self.k2=1
		else:
			card.relaykey(512, "open", 0.1)
			self.OpenTamper2.SetLabel('Close Tamper')
			self.OpenTamper2.SetForegroundColour (wx.Colour (255, 0, 0))
			self.k2=0

	def TampOpen3 (self, event):
		if self.k3==0:
			card.relaykey(32, "close", 0.1)
			self.OpenTamper3.SetLabel('Open Tamper')
			self.OpenTamper3.SetForegroundColour (wx.Colour (0, 0, 0))
			self.k3=1
		else:
			card.relaykey(32, "open", 0.1)
			self.OpenTamper3.SetLabel('Close Tamper')
			self.OpenTamper3.SetForegroundColour (wx.Colour (255, 0, 0))
			self.k3=0

	def TampOpen4 (self, event):
		if self.k4==0:
			card.relaykey(2, "close", 0.1)
			self.OpenTamper4.SetLabel('Open Tamper')
			self.OpenTamper4.SetForegroundColour (wx.Colour (0, 0, 0))
			self.k4=1
		else:
			card.relaykey(2, "open", 0.1)
			self.OpenTamper4.SetLabel('Close Tamper')
			self.OpenTamper4.SetForegroundColour (wx.Colour (255, 0, 0))
			self.k4=0

	def TampOpen5 (self, event):
		if self.k5==0:
			card.relaykey_b32("0","0","100000","0","close",0.1)
			self.OpenTamper5.SetLabel('Open Tamper')
			self.OpenTamper5.SetForegroundColour (wx.Colour (0, 0, 0))
			self.k5=1
		else:
			card.relaykey_b32("0","0","100000","0","open",0.1)
			self.OpenTamper5.SetLabel('Close Tamper')
			self.OpenTamper5.SetForegroundColour (wx.Colour (255, 0, 0))
			self.k5=0

	
		
			
	def ExitDialog(self, event):
		dial = wx.MessageDialog(None, 'Are you sure want to quit?', 'Programm will be closed', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		OK = int(dial.ShowModal())
		if OK == 5103:
			#startedat = time.time()
			#print 'Ok button was pressed'
			if self.ThreadActinity == 0:
				#time.sleep(0.7)
				card.relaykey_b32("11111111","11111111","11111111","11111111","close",0.1)
				self.Close()
			else:
				if self.ThrId[0] == 1:
					self.Timer21._Thread__stop()
					time.sleep(0.7)
					
				if self.ThrId[1] == 1:
					self.Timer22._Thread__stop()
					time.sleep(0.7)
					
			#print (time.time() - startedat)
			card.relaykey_b32("11111111","11111111","11111111","11111111","close",0.1)
			self.Close()
		else:
			#print 'Cancel button was pressed'
			dial.Destroy()

	def btn1(self, event):
		navigator.send_key_fast('1')
	def btn2(self, event):
		navigator.send_key_fast('2')
	def btn3(self, event):
		navigator.send_key_fast('3')
	def btn4(self, event):
		navigator.send_key_fast('4')
	def btn5(self, event):
		navigator.send_key_fast('5')
	def btn6(self, event):
		navigator.send_key_fast('6')
	def btn7(self, event):
		navigator.send_key_fast('7')
	def btn8(self, event):
		navigator.send_key_fast('8')
	def btn9(self, event):
		navigator.send_key_fast('9')
	def btn0(self, event):
		navigator.send_key_fast('0')
	def btnlog(self, event):
		navigator.send_key_fast('*')
	def btnds(self, event):
		navigator.send_key_fast('#')
	def btnemerg(self, event):
		navigator.send_key_fast('emergency')
	def btnpanic(self, event):
		navigator.send_key_fast('panic')
	def btnfire(self, event):
		navigator.send_key_fast('fire')


app = wx.App(False)
frame = PowerMaster(None, -1, 'Power Master Testing Tool')
app.MainLoop()


