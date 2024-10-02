import ansar.connect as ar

from crunch_api import *

# The client object.
class Client(ar.Point, ar.Stateless):
    def __init__(self, settings):
        ar.Point.__init__(self)
        ar.Stateless.__init__(self)
        self.settings = settings
        self.table = None
        self.group = None
        self.client_value = None

def Client_Start(self, message):         # Start the networking.
    host = self.settings.host
    port = self.settings.port
    ipp = ar.HostPort(host, port)

    self.table = ar.GroupTable(
        server_a=ar.CreateFrame(ar.ConnectToAddress, ipp, api_client='/', ansar_server=True),
        server_b=ar.CreateFrame(ar.ConnectToAddress, ipp, api_client='/', ansar_server=True),
    )
    self.group = self.table.create(self, get_ready=8.0)

def Client_GroupUpdate(self, message):
    self.table.update(message)

def Client_Ready(self, message):
    settings = self.settings
    request = settings.request(settings.x, settings.y)

    a = self.create(ar.Concurrently,
        (Divide(4.0, 2.0), self.table.server_a),
        (request, self.table.server_b),
    )
    def step_1(response):
        self.client_value = response[1]
        self.send(ar.Stop(), self.group)

    self.assign(a, ar.OnCompleted(step_1))

def Client_NotReady(self, message):
    self.abort(ar.Aborted())

def Client_Completed(self, message):
    d = self.debrief(self.return_address)
    if isinstance(d, ar.OnCompleted):
        d(message.value)
    self.complete(self.client_value or message.value)

def Client_Stop(self, message):          # Control-c or software interrupt.
    self.client_value = ar.Aborted()
    self.send(message, self.group)

# Declare the messages expected by the server object.
CLIENT_DISPATCH = [
    ar.Start,           # Initiate networking.
    ar.GroupUpdate,
    ar.Ready,            # Ready to send.
    ar.Completed,
	ar.NotReady,
    ar.Stop,            # Ctrl-c or programmed interrupt.
]

ar.bind(Client, CLIENT_DISPATCH)

# Configuration for this executable.
class Settings(object):
    def __init__(self, host=None, port=None, request=None, x=None, y=None):
        self.host = host
        self.port = port
        self.request = request
        self.x = x
        self.y = y

SETTINGS_SCHEMA = {
    'host': str,
    'port': int,
    'request': ar.Type,
    'x': float,
    'y': float,
}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)

# Define default configuration and start the server.
factory_settings = Settings(host='127.0.0.1', port=5051, request=Multiply, x=1.5, y=2.25)

if __name__ == '__main__':
    ar.create_object(Client, factory_settings=factory_settings)