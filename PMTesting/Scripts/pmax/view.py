
from common.xmlrpc_persistent import BetterXMLServer
import threading
import config
from common import log

class XMLRPC(threading.Thread):
    _Server = None

    def __init__(self, API, host = "localhost", port = 8000):
        threading.Thread.__init__(self)
        verbosity = False
        if (config.VERBOSE):
            verbosity = True

        self._Server = BetterXMLServer ((host, port), logRequests = verbosity, allow_none = True)
        #self._Server = SimpleXMLRPCServer((host, port), requestHandler=XMLRPCHandler, logRequests=verbosity)
        self._Server.register_introspection_functions()
        self._Server.register_instance(API)
        self._Server.register_function(self.stop, "stop")
        self._Server.register_function(self.is_alive, "is_alive")

    def run(self):
        log.write("Launching XML-RPC server [" + str(self._Server.server_address[0]) + ":" + str(self._Server.server_address[1]) + "]")
        self._Server.serve_forever()

    def stop(self):
        log.write("XML-RPC Server stopped")
        self._Server.shutdown()

    def is_alive(self):
        return True

class Console(threading.Thread):
    NAME = "DeviceSimulator"

    _stop_needed = 0
    _API = None
    def __init__(self, API):
        threading.Thread.__init__(self)
        self._stop_needed = 0
        self._API = API

    def run(self):
        while (not self._stop_needed):
            log.write(self.NAME + " > " , "nolog")
            command = raw_input()
            self._execute_command(command)
            if command.strip().upper() == "EXIT":
                self._xmlrpc.stop() 
                break

    def _execute_command(self, command):
        '''
        This function executes command specified by user in Console.
        command - command with parameters taken from Console
        '''

        args = command.split()
        params = []
        if (len(args) > 1):
            params = args[1:]

        self._API._dispatch(args[0], params)

class View():
    _xmlrpc = None
    _console_thread = None

    def __init__(self, API):
        self._xmlrpc = XMLRPC(API)
        self._xmlrpc.start()
        self._console_thread = Console(API)
        self._console_thread.start()
        self._console_thread.join()
        self._xmlrpc.join()

