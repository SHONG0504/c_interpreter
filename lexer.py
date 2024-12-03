import ply.lex as lex

# TODO: Add support for tokenizing double and single quote string literals
# TODO: Clean up ordering and organize by category

# TODO: After tokenization combine contiguous string
# TODO: Treat newline literal as string
# TODO: Figure out how to treat char array (string literals)


## State variables
read_string = 0
read_comment = 0
prev_token = None

ignore = [
    'SPACE',
    'SINGLE_LINE_COMMENT',
    'COMMENT_START', 'COMMENT_END',
    'COMMENT',
    'INCLUDE'
]

terminals = [
    'TYPE',
    'POINTER', 'ADDRESS', # *, &
    'SEMICOLON',
    'L_ROUND', 'R_ROUND',
    'L_SQUARE', 'R_SQUARE',
    'L_CURLY', 'R_CURLY',
    'L_POINTY', 'R_POINTY',
    'COMMA',
    'SINGLE_QUOTE', 'DOUBLE_QUOTE',
]

non_terminals = [
    'ID',
    'NUMBER',
    'FORMAT',
    'CHAR',
    'STRING',
    'NEWLINE_LITERAL',
    'LIBRARY',
]

# types = {
#     'void': 'VOID',
#     'int': 'INT',
#     'float': 'FLOAT',
#     'char': 'CHAR',
# }
types = ['void', 'int', 'float', 'char']

reserved_functions = [
    'print'
]

reserved = {
    'return': 'RETURN',
    'for': 'FOR',
    'while': 'WHILE',
    'if': 'IF',
    'else': 'ELSE',
}

comparison_operators = {
    '==': 'EQUALITY',
    '<': 'LT',
    '>': 'GT',
    '<=': 'LEQ',
    '>=': 'GEQ',
    '!=': 'INEQUALITY'
}

logical_operators = {
    '&&': 'LOGICAL_AND',
    '||': 'LOGICAL_OR',
    '!': 'NOT'
}

arithmetic_operators = {
    '+': 'PLUS',
    '-': 'MINUS',
    '++': 'INCREMENT',
    '--': 'DECREMENT',
    '*': 'MULTIPLY',
    '/': 'DIVIDE',
    '%': 'MODULO'
}

bitwise_operators = {
    '<<': 'BITSHIFT_L',
    '>>': 'BITSHIFT_R',
    '&': 'BITWISE_AND', # Can be address operator
    '|': 'BITWISE_OR',
    '^': 'XOR',
    '~': 'BITWISE_NOT'
}

assignment_operators = {
    '=': 'ASSIGN',
    '+=': 'PLUS_ASSIGN',
    '-=': 'MINUS_ASSIGN',
    '*=': 'MULTIPLY_ASSIGN',
    '/=': 'DIVIDE_ASSIGN',
    '%=': 'MODULO_ASSIGN',
    '<<=': 'BITSHIFT_L_ASSIGN',
    '>>=': 'BITSHIFT_R_ASSIGN'
}

operators = comparison_operators | \
    logical_operators | \
    arithmetic_operators | \
    bitwise_operators | \
    assignment_operators

brackets = {
    '(': 'L_ROUND',
    ')': 'R_ROUND',
    '[': 'L_SQUARE',
    ']': 'R_SQUARE',
    '{': 'L_CURLY',
    '}': 'R_CURLY',
    # '<': 'L_POINTY', # Not needed?
    # '>': 'R_POINTY'
}

string_formatter = {
    # https://cplusplus.com/reference/cstdio/printf/
    '%d': 'SIGNED_DEC_INT',
    '%f': 'LOWER_DEC_FLOAT',
}

tokens = list(reserved.values()) \
    + reserved_functions \
    + list(string_formatter.values()) \
    + ignore \
    + terminals + non_terminals \
    + list(operators.values())


def _typecheck(t):
    # Must call this function when processing token
    global prev_token
    if t.type in ignore:
        return None
    else:
        prev_token = t.type
        return t
    
def t_SINGLE_LINE_COMMENT(t):
    r'//.*\n'
    return _typecheck(t)

def t_COMMENT_START(t):
    r'\/\*'
    global read_comment

    if not read_comment:
        read_comment = 1
    return _typecheck(t)

def t_COMMENT_END(t):
    r'\*\/'
    global read_comment

    if read_comment:
        read_comment = 0
    return _typecheck(t)

def t_SEMICOLON(t):
    r';'

    if read_comment:
        t.type = 'COMMENT'
    elif read_string:
        t.type = 'STRING'
    return _typecheck(t)

def t_comparison_operators(t):
    r'(==|<(=)?|>(=)?|!=)'
    # ==, <, >, <=, >=, !=

    if t.value not in comparison_operators:
        print(f"{t.value} operator not in comparison_operators but matched regex.")
        exit(1)

    if read_comment:
        t.type = 'COMMENT'
    elif read_string:
        t.type = 'STRING'
    else:
        t.type = comparison_operators[t.value]
        
    return _typecheck(t)

def t_logical_operators(t):
    r'(&&|\|\||!)'
    # &&, ||, !

    if t.value not in logical_operators:
        print(f"{t.value} operator not in logical_operators but matched regex.")
        exit(1)

    if read_comment:
        t.type = 'COMMENT'
    elif read_string:
        t.type = 'STRING'
    else:
        t.type = logical_operators[t.value]
    return _typecheck(t)

def t_arithmetic_operators(t):
    r'((\+)?\+|(-)?-|\*|\/|%)'
    # +, -, ++, --, *, /

    if t.value not in arithmetic_operators:
        print(f"{t.value} operator not in arithmetic_operators but matched regex.")
        exit(1)

    if read_comment:
        t.type = 'COMMENT'
    elif read_string:
        t.type = 'STRING'
    elif t.value == '*':
        if prev_token in types:
            t.type = 'POINTER'
        else:
            t.type = 'MULTIPLY'
    else:
        t.type = arithmetic_operators[t.value]
    return _typecheck(t)

def t_bitwise_operators(t):
    r'(<<|>>|&|\||\^|~)'
    # <<, >>, &, |, ^, ~

    if t.value not in bitwise_operators:
        print(f"{t.value} operator not in bitwise_operators but matched regex.")
        exit(1)

    if read_comment:
        t.type = 'COMMENT'
    elif read_string:
        t.type = 'STRING'
    elif t.value == '&':
        if prev_token in types:
            t.type = 'ADDRESS'
        else:
            t.type = 'BITWISE_AND'
    else:
        t.type = bitwise_operators[t.value]
    return _typecheck(t)

def t_assignment_operators(t):
    r'([\+\-\*\/%]?=|<<=|>>=)'
    # =, +=, -=, *=, /=, %=, <<=, >>=

    if t.value not in assignment_operators:
        print(f"{t.value} operator not in assignment_operators but matched regex.")
        exit(1)

    if read_comment:
        t.type = 'COMMENT'
    elif read_string:
        t.type = 'STRING'
    else:
        t.type = assignment_operators[t.value]
    return _typecheck(t)
    
# t_COMMA = r'\,'
def t_COMMA(t):
    r','

    if read_comment:
        t.type = 'COMMENT'
    elif read_string:
        t.type = 'STRING'
    return _typecheck(t)

def t_brackets(t):
    r'(\(|\)|\[|\]|\{|\})'

    if t.value not in brackets:
        print(f"{t.value} invalid match in t_brackets")
        exit(1)

    if read_comment:
        t.type = 'COMMENT'
    elif read_string:
        t.type = 'STRING'
    else:
        t.type = brackets[t.value]
    return _typecheck(t)

def t_NEWLINE_LITERAL(t):
    r'\\n'

    if read_comment:
        t.type = 'COMMENT'
    elif read_string:
        t.type = 'STRING'
    return _typecheck(t)

def t_SPACE(t):
    r'[ ]+'

    if read_comment:
        t.type = 'COMMENT'
    elif read_string:
        t.type = 'STRING'
    else:
        t.type = 'SPACE'
    return _typecheck(t)

def t_INCLUDE(t):
    r'(^\s*\#\s*include\s*<([^<>]+)>)|(^\s*\#\s*include\s*"([^"]+)")'
    return _typecheck(t)

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'

    if read_comment:
        t.type = 'COMMENT'
    elif read_string:
        t.type = 'STRING'
    elif prev_token == 'SINGLE_QUOTE':
        if len(t.value) != 1:
            print(f"ERROR: {t.value} following single quote")
            exit(1)
        t.type = 'CHAR'
    elif t.value in types:
        t.type = 'TYPE'
    return _typecheck(t)

def t_NUMBER(t):
    r'\d+'

    if read_comment:
        t.type = 'COMMENT'
    elif read_string:
        t.type = 'STRING'
    elif prev_token == 'SINGLE_QUOTE':
        t.type = 'CHAR'
    else:
        t.value = int(t.value)
    return _typecheck(t)

def t_STAR(t):
    r'\*'
    if read_comment:
        t.type = 'COMMENT'
    elif read_string:
        t.type = 'STRING'
    elif prev_token == 'ID':
        t.type = 'MULTIPLY'
    elif prev_token == 'TYPE':
        t.type = 'POINTER'
    else:
        print("Invalid use of *")
        exit(1)
    return _typecheck(t)

def t_DOUBLE_QUOTE(t):
    r'\"'
    global read_comment, read_string
    
    if read_comment:
        t.type = 'COMMENT'
    elif read_string:
        read_string = 0
    else:
        read_string = 1
    return _typecheck(t)

def t_SINGLE_QUOTE(t):
    r'\''

    if read_comment:
        t.type = 'COMMENT'
    return _typecheck(t)
    
# def t_STRING(t):
#     r'\"(\\.|[^"\\])*\"'
#     return t


def t_FORMAT(t):
    r'\%[0 #+-]?[0-9*]*\.?\d*[hl]{0,2}[jztL]?[diuoxXeEfgGaAcpsSn%]'
    # TODO: Create dictionary for all format specifiers
    if read_comment:
        t.type = 'COMMENT'
    elif t.value in string_formatter:
        t.type = string_formatter[t.value]
    else:
        print(f"String formatter {t.value} not supported.")
        exit(1)
    return _typecheck(t)

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_eof(t):
    # TODO
    return None

def t_error(t):
    print(f"Illegal character '{t.value[0]} at line {t.lexer.lineno}'")
    exit(1)
