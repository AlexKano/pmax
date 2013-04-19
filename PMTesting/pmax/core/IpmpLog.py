__author__ = 'KANO'
import select
import time
import paramiko
import ssh
from pmax.core.Cache import GlobalStorage


class IpmpLog:
    CACHE_KEY_IPMP_LOG = "IPMP_LOG_"

    IP = None
    Password = None
    UserName = None
    Port = 22
    LogCommand = "tail -n 100 -f /var/log/messages"

    Log = []

    _isLogRunning = False
    _sshChannel = None
    _sshSession = None

    def __init__(self, server_ip="212.90.164.4", user_name='root', ssh_password="visonic"):
        self.IP = server_ip
        self.UserName = user_name
        self.Password = ssh_password

    def openSSHSession(self):
        #pass
        if self._sshSession is not None: return
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.IP, username='root', password=self.Password, port=self.Port)
        ssh.exec_command('s')
        ssh.exec_command('l')
        ssh.exec_command('visonic')
        transport = ssh.get_transport()
        channel = transport.open_session()
        #
        self._sshSession = ssh
        self._sshChannel = channel

    def startLog(self):
        if not self._isLogRunning:
            self._sshChannel.exec_command(self.LogCommand)
            self._isLogRunning = True

    def closeSSHSession(self):
        if self._sshSession:
            self._sshSession.close()
        self._isLogRunning = False

    def getLog(self, lines_limit=100):
        
        str1 = self._sshChannel.recv(1024)
        str_split = str1.split("\n")
        self.Log = str_split[:lines_limit]
        return self.Log


    @classmethod
    def GetByIP(cls, IP):
        return GlobalStorage.IpmpLog.get(cls.CACHE_KEY_IPMP_LOG + IP)

    @classmethod
    def SetByIP(cls, log_obj):
        GlobalStorage.IpmpLog[cls.CACHE_KEY_IPMP_LOG + log_obj.IP] = log_obj

    # def waitforString(self, channel, string, timeout=100, num=1, check_interval=100):
    #     data = string.split('***')
    #     for k in range(timeout * check_interval):
    #         rl, wl, xl = select.select([channel], [], [], 0.0)
    #         if rl:
    #             continue
    #
    #         # Must be stdout
    #         str1 = channel.recv(1024)
    #         str_split = str1.split("\n")
    #         for line in str_split:
    #             out.prnt(str1, "ipmp")
    #             if self.__checkOccurrence(line, data):
    #                 #out.prnt(str(num) + " Event " + string + " is received on IPMP")
    #                 strlog = line.split("(D)")
    #
    #                 out_string = str(num) + " " + strlog[0][:15] + "->" + strlog[1] \
    #                     if len(strlog) > 1 \
    #                     else str_split
    #
    #                 out.prnt(out_string)
    #
    #                 return 1
    #         time.sleep(1.0 / check_interval)
    #
    #     out.prnt("Time out " + str(timeout) + " s", "all+error")
    #     out.prnt("no possible to find " + string + "----------ERRORIPMP------------", "all+error")
    #     #strlcd = read()
    #     #out.prnt("LCD display: "+strlcd)
    #     return 0
    #
    # def __checkOccurrence(self, line, data):
    #     for d in data:
    #         if (d in line) == 0:
    #             return False
    #     return True
