#-----------------------------------------------------------------------
# sddgen: datarep.py
#-----------------------------------------------------------------------
from .model import Node, Model

class Types(Node):
    def __init__(self, node):
        super().__init__(node.value, node.key)
        pass

class TypeDef(Node):
    def __init__(self, node):
        super().__init__(node.value, node.key)
        pass

