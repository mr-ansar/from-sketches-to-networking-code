import ansar.connect as ar

# Declare the requests.
class Multiply(object):
	def __init__(self, x=0.0, y=0.0):
		self.x = x
		self.y = y

class Divide(object):
	def __init__(self, x=0.0, y=0.0):
		self.x = x
		self.y = y

# Response details.
class Output(object):
	def __init__(self, value=0.0):
		self.value = value

ar.bind(Multiply)
ar.bind(Divide)
ar.bind(Output)

API = [
	Multiply,
	Divide,
]

# The server object.
class Server(ar.Threaded, ar.Stateless):
	def __init__(self, settings):
		ar.Threaded.__init__(self)
		ar.Stateless.__init__(self)
		self.settings = settings

def Server_Start(self, message):		# Start the networking.
	host = self.settings.host
	port = self.settings.port
	ipp = ar.HostPort(host, port)
	self.table = ar.GroupTable(
		api=ar.CreateFrame(ar.ListenAtAddress, ipp, api_server=API),
	)
	self.group = self.table.create(self)

def Server_Stop(self, message):			# Control-c or software interrupt.
	self.send(message, self.group)		# Stop the networking.

def Server_Completed(self, message):	# Networking stopped.
	self.complete(ar.Aborted())			# End this process.

def Server_Multiply(self, message):		# Received Multiply.
	value = message.x * message.y
	response = Output(value=value)
	self.reply(response)

def Server_Divide(self, message):		# Received Multiply.
	value = message.x / message.y
	response = Output(value=value)
	self.reply(response)

# Declare the messages expected by the server object.
SERVER_DISPATCH = [
    ar.Start,			# Initiate networking.
	ar.Stop,			# Ctrl-c or programmed interrupt.
	ar.Completed,		# Networking cleared.
	Multiply,			# Network API.
	Divide,
]

ar.bind(Server, SERVER_DISPATCH)

# Configuration for this executable.
class Settings(object):
	def __init__(self, host=None, port=None):
		self.host = host
		self.port = port

SETTINGS_SCHEMA = {
	'host': ar.Unicode(),
	'port': ar.Integer8(),
}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)

# Start an instance of the process object.
if __name__ == '__main__':
	ar.create_object(Server, factory_settings=Settings(host='127.0.0.1', port=5051))
