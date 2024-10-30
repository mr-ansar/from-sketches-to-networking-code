import ansar.connect as ar

from component_api import *
from crunch_api import *

COMPONENT_API = [
    MulDiv,
    DivMul,
]

METERING_API = [
    ar.ApiUpdate,
    ar.ApiShow,
]

# The Component object.
class Component(ar.Point, ar.Stateless):
    def __init__(self, settings):
        ar.Point.__init__(self)
        ar.Stateless.__init__(self)
        self.settings = settings
        self.table = None
        self.group = None
        self.metering = None
        self.file = None

def Component_Start(self, message):
    self.file = ar.File("api-metering", ar.UserDefined(ar.ApiMetering), create_default=True)
    self.metering, _ = self.file.recover()

    crunch_ipp = self.settings.crunch
    public_ipp = self.settings.public
    private_ipp = self.settings.private

    self.table = ar.GroupTable(
        server_a=ar.CreateFrame(ar.ConnectToAddress, crunch_ipp, api_client='/', ansar_server=True),
        server_b=ar.CreateFrame(ar.ConnectToAddress, crunch_ipp, api_client='/', ansar_server=True),
        public=ar.CreateFrame(ar.ListenAtAddress, public_ipp, api_server=COMPONENT_API),
        private=ar.CreateFrame(ar.ListenAtAddress, private_ipp, api_server=METERING_API),
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
    self.file.store(self.metering)
    self.complete(ar.Aborted())

def Component_Stop(self, message):          # Control-c or software interrupt.
    self.send(message, self.group)

def Component_MulDiv(self, message):
    f = self.metering.out_of_service(message)
    if f:
        self.send(f, self.return_address)
        return

    f = ar.roll_call(self.table)
    if f:
        self.send(f, self.return_address)
        return

    m = self.metering.start_meter(message)
    if isinstance(m, ar.Faulted):
        self.send(m, self.return_address)
        return

    def begin(mul, div, server_a, server_b, return_address, m):
        a = self.create(ar.Concurrently,
            (mul, server_a),
            (div, server_b),
        )

        self.then(a, step_1, return_address, m)

    def step_1(response, return_address, m):
        value = response[0].value + response[1].value
        self.send(Output(value), return_address)
        self.metering.stop_meter(m, log=self)

    mul = Multiply(message.a, message.b)
    div = Divide(message.c, message.d)
    server_a = self.table.server_a
    server_b = self.table.server_b
    return_address = self.return_address

    begin(mul, div, server_a, server_b, return_address, m)

def Component_DivMul(self, message):
    f = self.metering.out_of_service(message)
    if f:
        self.send(f, self.return_address)
        return

    f = ar.roll_call(a=self.table.server_a, b=self.table.server_b)
    if f:
        self.send(f, self.return_address)
        return

    m = self.metering.start_meter(message)
    if isinstance(m, ar.Faulted):
        self.send(m, self.return_address)
        return

    def begin(div, mul, server_a, server_b, return_address, m):
        a = self.create(ar.Concurrently,
            (div, server_a),
            (mul, server_b),
        )

        self.then(a, step_1, return_address, m)

    def step_1(response, return_address, m):
        value = response[0].value + response[1].value
        self.send(Output(value), return_address)
        self.metering.stop_meter(m, log=self)

    div = Divide(message.a, message.b)
    mul = Multiply(message.c, message.d)

    server_a = self.table.server_a
    server_b = self.table.server_b
    return_address = self.return_address

    begin(div, mul, server_a, server_b, return_address, m)

def Component_ApiUpdate(self, message):
    if self.metering.update(message):
        self.file.store(self.metering)
    self.reply(ar.Ack())

def Component_ApiShow(self, message):
    self.reply(self.metering.report(message.request_type))

# Declare the messages expected by the component.
COMPONENT_DISPATCH = [
    ar.Start,
    ar.GroupUpdate,
    ar.Completed,
    ar.Stop,
    COMPONENT_API,
    METERING_API,
]

ar.bind(Component, COMPONENT_DISPATCH)

# Configuration for this executable.
class Settings(object):
    def __init__(self, crunch=None, public=None, private=None):
        self.crunch = crunch or ar.HostPort()
        self.public = public or ar.HostPort()
        self.private = private or ar.HostPort()

SETTINGS_SCHEMA = {
    'crunch': ar.UserDefined(ar.HostPort),
    'public': ar.UserDefined(ar.HostPort),
    'private': ar.UserDefined(ar.HostPort),
}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)

# Define default configuration and start the server.
factory_settings = Settings(crunch=ar.HostPort('127.0.0.1', 5051),
    public=ar.HostPort('0.0.0.0', 5052),
    private=ar.HostPort('127.0.0.1', 5053),
)

if __name__ == '__main__':
    ar.create_object(Component, factory_settings=factory_settings)
