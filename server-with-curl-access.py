import ansar.connect as ar

# Declare the requests.
class Multiply(object):
	def __init__(self, x=0.0, y=0.0):
		self.x = x
		self.y = y

# Response details.
class Output(object):
	def __init__(self, value=0.0):
		self.value = value

ar.bind(Multiply)
ar.bind(Output)

# The main object.
class Server(ar.Point, ar.Stateless):
	def __init__(self):
		ar.Point.__init__(self)
		ar.Stateless.__init__(self)

def Server_Start(self, message):		# Start the networking.
	ipp = ar.HostPort('127.0.0.1', 5051)
	self.table = ar.GroupTable(
		api=ar.CreateFrame(ar.ListenAtAddress, ipp, api_server=[Multiply,]),
	)
	self.group = self.table.create(self)

def Server_Stop(self, message):			# Control-c or software interrupt.
	self.send(message, self.group)		# Stop the networking.

def Server_Completed(self, message):	# Networking stopped.
	self.complete(ar.Aborted())			# End this process.

def Server_Multiply(self, message):		# Response to Multiply.
	response = Output(message.x * message.y)
	self.reply(response)

# Declare the messages expected by
# the main object.
SERVER_DISPATCH = [
    ar.Start,			# Initiate networking.
	ar.Stop,			# Ctrl-c or programmed interrupt.
	ar.Completed,		# Networking cleared.
	Multiply,			# Network API.
]

ar.bind(Server, SERVER_DISPATCH)

# Start an instance of the process object.
if __name__ == '__main__':
	ar.create_object(Server)
