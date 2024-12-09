from state import *

# TODO: Add type checking to every production
# TODO: Ensure that function calls fail if called before function is declared/defined
# TODO: Add const variables
# TODO: Rename variable_list to avoid confusion with variable_declaration

# AST Dict Keys
INSTRUCTION = 'instruction'
NAME = 'name'
VALUE = 'value'
TYPE = 'type'
SIZE = 'size'
POINTER = 'pointer'
INDEX = 'index'
ARGUMENTS = 'arguments' # Input to function call
PARAMETERS = 'parameters' # Input definitions of function
BODY = 'body' # Instructions of a function
NEGATIVE = 'negative' # Indicates that evaluation result needs to be multiplied by -1

# Types of instructions
NOTHING = 'nothing'
RETURN = 'return'
VAR_LOOKUP = 'var_lookup'
FUNCTION_DECLARATION = 'function_declaration'
FUNCTION_DEFINITION = 'function_definition'
FUNCTION_CALL = 'function_call'
VARIABLE_DECLARATION = 'variable_declaration'
VARIABLE_ASSIGNMENT = 'variable_assignment'
OPERATION = 'operation'
MULTIPLY = 'multiply'
DIVIDE = 'divide'
ADD = 'add'
SUBTRACT = 'subtract'

L = 'left'
R = 'right'

""" Instruction handling
VAR_LOOKUP:
    {
        INSTRUCTION: VAR_LOOKUP,
        NAME: <name of variable>
    }
"""

precedence = (
    ('left', 'LT', 'GT', 'LEQ', 'GEQ'),
    ('left', 'EQ', 'NE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'NEGATIVE')
)

def p_program(p):
    """program : global_statements"""
    p[0] = p[1]

    print(f"{len(p[1])} global statements")
    for index, statement in enumerate(p[1]):
        print(f"\t{index}: {statement}")
        f = statement[NAME]
        t = statement[TYPE] if TYPE in statement else None
        v = statement[VALUE] if VALUE in statement else None
        p = statement[PARAMETERS] if PARAMETERS in statement else None
        b = statement[BODY] if BODY in statement else None
        i = statement[INSTRUCTION]

        if i == VARIABLE_DECLARATION:
            state.global_variables[f] = {
                TYPE: t,
                VALUE: v
            }
        elif i == VARIABLE_ASSIGNMENT:
            if f not in state.global_variables:
                print(f"Global variable {f} assigned before declaration.")
                exit(1)
            if v[TYPE] != state.global_variables[f][TYPE]:
                print(f"Incorrect type assignment ({v[TYPE]}) for variable {f} ({state.global_variables[f][TYPE]})")
                exit(1)
            state.global_variables[f][VALUE] = v
        elif i == FUNCTION_DECLARATION:
            # Functions do not need to be declared if defined before calling
            state.functions[f] = {
                TYPE: t,
                PARAMETERS: p,
            }
        elif i == FUNCTION_DEFINITION:
            if f in state.functions:
                if t != state.functions[f][TYPE]:
                    print(f"{f}: Type of declaration ({state.functions[f][TYPE]}) and definition ({t}) does not match.")
                    exit(1)
            state.functions[f] = {
                TYPE: t,
                PARAMETERS: p,
                BODY: b
            }


# Statements that occur outside of functions
def p_global_statements(p):
    """global_statements : global_statement global_statements
                         | empty"""
    if len(p) == 2:
        p[0] = []
    else:
        if type(p[1]) == list:
            p[0] = p[1] + p[2]
        else:
            p[0] = [p[1]] + p[2]
    

def p_global_statement(p):
    """global_statement : variable_declaration SEMICOLON
                        | variable_list SEMICOLON
                        | function_declaration SEMICOLON
                        | function_definition"""
    
    # Represents variables that were assigned to (thus not having a type statement as it was declared earlier)
    s = [{
        INSTRUCTION: VARIABLE_ASSIGNMENT if statement[VALUE] else NOTHING,
        NAME: statement[NAME],
        VALUE: statement[VALUE]
    } for statement in p[1] if not statement[TYPE]]

    p[0] = p[1] if not s else s

# Statements that occur inside functions
def p_function_statements(p):
    """function_statements : function_statement function_statements
                           | empty"""
    if len(p) == 2:
        p[0] = []
    else:
        if type(p[1]) == list:
            p[0] = p[1] + p[2]
        else:
            p[0] = [p[1]] + p[2]

def p_function_statement(p):
    """function_statement : variable_declaration SEMICOLON
                          | variable_assignment SEMICOLON
                          | function_call SEMICOLON
                          | printf SEMICOLON
                          | for_loop
                          | return SEMICOLON"""
    p[0] = p[1]


def p_variable_declaration(p):
    """variable_declaration : type variable_list"""

    p[0] = [
        var_info | {
            INSTRUCTION: VARIABLE_DECLARATION,
            TYPE: p[1]
        } for var_info in p[2]
    ]

def p_variable_list(p):
    """variable_list : ID
                     | ID ASSIGN expr
                     | ID COMMA variable_list
                     | ID ASSIGN expr COMMA variable_list
                     | pointer_declarator
                     | pointer_declarator ASSIGN pointer_initializer
                     | pointer_declarator COMMA variable_list
                     | pointer_declarator ASSIGN pointer_initializer COMMA variable_list"""
    # Line 4n: declare
    # Line 4n+1: assign
    # Line 4n+2: declare, variable_list
    # Line 4n+3: assign, variable_list
    # TODO: possible simplification for ID and pointer_declarator

    if type(p[1]) == str:
        # Non pointer
        if len(p) == 2:
            # ID
            p[0] = [{
                NAME: p[1],
                VALUE: None
            }]
        elif len(p) == 4:
            if p[2] == ',':
                # ID COMMA variables
                p[0] = [{
                    NAME: p[1],
                    VALUE: None
                }] + p[3]
            else:
                # ID ASSIGN expr
                p[0] = [{
                    NAME: p[1],
                    VALUE: p[3]
                }]
        else:
            # ID ASSIGN expr COMMA variable_list
            p[0] = [{
                NAME: p[1],
                VALUE: p[3]
            }] + p[5]
    else:
        # Pointer
        if len(p) == 2:
            # pointer_declarator
            p[0] = p[1] | {VALUE: None}
        elif len(p) == 4:
            if p[2] == ',':
                # pointer_declarator COMMA variable_list
                p[0] = [
                    p[1] | {
                        VALUE: None
                    }
                ] + p[3]
            else:
                # pointer_declarator ASSIGN pointer_initializer
                p[0] = [
                    p[1] | {
                        VALUE: p[3]
                    }
                ]
        else:
            # pointer_declarator ASSIGN pointer_initializer COMMA variable_list
            p[0] = [
                p[1] | {
                    VALUE: p[3]
                }
            ] + p[5]

def p_variable_assignment(p):
    """variable_assignment : variable_list"""

    p[0] = []
    for index, var_info in enumerate(p[1]):
        if type(var_info) == str:
            name = var_info
            value = None
        elif type(var_info) == dict:
            name = var_info[NAME]
            value = var_info[VALUE]
        else:
            print(f"Unknown format for {var_info}")
            exit(1)
        p[0].append({
            INSTRUCTION: VARIABLE_ASSIGNMENT,
            NAME: name,
            TYPE: None,
            VALUE: value
        })

def p_pointer_declarator(p):
    """pointer_declarator : POINTER ID
                          | ID array_size"""

    p[0] = {
        NAME: p[2] if p[1] == '*' else p[1],
        SIZE: None if p[1] == '*' else p[2]
    }

def p_pointer_initializer(p):
    """pointer_initializer : L_CURLY expr_list R_CURLY
                           | expr"""
    
    p[0] = p[2] if len(p) == 4 else p[1]

def p_array_size(p):
    """array_size : L_SQUARE expr R_SQUARE
                  | L_SQUARE R_SQUARE"""

    p[0] = p[2] if len(p) == 4 else None

def p_expr_list(p):
    """expr_list : expr expr_list_prime"""
    if p[2]:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_expr_list_prime(p):
    """expr_list_prime : COMMA expr expr_list_prime
                       | empty"""

    if p[1]:
        if p[3]:
            p[0] = [p[2]] + p[3]
        else:
            p[0]= [p[2]]


def p_expr(p):
    """expr : comp expr_prime"""

    if p[2] is not None:
        p[2][VALUE][L] = p[1]
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_expr_prime(p):
    """expr_prime : LT comp expr_prime
                  | GT comp expr_prime
                  | LEQ comp expr_prime
                  | GEQ comp expr_prime
                  | EQ comp expr_prime
                  | NE comp expr_prime
                  | empty"""
    
    if len(p) == 3:
        rnode = p[2]
        p[0] = p[1]
    elif len(p) == 4:
        rnode = p[2]
        if p[3] is not None:
            p[3][VALUE][L] = p[2]
            rnode = p[3]
        p[0] = {
            INSTRUCTION: p[1],
            VALUE: {
                L: None,
                R: rnode
            }
        }
    else:
        p[0] = None

def p_comp(p):
    """comp : term comp_prime"""

    if p[2] is not None:
        p[2][VALUE][L] = p[1]
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_comp_prime(p):
    """comp_prime : PLUS term comp_prime
                  | MINUS term comp_prime
                  | empty"""
    
    if len(p) == 3:
        rnode = p[2]
        p[0] = p[1]
    elif len(p) == 4:
        rnode = p[2]
        if p[3] is not None:
            p[3][VALUE][L] = p[2]
            rnode = p[3]
        p[0] = {
            INSTRUCTION: ADD if p[1] == '+' else SUBTRACT,
            VALUE: {
                L: None,
                R: rnode
            }
        }
    else:
        p[0] = None

def p_term(p):
    """term : factor term_prime"""

    if p[2] is not None:
        p[2][VALUE][L] = p[1]
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_term_prime(p):
    """term_prime : MULTIPLY factor term_prime
                  | DIVIDE factor term_prime
                  | empty"""

    if len(p) == 4:
        rnode = p[2]
        if p[3] is not None:
            p[3][VALUE][L] = p[2]
            rnode = p[3]
        p[0] = {
            INSTRUCTION: MULTIPLY if p[1] == '*' else DIVIDE,
            VALUE: {
                L: None,
                R: rnode
            }
        }      
    else:
        p[0] = None

def p_factor(p):
    """factor : ID
              | literal
              | function_call
              | L_ROUND expr R_ROUND
              | NEGATIVE factor"""
    
    if p[1] == '-':
        # NEGATIVE factor
        p[2][NEGATIVE] = True
        p[0] = p[2]
    else:
        if p[1] == '(':
            # L_ROUND expr R_ROUND
            p[0] = p[2]
        elif type(p[1]) == str:
            # ID
            p[0] = {
                NAME: p[1]
            }
        else:
            # literal
            # function_call
            p[0] = p[1]
        p[0][NEGATIVE] = False



    

def p_literal(p):
    """literal : INT
               | FLOAT
               | SINGLE_QUOTE CHAR SINGLE_QUOTE"""
    if len(p) == 2:
        p[0] = {
            TYPE: 'int' if type(p[1]) == int else 'float',
            VALUE: p[1],
        }
    else:
        if len(p[2]) == 1:
            p[0] = {
                TYPE: 'char',
                VALUE: p[2]
            }
        else:
            # Reserved for string literals
            pass

def p_function_call(p):
    """function_call : ID L_ROUND arguments R_ROUND"""

    p[0] = {
        INSTRUCTION: FUNCTION_CALL,
        NAME: p[1],
        ARGUMENTS: p[3]
    }

def p_arguments(p):
    """arguments : argument
                 | argument COMMA arguments
                 | empty"""
    if len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_argument(p):
    """argument : ID
                | ID L_SQUARE expr R_SQUARE
                | function_call"""
    p[0] = p[1]
    p[0] = {
        NAME: p[1],
        INDEX: p[3] if len(p) == 5 else None
    }


# Rules to handle functions

def p_function_declaration(p):
    """function_declaration : function_prototype"""

    p[0] = {
        INSTRUCTION: FUNCTION_DECLARATION,
        NAME: p[1][NAME],
        TYPE: p[1][TYPE],
        PARAMETERS: p[1][PARAMETERS]
    }

def p_function_definition(p):
    """function_definition : function_prototype L_CURLY function_statements R_CURLY"""

    local_variables = {}

    # Store passed arguments as local variables
    if p[1][PARAMETERS]:
        for parameter in p[1][PARAMETERS]:
            local_variables[parameter[NAME]] = {
                TYPE: parameter[TYPE],
                VALUE: None
            }

    p[0] = {
        INSTRUCTION: FUNCTION_DEFINITION,
        NAME: p[1][NAME],
        TYPE: p[1][TYPE],
        PARAMETERS: p[1][PARAMETERS],
        BODY: p[3]
    }

    # Check to see if return value type matches function type
    # Maybe remove this part (type checking should occur separately to parsing)
    return
    print(f"Parsing statements in {p[1][NAME]}")
    for index, statement in enumerate(p[3]):
        print(f"\tS{index}: {statement}")
        continue
        if statement[INSTRUCTION] == DECLARATION:
            local_variables[statement[NAME]] = {
                TYPE: statement[TYPE],
                VALUE: statement[VALUE]
            }
        if statement['instruction'] == 'return':
            if statement[TYPE] == 'id':
                # Lookup variable from table (hash map)
                if statement[VALUE] in local_variables:
                    statement[TYPE] = local_variables[statement[VALUE]][TYPE]
                elif statement[VALUE] in state.global_variables:
                    statement[TYPE] = state.global_variables[statement[VALUE]][TYPE]
                else:
                    print(f"Variable {statement[VALUE]} in function {p[1][NAME]} used before declaration.")
                    exit(1)
            if statement[TYPE] != p[1][TYPE]:
                print(f"Return type of function {p[1][NAME]} does not match.")
                exit(1)
            else:
                # print(f"Return type of function {p[1][NAME]} matches.")
                pass

    p[0] = {
        INSTRUCTION: FUNCTION_DEFINITION,
        NAME: p[1][NAME],
        TYPE: p[1][TYPE],
        PARAMETERS: p[1][PARAMETERS],
        BODY: p[3]
    }

def p_function_prototype(p):
    """function_prototype : type ID L_ROUND parameters R_ROUND"""

    p[0] = {
        TYPE: p[1],
        NAME: p[2],
        PARAMETERS: p[4]
    }

def p_parameters(p):
    """parameters : parameter COMMA parameters
                  | parameter
                  | empty"""
    # arguments but without the function_call
    if len(p) == 2:
        if p[1] is None:
            p[0] = None
        else:
            p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_parameter(p):
    """parameter : type ID
                 | type
                 | type POINTER ID
                 | type POINTER"""
    # TODO: split rules for function definition and declaration because declaration doesn're require parameter names
    if len(p) == 2:
        name = None
        pointer = False
    elif len(p) == 3:
        if p[2] == '*':
            name = None
            pointer = True
        else:
            name = p[2]
            pointer = False
    else:
        name = p[3]
        pointer = True

    p[0] = {
        TYPE: p[1],
        NAME: name,
        POINTER: pointer
    }

def p_printf(p):
    """printf : PRINTF L_ROUND DOUBLE_QUOTE printf_string DOUBLE_QUOTE printf_args R_ROUND"""
    print(f"Print: {p[4]}")

def p_printf_string(p):
    """printf_string : STRING
                     | string_format
                     | STRING printf_string_prime
                     | string_format printf_string_prime
                     | empty"""

def p_printf_string_prime(p):
    """printf_string_prime : STRING printf_string
                           | string_format printf_string"""

def p_string_format(p):
    """string_format : SIGNED_DEC_INT
                     | LOWER_DEC_FLOAT"""

def p_printf_args(p):
    """printf_args : COMMA arguments
                   | empty"""

def p_for_loop(p):
    """for_loop : FOR L_ROUND for_init SEMICOLON"""
    # """for_loop : FOR L_ROUND for_init SEMICOLON for_cond SEMICOLON for_update R_ROUND"""

def p_for_init(p):
    """for_init : for_init_statement for_init_prime
                | empty"""
    
def p_for_init_prime(p):
    """for_init_prime : COMMA for_init_statement for_init_prime
                      | empty"""

def p_for_init_statement(p):
    """for_init_statement : variable_declaration
                          | variable_assignment
                          | function_call
                          | printf"""

# def p_for_cond(p):
#     """for_cond : ID"""

# def p_for_update(p):
#     """for_update : ID"""



def p_return(p):
    """return : RETURN expr
              | RETURN"""

    p[0] = {
        INSTRUCTION: RETURN,
        VALUE: p[2] if len(p) == 3 else None
    }

def p_type(p):
    """type : TYPE_VOID
            | TYPE_INT
            | TYPE_FLOAT
            | TYPE_CHAR"""
    p[0] = p[1]


def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Syntax error at ({p.value}, {p.type}), line {p.lineno}")
    else:
        print("Syntax error at EOF")
    exit(1)