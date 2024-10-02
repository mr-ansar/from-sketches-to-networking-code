import ansar.connect as ar

from crunch_api import *

CRUNCH_API = [
    Multiply,
    Divide,
]

# The server object.
class Server(ar.Point, ar.Stateless):
    def __init__(self, settings):
        ar.Point.__init__(self)
        ar.Stateless.__init__(self)
        self.settings = settings

def Server_Start(self, message):         # Start the networking.
    host = self.settings.host
    port = self.settings.port
    ipp = ar.HostPort(host, port)
    ar.listen(self, ipp, api_server=CRUNCH_API)

def Server_NotListening(self, message):  # No networking.
    self.complete(message)

def Server_Stop(self, message):          # Control-c or software interrupt.
    self.complete(ar.Aborted())

def Server_Multiply(self, message):      # Received Multiply.
    value = message.x * message.y
    response = Output(value=value)
    self.reply(response)

def Server_Divide(self, message):        # Received Divide.
    value = message.x / message.y
    response = Output(value=value)
    self.reply(response)

# Declare the messages expected by the server object.
SERVER_DISPATCH = [
    ar.Start,           # Initiate networking.
    ar.NotListening,    # Networking failed.
    ar.Stop,            # Ctrl-c or programmed interrupt.
    CRUNCH_API,       # Network API.
]

ar.bind(Server, SERVER_DISPATCH)

# Configuration for this executable.
class Settings(object):
    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port

SETTINGS_SCHEMA = {
    'host': str,
    'port': int,
}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)

# Define default configuration and start the server.
factory_settings = Settings(host='127.0.0.1', port=5051)

if __name__ == '__main__':
    ar.create_object(Server, factory_settings=factory_settings)
