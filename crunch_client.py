import ansar.connect as ar

from crunch_api import *

# The client object.
class Client(ar.Point, ar.Stateless):
    def __init__(self, settings):
        ar.Point.__init__(self)
        ar.Stateless.__init__(self)
        self.settings = settings

def Client_Start(self, message):         # Start the networking.
    host = self.settings.host
    port = self.settings.port
    ipp = ar.HostPort(host, port)
    ar.connect(self, ipp, api_client='/', ansar_server=True)

def Client_Connected(self, message):
    settings = self.settings
    request = settings.request(settings.x, settings.y)

    def completed_1(response):       # What to do when transaction completes.
        self.complete(response)      # Terminate with the response as the output.

    a = self.create(ar.GetResponse, request, self.return_address)

    self.assign(a, ar.OnCompleted(completed_1))

def Client_Completed(self, message):
    d = self.debrief(self.return_address)
    if isinstance(d, ar.OnCompleted):
        d(message.value)

def Client_NotConnected(self, message):  # No networking.
    self.complete(message)

def Client_Stop(self, message):          # Control-c or software interrupt.
    self.abort(ar.Aborted())

# Declare the messages expected by the server object.
CLIENT_DISPATCH = [
    ar.Start,           # Initiate networking.
    ar.Connected,       # Ready to send.
    ar.Completed,
    ar.NotConnected,    # Networking failed.
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