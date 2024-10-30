import ansar.encode as ar

from crunch_api import Output

__all__ = [
 'MulDiv',
 'DivMul',
]

# Declare the API.
class MulDiv(object):
    def __init__(self, a=0.0, b=0.0, c=0.0, d=0.0):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

class DivMul(object):
    def __init__(self, a=0.0, b=0.0, c=0.0, d=0.0):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

ar.bind(MulDiv)
ar.bind(DivMul)
