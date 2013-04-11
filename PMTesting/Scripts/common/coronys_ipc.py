import ctypes, ctypes.wintypes
import os, sys
    

IpcCreateServer, IpcIsNewMessage,  IpcReplyToServer, IpcGetNewMessageIndex,\
IpcGetNewMessageText, IpcReleaseServer, IpcSendMessage, IpcGetServerName = (None, None, None, None, None, None, None, None)
SendToCoronysLog = None

def init_rpc():
    global IpcCreateServer, IpcIsNewMessage, IpcReplyToServer, IpcGetNewMessageIndex,\
    IpcGetNewMessageText, IpcReleaseServer, IpcSendMessage, IpcGetServerName
    global SendToCoronysLog

    ETSdll = ctypes.CDLL('c:\\ETS\\ETS_IPC_EX_DLL.dll')
    prototype = ctypes.CFUNCTYPE (ctypes.c_long, ctypes.wintypes.LPCSTR)
    params = (1, "ServerName", 'SER_FOR_PY'),
    IpcCreateServer = prototype(('IpcCreateServer', ETSdll), params)

    prototype = ctypes.CFUNCTYPE (ctypes.c_long)
    params = None
    IpcIsNewMessage = prototype(('IpcIsNewMessage', ETSdll), params)

    prototype = ctypes.CFUNCTYPE (ctypes.c_long, ctypes.c_long, ctypes.wintypes.LPCSTR)
    params = (1, 'msg_index', 0), (1, 'msg_text', 0)
    IpcReplyToServer = prototype(('IpcReplyToServer', ETSdll), params)

    prototype = ctypes.CFUNCTYPE (ctypes.c_long)
    params = None
    IpcGetNewMessageIndex = prototype(('IpcGetNewMessageIndex', ETSdll), params)

    prototype = ctypes.CFUNCTYPE (ctypes.wintypes.LPCSTR)
    params = None
    IpcGetNewMessageText = prototype(('IpcGetNewMessageText', ETSdll), params)

    prototype = ctypes.CFUNCTYPE (ctypes.c_void_p)
    params = None
    IpcReleaseServer = prototype(('IpcReleaseServer', ETSdll), params)

    prototype = ctypes.CFUNCTYPE (ctypes.c_long, ctypes.wintypes.LPCSTR, ctypes.c_long, ctypes.wintypes.LPCSTR)
    params =  (1, 'server_name', 0), (1, 'msg_index', 0), (1, 'msg_text', 0)
    IpcSendMessage = prototype(('IpcSendMessage', ETSdll), params)

    prototype = ctypes.CFUNCTYPE (ctypes.wintypes.LPCSTR)
    params = None
    IpcGetServerName = prototype(('IpcGetServerName', ETSdll), params)

    ets_app_name = '\\\\.\\mailslot\\0\\ETS\\' + os.environ['USERNAME'] + '\\1' # instanse number
    SendToCoronysLog = lambda s: IpcSendMessage(ctypes.c_char_p(ets_app_name), ctypes.c_long(32),\
     ctypes.c_char_p("Tmmessage 188, \"%s: %s\"" % (sys.argv[0],s)))

    server_name = ctypes.create_string_buffer("DEMO_IPC")
    if(IpcCreateServer(server_name) == 0):
        return None
    return IpcGetServerName()

if __name__ == "__main__":
    
    print init_rpc()



    #ets_app_name = '\\\\.\\mailslot\\0\\ETS\\' + os.environ['USERNAME'] + '\\1' # instanse number
    #print  ets_app_name
    #IpcSendMessage(ctypes.c_char_p(ets_app_name), ctypes.c_long(32), ctypes.c_char_p("Tmmessage 188, \"%s: %s\"" % (sys.argv[0], "test message")))
    SendToCoronysLog("cocronys_ipc.py's test message.")