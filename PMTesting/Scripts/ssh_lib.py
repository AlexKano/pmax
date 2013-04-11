#!/usr/bin/python
# -*- coding: utf-8 -*-

import paramiko

def open_ssh(ip, uname, pwd):
    ssh = paramiko.SSHClient()
    #print ssh
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #print ssh
    #ssh.load_system_host_keys()
    ssh.connect(ip, username=uname, password=pwd)
    #print ssh
    i, o, e = ssh.exec_command('s')
    print o.read()
    i, o, e = ssh.exec_command('l')
    print o.read()
    i, o, e = ssh.exec_command('visonic')
    print o.read()
    print "SSH Connection successfully opened"
    return ssh


if __name__ == "__main__":

    pass
