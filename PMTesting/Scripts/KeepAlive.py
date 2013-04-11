#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, select, time
import re
import threading

import os
cmd_folder = os.path.dirname(os.path.abspath(__file__))
#sys.path.append( cmd_folder+'\..'+'\Modules' )
#sys.path.append( cmd_folder+'\Modules' )
import ssh_lib


class ThreadForSearch(threading.Thread):
    def __init__( self, Timeout, PanelID, ServerHost, Username, Password, LogPath, IsGetTime ):
        threading.Thread.__init__(self)
        self.Timeout   = Timeout
        self.PanelID   = PanelID
        self.ServerHost = ServerHost
        self.Username  = Username
        self.Password  = Password
        self.LogPath   = LogPath
        self.IsGetTime2 = IsGetTime
        self.Result = 0
        
    def run ( self ):
        self.Result = WaitKeepAlive ( self.Timeout, self.PanelID, self.ServerHost, self.Username, self.Password, self.LogPath, self.IsGetTime2 )
        print "End thread. IP: {0}. Result: {1}".format( self.ServerHost, self.Result )


def WaitKeepAlive ( Timeout, PanelSerial, Server, Username, Password, LogPath, IsGetTime = 0):

    LINES_TO_READ = 100
    Result = 0

    fpnTime = '{0}\\..\\Tmp\\time_ip_server_{1}_{2}.txt'.format( cmd_folder, Server, PanelSerial )
    time_IP = ''
    try:
        ft = open( fpnTime, "r", 0 ) # Win
        time_IP = ft.readline()
        print 'Read time: "{0}" from file "{1}"'.format( time_IP, fpnTime )
        ft.close()
    except IOError:
        print 'Exception in opening file {0}'.format( fpnTime )

    #Trying to spawn ssh connection
    try:
        ssh = ssh_lib.open_ssh(Server, Username, Password)
    except:
        print "Unable to open SSH connection: ", sys.exc_info()[0]
        sys.exit("OPEN_SSH")

    transport = ssh.get_transport()
    
    """
    channel = transport.open_session()

    if IsGetTime == 1:
        ssh_comm = 'tail -n 1 {0}'.format( LogPath )
    else:
        #ssh_comm = '''bash -c "tail -{0}f {1} | grep '.*sia_server.*'"'''.format( LINES_TO_READ, LogPath )
        ssh_comm = '''tail -{0}f {1}'''.format( LINES_TO_READ, LogPath )
        #ssh_comm = '''bash -v -c "tail -{0}f {1}"'''.format( LINES_TO_READ, LogPath )
    print ssh_comm

    channel.exec_command(ssh_comm)

    if IsGetTime == 1:
        log_buf = channel.recv(5000)
        pattern_str = "^([A-Z]+[a-z]+[ ]+[0-9]+ [0-9]+:[0-9]+:[0-9]+) .+"
        groups = re.search( re.compile(pattern_str, re.MULTILINE), log_buf )
        if groups != None:
            try:
                f = open( fpnTime, "w", 0 ) # Win
                f.write( groups.group(1) )
                print 'Wrote time: "{0}" in file "{1}"'.format( groups.group(1), fpnTime )
                f.close()
            except IOError:
                print 'Exception in writing time in file "{0}"'.format( fpnTime )
                return Result
        else:
            print 'Error in searching time!'
        return Result

    time_start = time.time()
    print "time_start: {0}".format( time_start )
    time_stop = time_start + int(Timeout)
    while time.time() < time_stop:
        rl, wl, xl = select.select( [channel], [], [], 1.0 )
        if (time_stop - time.time()) < 20: print 'Remained {0} sec.'.format( time_stop - time.time() )

        #print 'len: {0}'.format( len(rl) )
        if len(rl) <= 0: continue

        #log_buf = channel.recv(1000)
        log_buf = channel.recv(20000)

        #sys.stdout.write( log_buf )
        #sys.stdout.flush()
        
        lines = log_buf.split("\n")
        for line in lines:
            sys.stdout.write( line+"\n" )
            sys.stdout.flush()

    
    return Result
    """

    
    time_start = time.time()
    print "time_start: {0}".format( time_start )
    time_stop = time_start + int(Timeout)
    
    f = open( '{0}\\..\\Tmp\\{1}_{2}_sequence_for_waiting.txt'.format( cmd_folder, PanelSerial, Server ), "r", 0 )
    while True:
        Line = f.readline()
        if Line == '': break
        if Line[0] == '#': continue
        Line2 = Line#[:len(Line)-1].strip()
        print "Line: {0}".format( Line2 )

        Result = 0

        channel = transport.open_session()

        if IsGetTime == 1:
            ssh_comm = 'tail -n 1 {0}'.format( LogPath )
        else:
            #ssh_comm = '''bash -c "tail -{0}f {1} | grep '.*sia_server.*'"'''.format( LINES_TO_READ, LogPath )
            ssh_comm = '''tail -{0}f {1}'''.format( LINES_TO_READ, LogPath )
            #ssh_comm = '''bash -v -c "tail -{0}f {1}"'''.format( LINES_TO_READ, LogPath )
        print ssh_comm

        channel.exec_command(ssh_comm)

        if IsGetTime == 1:
            log_buf = channel.recv(5000)
            pattern_str = "^([A-Z]+[a-z]+[ ]+[0-9]+ [0-9]+:[0-9]+:[0-9]+) .+"
            groups = re.search( re.compile(pattern_str, re.MULTILINE), log_buf )
            if groups != None:
                try:
                    f = open( fpnTime, "w", 0 ) # Win
                    f.write( groups.group(1) )
                    print 'Wrote time: "{0}" in file "{1}"'.format( groups.group(1), fpnTime )
                    f.close()
                except IOError:
                    print 'Exception in writing time in file "{0}"'.format( fpnTime )
                    return Result
            else:
                print 'Error in searching time!'
            return Result

        while time.time() < time_stop:
            rl, wl, xl = select.select( [channel], [], [], 1.0 )
            if (time_stop - time.time()) < 20: print 'Remained {0} sec.'.format( time_stop - time.time() )
                
            if len(rl) > 0:

                log_buf = channel.recv(20000) # Does it return entire lines?

                pattern_str = Line2.format( PanelSerial )  # from 2012-03-26
                
                groups = re.search( re.compile(pattern_str, re.MULTILINE), log_buf )

                if groups == None:
                    continue

                if groups.group(1) <= time_IP:
                    print '''Found something, but it's time is less than the time from file. Event time: "{0}". File time: "{1}".'''.format( groups.group(1), time_IP )
                    continue

                if groups != None:
                    #print 'FOUND some event!: ' + groups# Acc: {0}, EvNum: {1}, Part: {2}, SourceNum(Zone): {3}'.format( groups.group(1), groups.group(2), groups.group(3), groups.group(4) )
                    print 'FOUND Keep alive! ({0}{1})'.format( groups.group(1), groups.group(2) )
                    Result = 1
            
            if Result != 0: break
            else:
                if (time_stop - time.time()) <= 0: return Result
            #if ((time_stop - time.time()) <= 0) and (Result != 0): return Result

    f.close()

    return Result


if __name__ == "__main__":

    iTimeout      = int(sys.argv[1])            # Timeout
    aPanelID      = sys.argv[2]                 # PanelID
    aServerHosts  = sys.argv[3].split(',')      # Servers IP adderesses
    aUsernames    = sys.argv[4].split(',')      # Usernames
    aPasswords    = sys.argv[5].split(',')      # Passwords
    aLogPathes    = sys.argv[6].split(',')      # Pathes to log files
    IsGetTime1 = 0
    if (len(sys.argv) == 8):
        if sys.argv[7] == 'time': IsGetTime1 = 1

    Threads = [None, None]

    for iServerIndex in range(len(aServerHosts)):
        
        try:
            Threads[iServerIndex] = ThreadForSearch( iTimeout, aPanelID, aServerHosts[iServerIndex], aUsernames[iServerIndex], aPasswords[iServerIndex], aLogPathes[iServerIndex], IsGetTime1 )
            #Starting appropriate thread
            Threads[iServerIndex].start()
        except:
            print "Unhandled exception while opening threads:", sys.exc_info()[0]
            sys.exit("OPEN_THREAD")
            raise

    # Waiting for answers from threads
    for iThreadNumber in range(len(aServerHosts)):
        print ">>>>>>>>>>> START JOIN {0} >>>>>>>>>>>>>".format( iThreadNumber )
        #Threads[iThreadNumber].join(5)
        Threads[iThreadNumber].join(iTimeout+10)
        print "<<<<<<<<<<<< END JOIN {0} <<<<<<<<<<<<<<".format( iThreadNumber )

    # Outputting results to communication file
    ResStr = ''
    bFirstThread = 1
    for tThread in Threads:
        if tThread != None:
            if bFirstThread != 1:
                ResStr += ','
            ResStr += str(tThread.Result)
            bFirstThread = 0
    print "Result is: '", ResStr, "'"
    f = open(cmd_folder+'\..'+'\WaitEvents.txt', "w", 0)
    f.write( ResStr )
    f.close()

    sys.exit(0)
