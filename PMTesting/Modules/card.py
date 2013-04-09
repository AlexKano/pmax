#!/usr/bin/env python
#Description:

#FUNCTION   dec_relay(<relay1_16>,<state>, <num_card>)
#<relay1_16> - dec numbers of relays that needs to change state (e.g. if <relay1_16> = 5 then first and third relays(00000101) are changed state )
#<state> - 01-open NC(normal close) relay; 02-close NC(normal close) relay 
#<num_card> - 01-first relay card; 02 - the second relay card' ..... 

#FUNCTION bin_relay(<relay_1_8>,<relay_9_16>,<state>, <num_card>)
#<relay1_8> - relays(1-8) that needs to change state (e.g. if <relay1_8> = 00000101 then first and third relays are changed state )
#<relay9_16> - relays(9-16) that needs to change state (e.g. if <relay9_9> = 00000101 then 9 and 11 relays are changed state )
#<state> - 01-open NC(normal close) relay; 02-close NC(normal close) relay 
#<num_card> - 01-first relay card; 02 - the second relay card' ..... 

#FUNCTION relaykey_b32(<relay_1_8>,<relay_9_16>,<relay_17_24>,<relay_25_32>,<state>,<TIME_after_release_key>)
#<relay1_8> - relays(1-8) that needs to change state (e.g. if <relay1_8> = 00000101 then first and third relays are changed state )
#<relay9_16> - relays(9-16) that needs to change state (e.g. if <relay9_9> = 00000101 then 9 and 11 relays are changed state )
#<relay17_24> - see above description
#<relay25_32> - see above description
#<state> - 01-open NC(normal close) relay; 02-close NC(normal close) relay 
#<TIME_after_release_key> - TIME after chsnging state (by default = 0.5) 

#FUNCTION key_b32(<relay_1_8>,<relay_9_16>,<relay_17_24>,<relay_25_32>,<TIME_between_press_release_key>,<TIME_after_release_key>)
#<relay1_8> - relays(1-8) that needs to change state (e.g. if <relay1_8> = 00000101 then first and third relays are changed state )
#<relay9_16> - relays(9-16) that needs to change state (e.g. if <relay9_9> = 00000101 then 9 and 11 relays are changed state )
#<relay17_24> - see above description
#<relay25_32> - see above description
#<TIME_between_press_release_key> - TIME beetwen chsnging state (by default = 0.5) 
#<TIME_after_release_key> - TIME after chsnging state (by default = 0.5) 




import serial
import out
import time
import com
TIME_between_press_release_key = 0.5
TIME_after_release_key = 0.5
TIME_between_card1_card2 = 0.1
def dec_to_bin(x):
	n1 = "0000000000000000000000000"
	n = ""
	if x==0:
		return n1 
	while x> 0:
		y = str(x % 2)
		n = y +n 
		x = int (x/2)
	return n1+n
def bin_to_hex(binstr):
	dec = int(binstr,2)
	hex1 = hex(dec)
	hex1 = hex1[2:4]
	if len (hex1)<2:
		hex1 = "0"+hex1
	return hex1
		
		
def dec_to_2hex(dec): 
	sbin =  dec_to_bin(dec)
	lens = len(sbin)
	bit38 = sbin[lens-24:lens-16]
	bit28 = sbin[lens-16:lens-8]
	bit18 = sbin[lens-8:lens]
	dec_bit28 = int(bit28,2)
	dec_bit18 = int(bit18,2)
	dec_bit38 = int(bit38,2)
	
	hex_bit28 = hex(dec_bit28)
	hex_bit18 = hex(dec_bit18)
	hex_bit38 = hex(dec_bit38)
	
	hex_bit28 = hex_bit28[2:4]
	hex_bit18 = hex_bit18[2:4]
	hex_bit38 = hex_bit38[2:4]
	
	if len (hex_bit28)<2:
		hex_bit28 = "0"+hex_bit28
	if len (hex_bit18)<2:
		hex_bit18 = "0"+hex_bit18
	if len (hex_bit38)<2:
		hex_bit38 = "0"+hex_bit38
		
	return hex_bit18,hex_bit28,hex_bit38
	
ser = serial.Serial(com.ComRelayER16(),"9600")
def relay1(Num,state):
        s = '5508'+state+Num+'01000024'
	#print s
        for i in range(len(s)/2):
                c = chr(int(s[i*2:i*2+2],16))
                ser.write(c)

	return 1
	
def relay(hex1_8,hex9_16,state,num_card):
	s = '5508'+state+hex9_16+hex1_8+num_card+'000024'
	#print s
        for i in range(len(s)/2):
                c = chr(int(s[i*2:i*2+2],16))
                ser.write(c)
	return 1

def dec_relay(relay1_16,state, num_card ="01"):
	relay1_8,relay9_16 = dec_to_2hex(relay1_16)
        s = '5508'+state+relay9_16+relay1_8+num_card+'000024'
	#print s
        for i in range(len(s)/2):
                c = chr(int(s[i*2:i*2+2],16))
                ser.write(c)

	return 1
def bin_relay(relay_1_8,relay_9_16,state, num_card ="01"):
	bin = relay_9_16 + relay_1_8
	dec = int(bin,2)
	print dec
	relay1_8,relay9_16,x = dec_to_2hex(dec)
        s = '5508'+state+relay9_16+relay1_8+num_card+'000024'
	#print s
        for i in range(len(s)/2):
                c = chr(int(s[i*2:i*2+2],16))
                ser.write(c)
	return 1
	
def relaykey(dec,state,time1=TIME_after_release_key):
	hex1_8,hex9_16,hex17_24 = dec_to_2hex(dec)
	hex24_32 = "00" 
	if state == "open":
		state1 = "01"
	if state == "close":
		state1 = "02"
	ts = 0
	if hex1_8 != "00" or hex9_16 != "00":	
		relay(hex1_8,hex9_16,state1,"01") #press 1 key on card 1
		ts = TIME_between_card1_card2
	if hex17_24 != "00":
		time.sleep(ts)
		relay(hex17_24,hex24_32,state1,"02") #press 1 key on card 2
	
	time.sleep(time1)
	#print ">> Pressing "+str(dec)+" key"
	
def relaykey_b(bit1_8,bit9_16,bit17_24,state,time1=TIME_after_release_key):
	hex1_8 = bin_to_hex(bit1_8)
	hex9_16 =bin_to_hex(bit9_16)
	hex17_24 = bin_to_hex(bit17_24)
	hex24_32 = "00" 
	if state == "open":
		state1 = "01"
	if state == "close":
		state1 = "02"
	ts = 0
	if hex1_8 != "00" or hex9_16 != "00":	
		relay(hex1_8,hex9_16,state1,"01") #press 1 key on card 1
		ts = TIME_between_card1_card2
	if hex17_24 != "00":
		time.sleep(ts)
		relay(hex17_24,hex24_32,state1,"02") #press 1 key on card 2
	
	time.sleep(time1)
	#print ">> Pressing "+bit17_24 +" "+bit9_16+" "+bit1_8+" key"
def relaykey_b32(bit1_8,bit9_16,bit17_24,bit25_32,state,time1=TIME_after_release_key):
	hex1_8 = bin_to_hex(bit1_8)
	hex9_16 =bin_to_hex(bit9_16)
	hex17_24 = bin_to_hex(bit17_24)
	hex24_32 = bin_to_hex(bit25_32)
	if state == "open":
		state1 = "01"
	if state == "close":
		state1 = "02"
	ts = 0
	if hex1_8 != "00" or hex9_16 != "00":	
		relay(hex1_8,hex9_16,state1,"01") #press 1 key on card 1
		ts = TIME_between_card1_card2
	if hex17_24 != "00"or hex24_32 != "00":
		time.sleep(ts)
		relay(hex17_24,hex24_32,state1,"02") #press 1 key on card 2
	
	time.sleep(time1)
	#print ">> Pressing "+bit17_24 +" "+bit9_16+" "+bit1_8+" key"

def key(dec,time1=TIME_between_press_release_key ,time2=TIME_after_release_key ):
	hex1_8,hex9_16,hex17_24 = dec_to_2hex(dec)
	hex24_32 = "00" 
	ts = 0
	if hex1_8 != "00" or hex9_16 != "00":
		relay(hex1_8,hex9_16,'01',"01") #press 1 key on card 1
		ts = TIME_between_card1_card2
	if hex17_24 != "00":
		time.sleep(ts)
		relay(hex17_24,hex24_32,'01',"02") #press 1 key on card 2
	ts = 0
	time.sleep(time1)
	#print ">> Pressing "+str(dec)+" key"
	if hex1_8 != "00" or hex9_16 != "00":
		relay(hex1_8,hex9_16,'02',"01") #release 1 key on card 1
		ts = TIME_between_card1_card2
	if hex17_24 != "00":
		time.sleep(ts)
		relay(hex17_24,hex24_32,'02',"02") #release 1 key on card 2
	time.sleep(time2)
	return 1
	
def key_b(bit1_8,bit9_16,bit17_24="0",time1=TIME_between_press_release_key ,time2=TIME_after_release_key):
	hex1_8 = bin_to_hex(bit1_8)
	hex9_16 = bin_to_hex(bit9_16)
	hex17_24 =  bin_to_hex(bit17_24)
	hex24_32 = "00" 
	ts = 0
	if hex1_8 != "00" or hex9_16 != "00":
		relay(hex1_8,hex9_16,'01',"01") #press 1 key on card 1
		ts = TIME_between_card1_card2
	if hex17_24 != "00":
		time.sleep(ts)
		relay(hex17_24,hex24_32,'01',"02") #press 1 key on card 2

	#print time1	
	time.sleep(time1)
	#print ">> Pressing "+bit17_24 +" "+bit9_16+" "+bit1_8+" key"
	ts = 0
	if hex1_8 != "00" or hex9_16 != "00":
		relay(hex1_8,hex9_16,'02',"01") #release 1 key on card 1
		ts = TIME_between_card1_card2
	if hex17_24 != "00":
		time.sleep(ts)
		relay(hex17_24,hex24_32,'02',"02") #release 1 key on card 2
	#print time2
	time.sleep(time2)
	return 1

def key_b32(bit1_8,bit9_16,bit17_24="0",bit25_32="0",time1=TIME_between_press_release_key ,time2=TIME_after_release_key):
	hex1_8 = bin_to_hex(bit1_8)
	hex9_16 = bin_to_hex(bit9_16)
	hex17_24 =  bin_to_hex(bit17_24)
	hex24_32 = bin_to_hex(bit25_32)
	ts = 0
	if hex1_8 != "00" or hex9_16 != "00":
		relay(hex1_8,hex9_16,'01',"01") #press 1 key on card 1
		ts = TIME_between_card1_card2
	if hex17_24 != "00"or hex24_32 != "00":
		time.sleep(ts)
		relay(hex17_24,hex24_32,'01',"02") #press 1 key on card 2

	#print time1	
	time.sleep(time1)
	#print ">> Pressing "+bit17_24 +" "+bit9_16+" "+bit1_8+" key"
	ts = 0
	if hex1_8 != "00" or hex9_16 != "00":
		relay(hex1_8,hex9_16,'02',"01") #release 1 key on card 1
		ts = TIME_between_card1_card2
	if hex17_24 != "00"or hex24_32 != "00":
		time.sleep(ts)
		relay(hex17_24,hex24_32,'02',"02") #release 1 key on card 2
	#print time2
	time.sleep(time2)
	return 1

