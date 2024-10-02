import ansar.connect as ar

from crunch_api import *


# The client object.
class INITIAL: pass
class STARTING: pass
class RUNNING: pass
class CLEARING: pass

class Client(ar.Point, ar.StateMachine):
    def __init__(self, settings):
        ar.Point.__init__(self)
        ar.StateMachine.__init__(self, INITIAL)
        self.settings = settings
        self.table = None
        self.group = None
        self.response_value = None

def Client_INITIAL_Start(self, message):
    host = self.settings.host
    port = self.settings.port
    ipp = ar.HostPort(host, port)

    self.table = ar.GroupTable(
        server_a=ar.CreateFrame(ar.ConnectToAddress, ipp, api_client='/', ansar_server=True),
        server_b=ar.CreateFrame(ar.ConnectToAddress, ipp, api_client='/', ansar_server=True),
    )
    self.group = self.table.create(self)
    return STARTING

def Client_STARTING_GroupUpdate(self, message):
    self.table.update(message)
    return STARTING

def Client_STARTING_Ready(self, message):
    settings = self.settings
    request = settings.request(settings.x, settings.y)

    a = self.create(ar.Concurrently,
        (Divide(4.0, 2.0), self.table.server_a),
        (request, self.table.server_b),
    )
    def step_1(response):
        self.response_value = response[1]
        self.send(ar.Stop(), self.group)
        return CLEARING

    self.assign(a, ar.OnCompleted(step_1))
    return RUNNING

def Client_STARTING_Stop(self, message):
    self.response_value = ar.Aborted()
    self.send(ar.Stop(), self.group)
    return CLEARING

def Client_STARTING_Completed(self, message):
    self.complete(message)

def Client_RUNNING_Completed(self, message):
    d = self.debrief(self.return_address)
    if isinstance(d, ar.OnCompleted):
        return d(message.value)
    self.complete(message.value)

def Client_RUNNING_Stop(self, message):
    self.abort(ar.Aborted())

def Client_CLEARING_Completed(self, message):
    self.complete(self.response_value)

# Declare the messages expected by the server object.
CLIENT_DISPATCH = {
    INITIAL: (
        (ar.Start,), ()
    ),
    STARTING: (
        (ar.GroupUpdate, ar.Ready, ar.Stop, ar.Completed), ()
    ),
    RUNNING: (
        (ar.Completed, ar.Stop), ()
    ),
    CLEARING: (
        (ar.Completed,), ()
    ),
}

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