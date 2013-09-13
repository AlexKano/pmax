import xmlrpclib
import threading

class ServerAdapter:
	_server = None
	_actionsQueue = []
	_processorThread = None
	
	def __init__(self, ip):
		self._server = xmlrpclib.ServerProxy(ip)
		self._startProcessingThread();
		
	## For panel ##
	def get_lcd(self):
		self._server.get_lcd();
		
	def start_vkp_mode(self):
		self._server.start_vkp_mode();
	
	def send_key(self, action):
		self._actionsQueue.append(action)
		# self._server.send_key(action);
		
		
	## For devices ##
	def key_b(self, params):
		self._server.key_b(params);
		
	def relaykey(self, params):
		if len(params) > 2:
			self._server.relaykey_b32(params);
		else:
			self._server.relaykey(params);
	
	
	## Private functions ##
	def _processActions(self):
		# for now works only with panel actions
		while True:
			while len(self._actionsQueue):
				self._server.send_key(self._actionsQueue.pop(0))
			sleep(100)
	
	def _startProcessingThread(self):
		_processorThread = threadingThread(target=self._processActions, args=self) 
		_processorThread.daemon = True  # YOU MAY NOT WANT THIS: Only use this line if you want the program to exit without waiting for the thread to finish 
		_processorThread.start()        # Starts the thread 
		_processorThread.setName('actionsProcessorThread') # Makes it easier to interact with the thread later
		
		