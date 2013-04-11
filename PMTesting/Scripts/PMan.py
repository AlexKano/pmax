#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, select, time
import re
import threading

import os
cmd_folder = os.path.dirname(os.path.abspath(__file__))
#sys.path.append( cmd_folder+'\..'+'\Modules' )
#import ssh_lib
import ssh_lib


class ServerSettings(threading.Thread):    
    def __init__( self, ServerIP, Username, Password, Command, Params ):
        threading.Thread.__init__(self)
        self.ServerIP = ServerIP
        self.Username = Username
        self.Password = Password
        self.Command = Command
        self.Params = Params
        
    def run( self ):
        #Spawning SSH Connection
        try:
            self.ssh = ssh_lib.open_ssh( self.ServerIP, self.Username, self.Password )
        except:
            print "Unable to open SSH connection: ", sys.exc_info()[0]
            sys.exit("OPEN_SSH")

        #transport = ssh.get_transport()
        #channel = transport.open_session()

        if (self.Command == "set_ka_time_mins"):
            self._SetKATime( self.Params )
        elif (self.Command == "set_enc_key"):
            self._SetEncryptionKey( self.Params )
        else:
            print "Unknown function to perform"
            sys.exit("UNKNOWN_FUNCTION")

        return

    def __del__( self ):
        self.ssh.close()
        

    def _SetKATime ( self, KATime ):
        #Creating MySQL query to set KA Time
        sQuery = "UPDATE unit_group_type \
                  SET ugt_timer_seconds=" + str(int(KATime) * 60) + " \
                  WHERE utg_id=1 AND \
                        ugt_access_type='gprs'"
        self.__ExecSSHCommand("mysql ipmp -e \"" + sQuery + "\"")

        #Calling Reconfigure() for all panels
        IPMPPyScriptPath = "/opt/visonic/ipmp/script/ipmp_py.sh"
        #Creating tmp file with python commands
        ReconfigureTmpPath = "/tmp/reconf.tmp"
        self.__ExecSSHCommand("echo 'import ipmp' > " + ReconfigureTmpPath)
        self.__ExecSSHCommand("echo 'pmax = ipmp.Pmax()' >> " + ReconfigureTmpPath)
        self.__ExecSSHCommand("echo 'pmax.Reconfigure()' >> " + ReconfigureTmpPath)
        self.__ExecSSHCommand(IPMPPyScriptPath + " < " + ReconfigureTmpPath)
        #Removing tmp file
        self.__ExecSSHCommand("rm -f " + ReconfigureTmpPath)

        return

    def _SetEncryptionKey ( self, EncKey ):
        #Setting encryption key to the file

        if (len(EncKey) != 32):
            print "Encryption key should be 32 HEX symbols. Actual length is " + str(len(EncKey)) + " symbols"
            sys.exit()
        
        IPMPConfigXML = "/ha_shared/ipmp/config/app_cfg.xml"
        sReplaceCommand = "sed s:\<work_key\>[0-9A-Z]*\<\/work_key\>:\<work_key\>" + EncKey + "\<\/work_key\>: < " + IPMPConfigXML + " > " + IPMPConfigXML + ".tmp"
        self.__ExecSSHCommand(sReplaceCommand)
        
        #Creating backup of original XML file
        self.__ExecSSHCommand("mv -f " + IPMPConfigXML + " " + IPMPConfigXML + "~")
        self.__ExecSSHCommand("mv -f " + IPMPConfigXML + ".tmp" + " " + IPMPConfigXML)

        #Restarting sia_server service
        SIAServerPath = "/etc/init.d/sia_server"
        self.__ExecSSHCommand(SIAServerPath + " " + "restart")

        return

    def __ExecSSHCommand( self, Command ):
        SSHClient = self.ssh

        print "<command>"
        print "[Action]: " + Command
        i,o,e = SSHClient.exec_command(Command)
        print "[Output]: " + str(o.read())
        print "</command>\r\n"

        return


    
if __name__ == "__main__":

    # Script parameters:
    ARGS_COUNT = 5
    ScriptParams = "<server1_IP[,server2_IP]> <server1_username[,server2_username]> <server1_password[,server2_password]> <command1[,command2]> <params1[,params2]>"

    if (len(sys.argv) != ARGS_COUNT + 1):
        print "Incorrect number of arguments"
        #Outputting udage help
        print "Usage: " + sys.argv[0][sys.argv[0].rfind("\\") + 1:] + " " + ScriptParams
        sys.exit() #INCORRECT_ARGUMENTS

    iTimeout = 30

    #Getting number of servers

    aServerHosts  = sys.argv[1].split(',')      # Servers IP adderesses
    aUsernames    = sys.argv[2].split(',')      # Usernames
    aPasswords    = sys.argv[3].split(',')      # Passwords
    aCommands     = sys.argv[4].split(',')      # Commands to the servers
    aParams       = sys.argv[5].split(',')      # Parameters to the commands

    Threads = [None, None]

    for iServerIndex in range(len(aServerHosts)):
        try:
            Threads[iServerIndex] = ServerSettings( aServerHosts[iServerIndex], aUsernames[iServerIndex], aPasswords[iServerIndex], aCommands[iServerIndex], aParams[iServerIndex])
            # Starting appropriate thread
            Threads[iServerIndex].start()
        except:
            print "Unhandled exception while opening threads:", sys.exc_info()[0]
            sys.exit("OPEN_THREAD")
            raise

    for iServerIndex in range(len(aServerHosts)):
        Threads[iServerIndex].join()
        del Threads[iServerIndex]

    sys.exit(0)
