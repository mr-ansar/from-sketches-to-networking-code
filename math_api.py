import ansar.encode as ar

__all__ = [
    'Multiply',
    'Divide',
    'Output',
]

class Multiply(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

class Divide(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

class Output(object):
    def __init__(self, value=0.0):
        self.value = value

ar.bind(Multiply)
ar.bind(Divide)
ar.bind(Output)