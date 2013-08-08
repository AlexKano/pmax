import paramiko
import sys
sys.path.append(".\Modules")
import os
import time
import datetime
#import devices
import random
#import card
import out
#import navigator
import select

def login(ip_adress='212.90.164.10',uname='root',pwd='visonic'):
	op = paramiko.SSHClient()
	op.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	op.connect(ip_adress, username=uname,password=pwd)
	i, o, e = op.exec_command('s')
	i, o, e = op.exec_command('l')
	i, o, e = op.exec_command('visonic')
	transport = op.get_transport()
	channel = transport.open_session()
	channel.exec_command("tail -n 100 -f /var/log/messages")
	return channel,op

def find_event_on_IPMP(channel,event,attempts=6000,timeout=0.01):
	ifevent=False
	for att in range(attempts):
		#print att
		rl, wl, xl = select.select([channel],[],[],0.0)
		time.sleep(timeout)
		if len(rl) > 0:
			str1 = channel.recv(1024)
			dd=str1.split('\n')	
			for i in range(len(dd)):
				if event in dd[i]:
					ifevent=True
					break
		if ifevent: break
	return ifevent



if __name__=="__main__":
	connection=login()
	navigator.send_key_fast('panic',0.3)
	print find_event_on_IPMP(connection[0],'CID event: \'#0B11AD|1120',1000,0.01)
	connection[1].close()