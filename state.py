# Module to define the current state of the parser/interpreter

from collections import deque

class State:
    def __init__(self):
        # Stores the name and return type of current function being parsed
        self.current_function = None
        self.local_variables = {}
        
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

state = State()