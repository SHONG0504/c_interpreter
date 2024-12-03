import ply.yacc as yacc

"""
Stores states of variables
{ID: {'type': TYPE, 'value': <value of type>}}
"""
variables = {}

"""
Stores information of functions and local function stack
{ID: {'type': TYPE, 'variables': {<>}}}
"""
functions = {}



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
                 | function_call SEMICOLON"""
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

    print(variables)
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
        if '.' in p[1]:
            p[0] = float(p[1])
        else:
            p[0] = int(p[1])
    else:
        p[0] = p[2]

def p_function_call(p):
    """function_call : ID L_ROUND arguments R_ROUND"""
    print(f"function_call: {p}")

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
def p_function_prototype(p):
    """function_prototype : TYPE ID L_ROUND"""

def p_function_definition(p):
    """"""

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


def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Syntax error at ({p.value}, {p.type}), line {p.lexpos}")
    else:
        print("Syntax error at EOF")
    exit(1)