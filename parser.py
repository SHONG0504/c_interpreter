import ply.yacc as yacc
from collections import deque

# TODO: Add type checking to every production

"""
Stores states of variables
{ID: {'type': TYPE, 'value': <value of type>}}
"""
variables = {
    'global': {}
}

"""
Stores information of functions and local function stack
{ID: {'type': TYPE, 'variables': {<>}}}
"""
functions = {}

call_stack = deque()

main_call = []


precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE')
)

def p_program(p):
    """program : statements"""
    p[0] = p[1]

def p_statements(p):
    """statements : statement statements
                  | empty"""
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = [p[1]] + p[2]

def p_statement(p):
    """statement : declaration
                 | function_call SEMICOLON
                 | function_declaration
                 | function_definition
                 | return
                 | main"""
    # TODO
    p[0] = p[1]


def p_variable_declaration(p):
    """declaration : TYPE ID SEMICOLON
                   | TYPE ID ASSIGN literal SEMICOLON
                   | TYPE ID ASSIGN function_call SEMICOLON"""
    variables[p[2]] = {
        'type': p[1],
        'value': None
    }

    print(f"{variables}")
    p[0] = {
        'variable': p[2],
        'type': p[1],
        'value': None
    }

def p_literal(p):
    """literal : NUMBER
               | SINGLE_QUOTE CHAR SINGLE_QUOTE"""
    # TODO: Support other literal types
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_function_call(p):
    """function_call : ID L_ROUND arguments R_ROUND"""
    # TODO: finish this

    # print(f"{functions}")

    p[0] = {
        'type': functions[p[1]]['type'],
        'name': p[1],
        'arguments': p[3] if p[3] else None
    }

def p_arguments(p):
    """arguments : ID
                 | ID COMMA arguments
                 | empty"""
    if len(p) == 2:
        if p[1] is None:
            # No args
            p[0] = []
        else:
            # 1 arg
            p[0] = [p[1]]
    else:
        # Multiple args
        p[0] = [p[1]] + p[3]


# Rules to handle functions

def p_function_declaration(p):
    """function_declaration : function_prototype SEMICOLON"""

    global functions
    functions[p[1]['name']] = {
        'type': p[1]['type'],
        'parameters': p[1]['parameters']
    }

    p[0] = functions[p[1]['name']]

def p_function_definition(p):
    """function_definition : function_prototype L_CURLY statements R_CURLY"""

    global functions
    functions[p[1]['name']] = {
        'type': p[1]['type'],
        'parameters': p[1]['parameters'],
        'body': p[3]
    }

    p[0] = functions[p[1]['name']]

def p_function_prototype(p):
    """function_prototype : TYPE ID L_ROUND parameters R_ROUND"""

    p[0] = {
        'type': p[1],
        'name': p[2],
        'parameters': p[4] if p[4] else None
    }

def p_main(p):
    """main : TYPE MAIN L_ROUND parameters R_ROUND L_CURLY statements R_CURLY"""
    # Special case for function_definitions for main function
    global call_stack

    print(f"main: {len(p[7])} statements")
    for statement in p[7]:
        print(statement)


def p_parameters(p):
    """parameters : parameter COMMA parameters
                  | parameter
                  | empty"""
    if len(p) == 2:
        if p[1] is None:
            # No params
            p[0] = []
        else:
            # 1 param
            p[0] = [p[1]]
    else:
        # 2 or more params
        p[0] = [p[1]] + p[3]

def p_parameter(p):
    """parameter : TYPE ID"""
    p[0] = {'type': p[1], 'name': p[2]}

def p_return(p):
    """return : RETURN function_call SEMICOLON
              | RETURN ID SEMICOLON
              | RETURN literal SEMICOLON
              | RETURN SEMICOLON"""
    
    if len(p) == 4:
        p[0] = {
            'type': 'return',
            'value': p[2]
        }
    else:
        p[0] = {
            'type': 'return',
            'value': None
        }


def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Syntax error at ({p.value}, {p.type}), line {p.lineno}")
    else:
        print("Syntax error at EOF")
    exit(1)