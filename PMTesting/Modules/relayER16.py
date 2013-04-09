#!/usr/bin/env python
import serial
import out
import com
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
	
def dec_to_2hex(dec): 
	sbin =  dec_to_bin(dec)
	lens = len(sbin)
	bit38 = sbin[lens-24:lens-16]
	bit28 = sbin[lens-16:lens-8]
	bit18 = sbin[lens-8:lens]
	dec_bit28 = int(bit28,2)
	dec_bit18 = int(bit18,2)
	hex_bit28 = hex(dec_bit28)
	hex_bit18 = hex(dec_bit18)
	hex_bit28 = hex_bit28[2:4]
	hex_bit18 = hex_bit18[2:4]
	
	if len (hex_bit28)<2:
		hex_bit28 = "0"+hex_bit28
	if len (hex_bit18)<2:
		hex_bit18 = "0"+hex_bit18
	return hex_bit18,hex_bit28
ser = serial.Serial(com.ComRelayER16(),"9600")

def relay(Num,state):
        s = '5508'+state+Num+'01000024'
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
def bin_relay(relay1_8,relay9_16,state, num_card ="01"):
	bin = relay9_16 + relay1_8
	dec = int(bin,2)
	relay1_8,relay9_16 = dec_to_2hex(dec)
        s = '5508'+state+relay9_16+relay1_8+num_card+'000024'
	#print s
        for i in range(len(s)/2):
                c = chr(int(s[i*2:i*2+2],16))
                ser.write(c)

	return 1
