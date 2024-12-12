# Module to define the current state of the parser/interpreter

from collections import deque

class Statement:
    def __init__(self, body_,):
        self.body = body_

class Variable:
    def __init__(self, type_, name_, value_: dict):
        self.type = type_
        self.name = name_
        self.value = value_
        self.address = self.allocate_mem()

    def __eq__(self, value: "Variable"):
        return self.name == value.name

    def __hash__(self):
        return hash(self.address)
    
    def __str__(self):
        return f"({self.type}, {self.name}, {self.value}, {self.address})"
    
    def allocate_mem(self):
        pass
    
class Literal:
    def __init__(self, type_, value_, negative_):
        self.type = type_
        self.value = value_
        self.negative = negative_

class Function:
    def __init__(self, type_, parameters_, body_):
        self.type = type_
        self.parameters = parameters_
        self.body = body_

class State:
    def __init__(self, memsize_: int):
        # Stores the name and return type of current function being parsed
        self.current_function = None
        self.local_variables = {}

        # Memory
        self.memory_size = memsize_
        self.memory = [0 for i in range(memsize_)]
        
        # Keeps track of order in which function calls were made
        self.call_stack = deque()

        # Stores the initial program instructions in the main function
        self.main_call = []

        self.functions = {}
        self.global_variables = {}

    def variable_lookup(self, name: str) -> dict:
        """ Returns the type and value of variable
        Args:
            name (str): Name of variable to lookup
        Returns:
            dict: {'type': <type>, 'value': <value>}
            None: If variable has not been declared or not in scope
        """
        # TODO: Handle local variables in different stack layers
        if name in self.local_variables:
            pass
        elif name in self.global_variables:
            return self.global_variables[name]

state = State(memsize_=1_000_000)