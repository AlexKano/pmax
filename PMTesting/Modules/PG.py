#!/usr/bin/python
# -*- coding: utf-8 -*-

# working with panel by command line (by YuriyR)

import sys, os
import time
import logging
import com

SEPARATOR = "\\"
if (os.name == "posix"):
    SEPARATOR = "/"

cmd_folder = os.path.dirname(os.path.abspath(__file__))

sys.path.append( cmd_folder + SEPARATOR + 'PowerMaster' )
import serial_port_craft

import devices_forPG

def output_enroll_result(iResult):
    try:
	CurrDir = cmd_folder
        f = open(CurrDir + SEPARATOR + "enroll","w")
        f.write("%d" % iResult)
        f.close()
    except:
        logging.info( 'Failed to store enroll result to "enroll" file')

        
def HandlingCommand(dev):

    if (sys.argv[1] == 'enroll') or (sys.argv[1] == 'save'):
        #For 'save' operation changing ShortID and LongID for correct order
        if (sys.argv[1] == 'save'):
            sShortID = sys.argv[3]
            sys.argv[3] = sys.argv[4]

        dev = None
        if   sys.argv[2]  == 'contact':      dev = devices_forPG.restorable_device(sys.argv[3], devices_forPG.device_type.contact)
        elif (sys.argv[2] == 'new_contact') or (sys.argv[2] == 'contact_aux'):
            dev = devices_forPG.restorable_device(sys.argv[3], devices_forPG.device_type.contact_aux)
        elif sys.argv[2] == 'motion':        dev = devices_forPG.violated_device  (sys.argv[3], devices_forPG.device_type.motion_sensor)
        elif sys.argv[2] == 'motion_cam':    dev = devices_forPG.violated_device  (sys.argv[3], devices_forPG.device_type.motion_camera)
        elif sys.argv[2] == 'smoke':         dev = devices_forPG.restorable_device(sys.argv[3], devices_forPG.device_type.smoke)
        elif sys.argv[2] == 'smoke_heat':    dev = devices_forPG.restorable_device(sys.argv[3], devices_forPG.device_type.smoke_heat)
        elif sys.argv[2] == 'gas':           dev = devices_forPG.gas_device  (sys.argv[3], devices_forPG.device_type.gas)
        elif sys.argv[2] == 'co':            dev = devices_forPG.device_co   (sys.argv[3], devices_forPG.device_type.co)
        elif sys.argv[2] == 'glass_break':   dev = devices_forPG.glass_break_device(sys.argv[3], devices_forPG.device_type.glass_break)
        elif sys.argv[2] == 'clip':          dev = devices_forPG.violated_device(sys.argv[3], devices_forPG.device_type.clip)
        elif sys.argv[2] == 'flood':         dev = devices_forPG.flood_device(sys.argv[3], devices_forPG.device_type.flood)
        elif sys.argv[2] == 'shock':
            dev = devices_forPG.restorable_device(sys.argv[3], devices_forPG.device_type.shock)
        elif sys.argv[2] == 'shock_aux':
            dev = devices_forPG.restorable_device(sys.argv[3], devices_forPG.device_type.shock_aux)
        elif sys.argv[2] == 'shock_contact':
            dev = devices_forPG.restorable_device(sys.argv[3], devices_forPG.device_type.shock_contact)
        elif sys.argv[2] == 'shock_aux_contact':
            dev = devices_forPG.restorable_device(sys.argv[3], devices_forPG.device_type.shock_aux_contact)

	   # keyfobs
        elif sys.argv[2] == 'keyfob':        dev = devices_forPG.keyfob(sys.argv[3], devices_forPG.device_type.keyfob)
        elif sys.argv[2] == 'keyfob_235':    dev = devices_forPG.keyfob(sys.argv[3], devices_forPG.device_type.keyfob_235)
        elif sys.argv[2] == 'keyfob_lcd':    dev = devices_forPG.keyfob(sys.argv[3], devices_forPG.device_type.keyfob_lcd) # now don't work (panel K15.008)
        # keypads
        elif (sys.argv[2] == 'kp140'):       dev = devices_forPG.big_keypad(sys.argv[3], devices_forPG.device_type.keypad_big)   # "keypad"
        elif (sys.argv[2] == 'kp141'):       dev = devices_forPG.big_keypad(sys.argv[3], devices_forPG.device_type.keypad_small) # "keypad_small"
        elif (sys.argv[2] == 'kp160'):       dev = devices_forPG.big_keypad(sys.argv[3], devices_forPG.device_type.arming_station) # "arming_station"
        elif (sys.argv[2] == 'kp250'):       dev = devices_forPG.big_keypad(sys.argv[3], devices_forPG.device_type.keypad_250)   # full functionality

        elif sys.argv[2] == 'siren_out':     dev = devices_forPG.device  (sys.argv[3], devices_forPG.device_type.outdoor_siren)
        elif sys.argv[2] == 'siren_in':      dev = devices_forPG.device  (sys.argv[3], devices_forPG.device_type.indoor_siren)
        elif sys.argv[2] == 'repeater':      dev = devices_forPG.repeater(sys.argv[3])
        elif sys.argv[2] == 'repeater':      dev = devices_forPG.repeater(sys.argv[3])
        elif sys.argv[2] == 'wired_zone':    dev = devices_forPG.device  (sys.argv[3], devices_forPG.device_type.wired_zone)
        elif sys.argv[2] == 'temperature':   dev = devices_forPG.temperature_device(sys.argv[3], devices_forPG.device_type.temperature)
        elif sys.argv[2] == 'tower30':       dev = devices_forPG.tower_device(sys.argv[3], devices_forPG.device_type.tower30)
        elif sys.argv[2] == 'tower32':       dev = devices_forPG.tower_device(sys.argv[3], devices_forPG.device_type.tower32)
        elif sys.argv[2] == 'tower20':       dev = devices_forPG.tower_device(sys.argv[3], devices_forPG.device_type.tower20)

        if dev == None:
            print 'unknown device type'

            f = open(devices_forPG.CurrDir + SEPARATOR + 'ShortID.txt', "w", 0)
            f.write( '{0},{1},{2}'.format( str(-1), str(-1), str(-1) ) )
            f.close()

            # set stop event and wait finish work thread
            com_thr.stop_event.set()
            com_thr.join()

            sys.exit(0)

        if sys.argv[1] != 'save':
            dev.SerPort = com_thr
            #print dev.SerPort
            IsSerPort = 1

            for i in range(4):
                dev.short_id = -1
                dev.DevType = ''
                dev.DevNum = -1
                logging.info( 'enroll beg {0} {1} {2} -- Loop: {3}'.format(sys.argv[3], dev.short_id, sys.argv[2], i) )
                try:
                    if len(sys.argv) > 4: #Enrolling with Customer ID, if specified
                        dev.enroll(int(sys.argv[4]), int(sys.argv[5]))
                    else:
                        dev.enroll()
                        #pass
                except:
                    print 'Except: {0}'.format('exception')
                    logging.info( 'Except: {0}'.format('exception') )

                #output_enroll_result(dev.short_id >= 0);
                logging.info( 'enroll end {0} {1} {2}'.format(sys.argv[3], dev.short_id, sys.argv[2]) )
                if dev.short_id != -1: break # success
                else: print 'Attempt #{0}. Device has not enrolled.'.format( i )

        #time.sleep(2)

            f = open(devices_forPG.CurrDir + SEPARATOR + 'ShortID.txt', "w", 0)
            f.write( '{0},{1},{2}'.format( str(dev.short_id), str(dev.DevType), str(dev.DevNum) ) )
            f.close()
            if dev.short_id != -1: dev.update()

        if sys.argv[1] == 'save': dev.short_id = int(sShortID)

        #CurrDir2 = '\\'.join(["%s" % s1 for s1 in devices_forPG.CurrDir.split('\\')[:-1] ])
        #print CurrDir2

        if (sys.argv[1] != 'save'):
            #print dev.SerPort
            del dev.SerPort
            dev.SerPort = None
            #IsSerPort = 0
        if dev.short_id != -1: devices_forPG.save(dev)
    elif sys.argv[1] == 'update':
        dev.update()
    elif sys.argv[1] == 'open':
        dev.open(1)
    elif sys.argv[1] == 'close':
        dev.open(0)
    elif sys.argv[1] == 'open_smoke_alarm':
        dev.smoke_alarm(1)
    elif sys.argv[1] == 'close_smoke_alarm':
        dev.smoke_alarm(0)
    elif (sys.argv[1] == 'open_smoke') or (sys.argv[1] == 'open_smoke_trouble'):
        dev.smoke_trouble(1)
    elif (sys.argv[1] == 'close_smoke') or (sys.argv[1] == 'close_smoke_trouble'):
        dev.smoke_trouble(0)

    elif sys.argv[1] == 'open_aux': # unfinished
        print 'Command: "' + sys.argv[1] + '" not implemented yet'
        #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'open_aux. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
        #dev.open_aux(1)

    elif sys.argv[1] == 'close_aux': # unfinished
        print 'Command: "' + sys.argv[1] + '" not implemented yet'
        #dev = devices.restorable_device(sys.argv[3], None)
        #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'close_aux. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
        #dev.open_aux(0)

    elif sys.argv[1] == 'open_heat_alarm':
        #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'open_heat_alarm. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
        dev.heat_alarm(1)

    elif sys.argv[1] == 'close_heat_alarm':
        #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'close_heat_alarm. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
        dev.heat_alarm(0)

    elif (sys.argv[1] == 'open_heat') or (sys.argv[1] == 'open_heat_trouble'):
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'open_heat_trouble. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.heat_trouble(1)

    elif (sys.argv[1] == 'close_heat') or (sys.argv[1] == 'close_heat_trouble'):
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'close_heat_trouble. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.heat_trouble(0)

    elif sys.argv[1] == 'open_supervision':
        #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'open_supervision. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
        dev.supervision(1)

    elif sys.argv[1] == 'close_supervision':
        #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'close_supervision. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
        dev.supervision(0)

    elif sys.argv[1] == 'clean_me':
        #dev = devices.restorable_device(sys.argv[3], None)
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'clean_me. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
        dev.clean_me()

    elif sys.argv[1] == 'violate': # not close ???
        #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'violate. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
        dev.violate()

    elif sys.argv[1] == 'glass_break': # not close ???
        #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'glass_break. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
        dev.glass_break()

    elif sys.argv[1] == 'open_masking':
        #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'open_masking. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
        dev.masking(1)

    elif sys.argv[1] == 'close_masking':
        #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'close_masking. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
        dev.masking(0)

    elif sys.argv[1] == 'open_co_alert':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'open_co_alert. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.alert(1)

    elif sys.argv[1] == 'close_co_alert':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'close_co_alert. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.alert(0)

    elif sys.argv[1] == 'open_co_trouble':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'open_co_trouble. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.trouble(1)

    elif sys.argv[1] == 'close_co_trouble':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'close_co_trouble. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.trouble(0)

    elif sys.argv[1] == 'open_gas_alert':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'open_gas_alert. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.gas_alert(1)
        
    elif sys.argv[1] == 'close_gas_alert':
       #dev = devices.load(int(sys.argv[2]))
        #logging.info( 'close_gas_alert. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.gas_alert(0)

    elif sys.argv[1] == 'open_gas_trouble':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'open_gas_trouble. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.gas_trouble(1)
        
    elif sys.argv[1] == 'close_gas_trouble':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'close_gas_trouble. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.gas_trouble(0)

   ##elif sys.argv[1] == 'open_inactive':
    ##    dev = devices.restorable_device(sys.argv[3], None)
    ##    dev.short_id = int(sys.argv[2])
    ##    logging.info( 'open_inactive. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
    ##    dev.inactive(1)
    ##
    ##elif sys.argv[1] == 'close_inactive':
    ##    dev = devices.restorable_device(sys.argv[3], None)
    ##    dev.short_id = int(sys.argv[2])
    ##    logging.info( 'close_inactive. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
    ##    dev.inactive(0)

   #============================================  # Flood events

    elif sys.argv[1] == 'open_flood':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'open_flood. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.flood(1)

    elif sys.argv[1] == 'close_flood':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'close_flood. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.flood(0)

   #============================================  # Temperature events

    elif sys.argv[1] == 'open_freezer':
       dev.freezer(1)
    elif sys.argv[1] == 'close_freezer':
       dev.freezer(0)
    elif sys.argv[1] == 'open_freezing':
       dev.freezing(1)
    elif sys.argv[1] == 'close_freezing':
       dev.freezing(0)

    elif sys.argv[1] == 'open_cold':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'open_cold. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.cold(1)

    elif sys.argv[1] == 'close_cold':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'close_cold. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.cold(0)

    elif sys.argv[1] == 'open_hot':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'open_hot. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.hot(1)

    elif sys.argv[1] == 'close_hot':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'close_hot. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.hot(0)

    elif sys.argv[1] == 'open_freezer_trouble':
        #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'open_freezer_trouble. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
        dev.freezer_trouble(1)

    elif sys.argv[1] == 'close_freezer_trouble':
        #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'close_freezer_trouble. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
        dev.freezer_trouble(0)

    elif sys.argv[1] == 'open_probe':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'open_probe. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.probe(1)

    elif sys.argv[1] == 'close_probe':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'close_probe. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.probe(0)

    elif sys.argv[1] == 'set_temperature':
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'set_temperature. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.set_temperature(iTemperature)
        
   #============================================  # General events

    elif sys.argv[1] == 'open_tamper':
        dev.tamper(1)
    elif sys.argv[1] == 'close_tamper':
        dev.tamper(0)

    elif (sys.argv[1] == 'low_bat') or (sys.argv[1] == 'open_low_bat'): # work for keyfob
        dev.lowbattery(1)
    elif (sys.argv[1] == 'rest_bat') or (sys.argv[1] == 'close_low_bat'): # work for keyfob
        dev.lowbattery(0)

    elif (sys.argv[1] == 'ac_fail'): # work for motion_cam
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'ac_fail. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.ac_fail(1)

    elif (sys.argv[1] == 'ac_rest'): # work for motion_cam
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'ac_rest. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.ac_fail(0)

    # ******************************************

    elif sys.argv[1] == 'arm_away': # work for keyfob and keypad
        if (dev.__class__ == devices_forPG.big_keypad) or (dev.__class__ == devices_forPG.arming_station):
            dev.set_user_code(sCode)
            dev.set_partitions2(Part)
        dev.arm_away()

    elif sys.argv[1] == 'arm_home': # work for keyfob and keypad
        if (dev.__class__ == devices_forPG.big_keypad) or (dev.__class__ == devices_forPG.arming_station):
            dev.set_user_code(sCode)
            dev.set_partitions2(Part)
        dev.arm_home()

    elif sys.argv[1] == 'disarm': # work for keyfob and keypad
        if (dev.__class__ == devices_forPG.big_keypad) or (dev.__class__ == devices_forPG.arming_station):
            dev.set_user_code(sCode)
            dev.set_partitions2(Part)
        dev.disarm()

    #All available actions
    elif (sys.argv[1] in arming_actions):
        if (dev.__class__ == devices_forPG.big_keypad) or (dev.__class__ == devices_forPG.arming_station):
            if (sys.argv[1] != "arm_quick") and (sys.argv[1] != "arm_home_quick"):
                dev.set_user_code(sCode)
            dev.set_partitions2(Part)
        dev.specific_action(sys.argv[1])
        
    elif sys.argv[1] == 'panic': # work for keyfob and keypad
        dev.panic()
    elif sys.argv[1] == 'fire': # work for keypad and zone
       dev.fire()
    elif sys.argv[1] == 'emergency': # work for keypad
        dev.emergency()
    elif sys.argv[1] == 'aux_button': # work for keypad
        dev.aux_button()

    elif sys.argv[1] == 'hello': # work for keypad
       #dev = devices.load(int(sys.argv[2]))
        #dev.short_id = int(sys.argv[2])
        #logging.info( 'hello. {0} {1}'.format(sys.argv[3], sys.argv[2]) )
       dev.hello()

    elif (sys.argv[1] == 'jamming_open') or (sys.argv[1] == 'open_jamming'):
       dev.jamming(1)
    elif (sys.argv[1] == 'jamming_close') or (sys.argv[1] == 'close_jamming'):
       dev.jamming(0)

    #============================================
    #Proximity tag events
    #============================================

    elif (sys.argv[1].lower().find("tag") >= 0):
        tag_action_str = ""
        if (sys.argv[1].lower().find("enroll") == 0):
            tag_action_str = "away"
        elif (sys.argv[1].lower().find("tag") == 0):
            tag_action_str = sys.argv[1][4:] #4 = len("tag_")
        else:
            print "Incorrect action for tag was specified"
            sys.exit(0)

        dev.set_partitions2(Part)
        dev.tag_action( int(sTagNum), tag_action_str )


    #===========================================

    else:
        print 'Unknown Command. Read "PG_help.xls" file for commands list and descriptions.'



        
LOG_FILENAME = devices_forPG.CurrDir + SEPARATOR + 'LogPG.txt'
logging.basicConfig(level=logging.DEBUG,
#logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=LOG_FILENAME
                    #,filemode='w'
                   )
#logging.debug('This is a debug message')
#logging.info('This is an info message')
#logging.warning('This is a warning message')
#logging.error('This is an error message')
#logging.critical('This is a critical error message')

#sys.exit()

#Keypad code
sCode = "1111"
Part = [0]
#Checking if code was specified for arm operation
arming_actions = ['arm_away', 'arm_home', 'disarm', 'arm_latchkey', 'arm_partition', 'arm_quick', 'arm_home_quick', 'arm_instant']
tag_command = [ 'enroll_tag', 'tag_away', 'tag_home', 'tag_disarm', 'tag_away_latchkey', 'tag_arm_part', 'tag_quick_arm', 'tag_quick_home', 'tag_arm_instant', 'tag_check_code' ]

#if ((sys.argv[1] == 'arm_away') or (sys.argv[1] == 'arm_home') or (sys.argv[1] == 'disarm')) and (len(sys.argv) > 4):
if (sys.argv[1] in arming_actions) and (len(sys.argv) > 4):
    sCode = sys.argv[2]
    sys.argv[2] = sys.argv[3]
    sys.argv[3] = sys.argv[4]
    if (len(sys.argv) == 6):
        Part = sys.argv[5]

if (sys.argv[1] in tag_command) and (len(sys.argv) > 4):
    #print 'tag_'
    sTagNum = sys.argv[2]
    sys.argv[2] = sys.argv[3]
    sys.argv[3] = sys.argv[4]
    if (len(sys.argv) > 5):
        Part = sys.argv[5]

#Setting temperature
if (sys.argv[1] == 'set_temperature'):
    iTemperature = sys.argv[2]
    sys.argv[2] = sys.argv[3]
    sys.argv[3] = sys.argv[4]


dev_with_new_port = [
    'enroll', 'update', 'save', 'open_tamper', 'close_tamper'
    , 'low_bat', 'open_low_bat', 'rest_bat', 'close_low_bat'
    , 'ac_fail', 'ac_rest' , 'hello', 'fire'
    , 'open', 'close', 'violate', 'open_smoke_alarm', 'close_smoke_alarm'
    , 'open_smoke', 'open_smoke_trouble', 'close_smoke', 'close_smoke_trouble'
    , 'panic', 'emergency', 'aux_button', 'jamming_open', 'open_jamming', 'jamming_close', 'close_jamming'

    , 'open_heat_alarm', 'close_heat_alarm', 'open_heat', 'open_heat_trouble', 'close_heat', 'close_heat_trouble'
    , 'open_supervision', 'close_supervision', 'clean_me', 'glass_break', 'open_masking', 'close_masking'
    , 'open_co_alert', 'close_co_alert', 'open_co_trouble', 'close_co_trouble'
    , 'open_gas_alert', 'close_gas_alert', 'open_gas_trouble', 'close_gas_trouble'
    , 'open_flood', 'close_flood'
    , 'open_freezer', 'close_freezer', 'open_freezing', 'close_freezing'
    , 'open_cold', 'close_cold', 'open_hot', 'close_hot', 'open_freezer_trouble', 'close_freezer_trouble'
    , 'open_probe', 'close_probe', 'set_temperature'
    ]
#dev_with_new_port.update( tag_command )
#dev_with_new_port.update( arming_actions )
dev_with_new_port.extend( tag_command )
dev_with_new_port.extend( arming_actions )


if sys.argv[1] not in dev_with_new_port:
    print 'open old port'
    devices_forPG.ser_old = devices_forPG.ser()
    devices_forPG.ser_old.ser()
    devices_forPG.s = devices_forPG.ser_old.ser

dev = None
#dev.SerPort = None
com_thr = None
params = ['']
Cmd = None
IsSerPort = 0
IsErrorIn_PG_py = 0

if sys.argv[1] in dev_with_new_port:
    if (sys.argv[1] != 'save'):
        print 'open new port'

        '''# Get params from "cmd_for_python.txt"
        try:
            fCmd = open(devices_forPG.CurrDir + SEPARATOR + 'cmd_for_python.txt', "r", 0) # Win
            StrCmd = fCmd.readline()
            fCmd.close()
            StrCmd2 = StrCmd[:len(StrCmd)].strip()
            params = StrCmd2.split(",")
        except IOError as (errno, strerror):
            print "\nI/O exception({0}): {1}. File cmd_for_python.txt".format(errno, strerror)
'''
        if (sys.argv[1] != 'enroll'):
            #dev = devices_forPG.restorable_device(sys.argv[3], None)
            dev = devices_forPG.load(int(sys.argv[2]))
            dev.short_id = int(sys.argv[2])
            if (params[0].strip() == 'IsNotSerialPort'): dev.SerPort = None
            #print dev

        if (params[0].strip() != 'IsNotSerialPort'):
            #f2 = open(devices_forPG.CurrDir + SEPARATOR + 'com.txt', "r", 0) # Win
            strCom = com.ComPanel()
	    print strCom 
            #f2.close()

            com_thr = serial_port_craft.COM_thr()
            com_thr.open_serial_port(strCom, 9600, 'PortAuto')
            ####com_thr.start()
            if (sys.argv[1] != 'enroll') and (sys.argv[1] != 'save'):
                dev.SerPort = com_thr
                #print dev.SerPort
                IsSerPort = 1
	'''
        if (params[0].strip() == 'wait'):
            # clear file for result
            f = open(devices_forPG.CurrDir + SEPARATOR + 'res_from_python.txt', "w", 0)
            f.write( '' )
            f.close()

            Cmd = serial_port_craft.packet( int(params[1].strip()) )
            if (params[1].strip() == '1'):
                Cmd.LCD = int(params[2].strip())
                com_thr.wait(Cmd, 'Start')
            elif (params[1].strip() == '3'):
                Cmd.BzrNum = int(params[2].strip())
                com_thr.wait(Cmd, 'Start')
            elif (params[1].strip() == '6'):
                Cmd.EvNum = int(params[2].strip())
                Cmd.SourceNum = int(params[4].strip())
                com_thr.wait(Cmd, 'Start')
            else:
                print 'unknown wait command'

        try:
            logging.info( '{0}. {1} {2}'.format( sys.argv[1], sys.argv[3], sys.argv[2] ) )
        except:
            IsErrorIn_PG_py = 1
            sys.stdout.write( "(PG.py) Unexpected error: {0}\n".format( sys.exc_info()[0] ) )
            sys.stdout.flush()
            logging.info( "(PG.py) Unexpected error: {0}".format( sys.exc_info()[0] ) )
            if (IsSerPort == 1):
                # set stop event and wait finish work thread
                com_thr.stop_event.set()
                com_thr.join()
            sys.exit(0)
	'''
HandlingCommand(dev)


if sys.argv[1] in dev_with_new_port:

    if (params[0].strip() == 'wait'):
        ResBzr = com_thr.wait( Cmd, 'Check', float(params[3].strip()) )
        f = open(devices_forPG.CurrDir + SEPARATOR + 'res_from_python.txt', "w", 0)
        if ResBzr == True: f.write( '1' )
        if ResBzr == False: f.write( '0' )
        f.close()
        # clear file for command # better do it in coronys?
        #f = open(devices_forPG.CurrDir+'\\cmd_for_python.txt', "w", 0)
        #f.write( '' )
        #f.close()

    if (sys.argv[1] != 'save'):

        #if (IsSerPort == 1):
        if (com_thr != None):
            # set stop event and wait finish work thread
            com_thr.stop_event.set()
            com_thr.join()

        if (sys.argv[1] != 'enroll'):
            if (dev.SerPort != None):
                #print dev.SerPort
                del dev.SerPort

if (IsErrorIn_PG_py == 1):
    f = open(devices_forPG.CurrDir + SEPARATOR + 'ShortID.txt', "w", 0)
    f.write( '{0},{1},{2}'.format( str(-1), str(-1), str(-1) ) )
    f.close()

sys.exit(0)
