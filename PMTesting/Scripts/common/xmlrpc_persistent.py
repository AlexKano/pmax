#!/usr/bin/python

import sys
import SimpleXMLRPCServer
import SocketServer
import xmlrpclib



# =============================================================================
# Class implementing a request handler for xml-rpc
# =============================================================================

class XMLRPCHandler (SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):

    protocol_version = "HTTP/1.1"
    rpc_paths = ('/RPC2',)

    # ---------------------------------------------------------------------------
    # Process a POST request
    # ---------------------------------------------------------------------------

    def do_POST (self):
        """
        This is a fix for SimpleXMLRPCRequestHandler.do_POST, which does always
        close the underlying socket - even if self.close_connection is false
        (= persistent connection)
        """

        try:
            # get arguments
            data = self.rfile.read (int (self.headers ["content-length"]))
            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            response = self.server._marshaled_dispatch (data, getattr (self, '_dispatch', None))
        except: # This should only happen if the module is buggy
                # internal error, report as HTTP server error
            self.send_response(500)
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-length", str (len (response)))
            self.end_headers()
            self.wfile.write(response)
            
            # flush data sent to the socket
            self.wfile.flush()
            
            # and shut down the connection if we do not have a persistent connection
            if self.close_connection:
                self.connection.shutdown(1)


# =============================================================================
# This class implements a (forking) XML-RPC server, which supports None values
# =============================================================================

class BetterXMLServer(SocketServer.ThreadingTCPServer, SimpleXMLRPCServer.SimpleXMLRPCServer):

    allow_reuse_address = True    # for SocketServer.TCPServer

    # ---------------------------------------------------------------------------
    # Constructor
    # ---------------------------------------------------------------------------
    
    def __init__ (self, addr, requestHandler=XMLRPCHandler, logRequests=1, allow_none=False):
        SimpleXMLRPCServer.SimpleXMLRPCServer.__init__ (self, addr, requestHandler, logRequests)
        self.allow_none = allow_none


    # ---------------------------------------------------------------------------
    # Dispatch a method from marshalled xml data
    # ---------------------------------------------------------------------------

    def _marshaled_dispatch (self, data, dispatch_method=None):
        """
        Dispatches an XML-RPC method from marshalled (XML) data.
    
        XML-RPC methods are dispatched from the marshalled (XML) data
        using the _dispatch method and the result is returned as
        marshalled data. For backwards compatibility, a dispatch
        function can be provided as an argument (see comment in
        SimpleXMLRPCRequestHandler.do_POST) but overriding the
        existing method through subclassing is the prefered means
        of changing method dispatch behavior.
    
        This is a fix for SimpleXMLRPCDispatcher, which does not honor allow_none
        flag of xmlrpclib.dumps ().
        """

        params, method = xmlrpclib.loads (data)
        
        # generate response
        try:
            if dispatch_method is not None:
                response = dispatch_method (method, params)
            else:
                response = self._dispatch (method, params)
            
            # wrap response in a singleton tuple
            response = (response,)
            response = xmlrpclib.dumps (response, methodresponse=1,
                                        allow_none=self.allow_none)
        
        except xmlrpclib.Fault, fault:
            response = xmlrpclib.dumps (fault, allow_none=self.allow_none)
        
        except:
            # report exception back to server
            response = xmlrpclib.dumps (xmlrpclib.Fault (1, "%s:%s" % (sys.exc_type, sys.exc_value)), allow_none=self.allow_none)
        
        return response
