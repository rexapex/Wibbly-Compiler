class SymbolTable:
    def __init__(self):
        self.globalScope = Scope()

class Decleration:
    def __init__(self, type):
        self.type = type

class Scope:
    def __init__(self):
        self.childScopes = []
        self.declerations = dict()
