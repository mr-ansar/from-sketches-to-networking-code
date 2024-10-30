import ansar.connect as ar

from component_api import *
from crunch_api import *

COMPONENT_API = [
    MulDiv,
    DivMul,
]

# The Component object.
class Component(ar.Point, ar.Stateless):
    def __init__(self, settings):
        ar.Point.__init__(self)
        ar.Stateless.__init__(self)
        self.settings = settings
        self.table = None
        self.group = None

def Component_Start(self, message):         # Start the networking.
    crunch_ipp = self.settings.crunch
    public_ipp = self.settings.public

    self.table = ar.GroupTable(
        server_a=ar.CreateFrame(ar.ConnectToAddress, crunch_ipp, api_client='/', ansar_server=True),
        server_b=ar.CreateFrame(ar.ConnectToAddress, crunch_ipp, api_client='/', ansar_server=True),
        public=ar.CreateFrame(ar.ListenAtAddress, public_ipp, api_server=COMPONENT_API),
    )
    self.group = self.table.create(self)

def Component_GroupUpdate(self, message):
    self.table.update(message)

def Component_Completed(self, message):
    d = self.debrief(self.return_address)
    if isinstance(d, ar.OnCompleted):
        d(message.value)
        return

    # Table has terminated.
    self.complete(ar.Aborted())

def Component_Stop(self, message):          # Control-c or software interrupt.
    self.send(message, self.group)

def Component_MulDiv(self, message):
    f = ar.roll_call(self.table)
    if f:
        self.send(f, self.return_address)
        return

    def begin(mul, div, server_a, server_b, return_address):
        a = self.create(ar.Concurrently,
            (mul, server_a),
            (div, server_b),
        )

        self.then(a, step_1, return_address)

    def step_1(response, return_address):
        value = response[0].value + response[1].value
        self.send(Output(value), return_address)

    mul = Multiply(message.a, message.b)
    div = Divide(message.c, message.d)
    server_a = self.table.server_a
    server_b = self.table.server_b
    return_address = self.return_address

    begin(mul, div, server_a, server_b, return_address)

def Component_DivMul(self, message):
    f = ar.roll_call(a=self.table.server_a, b=self.table.server_b)
    if f:
        self.send(f, self.return_address)
        return

    def begin(div, mul, server_a, server_b, return_address):
        a = self.create(ar.Concurrently,
            (div, server_a),
            (mul, server_b),
        )

        self.then(a, step_1, return_address)

    def step_1(response, return_address):
        value = response[0].value + response[1].value
        self.send(Output(value), return_address)

    div = Divide(message.a, message.b)
    mul = Multiply(message.c, message.d)

    server_a = self.table.server_a
    server_b = self.table.server_b
    return_address = self.return_address

    begin(div, mul, server_a, server_b, return_address)

# Declare the messages expected by the server object.
COMPONENT_DISPATCH = [
    ar.Start,
    ar.GroupUpdate,
    ar.Completed,
    ar.Stop,
    COMPONENT_API,
]

ar.bind(Component, COMPONENT_DISPATCH)

# Configuration for this executable.
class Settings(object):
    def __init__(self, crunch=None, public=None):
        self.crunch = crunch or ar.HostPort()
        self.public = public or ar.HostPort()

SETTINGS_SCHEMA = {
    'crunch': ar.UserDefined(ar.HostPort),
    'public': ar.UserDefined(ar.HostPort),
}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)

# Define default configuration and start the server.
factory_settings = Settings(crunch=ar.HostPort('127.0.0.1', 5051),
    public=ar.HostPort('127.0.0.1', 5052),
)

if __name__ == '__main__':
    ar.create_object(Component, factory_settings=factory_settings)
