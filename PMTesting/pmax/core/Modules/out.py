import time
import datetime
def clear_log():
	f = open ("Logs/log.txt","w")
	f.close
	f = open ("Logs/error_log.txt","w")
	f.close
def prnt (value1,out1 = "all"):
	value = str(value1)
	tt = datetime.datetime.now()
	sss = str(tt.strftime("%d.%m.%Y %H:%M:%S"))
	if out1 == "all":
		f = open ("Logs/log.txt","a")
		f1 = open ("Logs/all_log.txt","a")
		f.write (sss +": " + value)
		f.write ("\n")
		f1.write (sss +": " + value)
		f1.write ("\n")
		print value
		f.close
		f1.close
	if out1 == "ipmp":
		f = open ("Logs/IPMPlog.txt","a")

		f.write (sss +": " + value)
		f.write ("\n")

		f.close

	if out1 == "all+error":
		f = open ("Logs/log.txt","a")
		f1 = open ("Logs/all_log.txt","a")
		f.write (sss +": " + value)
		f.write ("\n")
		f1.write (sss +": " + value)
		f1.write ("\n")
		print value
		f.close
		f1.close	
		f3 = open ("Logs/error_log.txt","a")
		f3.write (sss +": " + value)
		f3.write ("\n")
		f3.close
	if out1 == "time":
		f = open ("Logs/Timelog.txt","a")

		f.write (sss +": " + value)
		f.write ("\n")

		f.close
