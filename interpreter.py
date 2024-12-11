import os, sys
import ply
import graphviz
import json

import ply.lex as lex
import ply.yacc as yacc

from lexer import *
from parser import *

class Interpreter:
    def __init__(self, fpath: str):
        self.fpath = os.path.abspath(fpath)
        with open(self.fpath, 'r') as f:
            self.filedata = f.read()
        self.lexer = None
        self.parser = None
        self.state = state # from parser.py

    def tokenize(self, debug=False):
        self.lexer: lex.Lexer = lex.lex(
            debug=debug
        )
        self.lexer.input(self.filedata)
    
    def generate_ast(self, debug=0):
        self.parser = yacc.yacc(
            debug=debug
        )
        self.parser.parse(self.filedata, self.lexer)
        return

        print(f"{len(state.global_variables)} Global Variables:")
        print(json.dumps(state.global_variables, indent=4))
        print(f"\n\n{len(state.functions)} Functions:")
        print(json.dumps(state.functions, indent=4))


    def evaluate_ast(self, ast: dict | None, scope: dict | list[dict] = None) -> dict:
        # TODO: Implement type checking
        if ast is None:
            return None
        
        # Load variables in scope
        scope_list : list[dict] = []
        if scope:
            if type(scope) == dict:
                scope_list.append(scope)
            else:
                for s in scope:
                    scope_list.append(s)

        if type(ast[VALUE]) == dict:
            if ast[INSTRUCTION] == FUNCTION_CALL:
                return self.evaluate_function_call(ast, scope_list)
            elif ast[INSTRUCTION] == VAR_LOOKUP:
                return self.evaluate_var_lookup(ast, scope_list)
            elif ast[INSTRUCTION] in [
                ADD, SUBTRACT, MULTIPLY, DIVIDE, '<', '>', '<=', '>=', '==', '!='
            ]:
                left = self.evaluate_ast(ast[VALUE][L], scope_list)
                right = self.evaluate_ast(ast[VALUE][R], scope_list)

                if ast[INSTRUCTION] == ADD:
                    return {
                        TYPE: type(left[VALUE] + right[VALUE]).__name__,
                        VALUE: left[VALUE] + right[VALUE]}
                elif ast[INSTRUCTION] == SUBTRACT:
                    return {
                        TYPE: type(left[VALUE] + right[VALUE]).__name__,
                        VALUE: left[VALUE] - right[VALUE]}
                elif ast[INSTRUCTION] == MULTIPLY:
                    return {
                        TYPE: type(left[VALUE] + right[VALUE]).__name__,
                        VALUE: left[VALUE] * right[VALUE]}
                elif ast[INSTRUCTION] == DIVIDE:
                    if right[VALUE] == 0:
                        raise ZeroDivisionError
                    return {
                        TYPE: type(left[VALUE] / right[VALUE]).__name__,
                        VALUE: left[VALUE] / right[VALUE]}
                elif ast[INSTRUCTION] == '<':
                    return {
                        TYPE: 'int',
                        VALUE: 1 if left[VALUE] < right[VALUE] else 0}
                elif ast[INSTRUCTION] == '>':
                    return {
                        TYPE: 'int',
                        VALUE: 1 if left[VALUE] > right[VALUE] else 0}
                elif ast[INSTRUCTION] == '<=':
                    return {
                        TYPE: 'int',
                        VALUE: 1 if left[VALUE] <= right[VALUE] else 0}
                elif ast[INSTRUCTION] == '>=':
                    return {
                        TYPE: 'int',
                        VALUE: 1 if left[VALUE] >= right[VALUE] else 0}
                elif ast[INSTRUCTION] == '==':
                    return {
                        TYPE: 'int',
                        VALUE: 1 if left[VALUE] == right[VALUE] else 0}
                elif ast[INSTRUCTION] == '!=':
                    return {
                        TYPE: 'int',
                        VALUE: 1 if left[VALUE] != right[VALUE] else 0}
            else:
                err = f"{ast[INSTRUCTION]} not processed yet"
                raise Exception(err)
        else:
            # Leaf node
            if NEGATIVE not in ast:
                ast[NEGATIVE] = False
            elif ast[NEGATIVE]:
                ast[VALUE] = -ast[VALUE]
                ast[NEGATIVE] = False
            return ast

    def interpret(self):
        print("\n\nStarting interpreter:\n")

        # Initialize and evaluate global variables
        for var_name, gv in self.state.global_variables.items():
            # Evaluate AST
            if gv[VALUE] is None:
                # Variable declared but no value assigned
                continue

            arr_eval = []
            if gv[POINTER]:
                if gv[VALUE] is not None:
                    for ast in gv[VALUE]:
                        arr_eval.append(self.evaluate_ast(ast))
            elif type(gv[VALUE]) == list:
                for ast in gv[VALUE]:
                    arr_eval.append(self.evaluate_ast(ast))
            elif type(gv[VALUE]) == dict:
                arr_eval.append(self.evaluate_ast(gv[VALUE]))
            else:
                raise Exception("Something is wrong")

        if "main" not in state.functions:
            print("Main function does not exist.")
            return
        
        # Start interpretation from main()
        print("Starting main:\n")
        main_variables = {}
        for statement in self.state.functions['main']['body']:
            self.handle_statement(statement, main_variables)

    def handle_statement(self, statement: dict, scope: dict | list[dict]):
        if statement[INSTRUCTION] == VARIABLE_DECLARATION:
            self.evaluate_variable_declaration(statement, scope)
        elif statement[INSTRUCTION] == VARIABLE_ASSIGNMENT:
            self.evaluate_variable_assignment(statement, scope)
        elif statement[INSTRUCTION] == FOR_LOOP:
            # Initialize local variables
            local_fl_vars = {}
            local_fl_vars.update(scope)
            for var in statement[INIT]:
                # If variable is declared inside for loop, the scope is only to that for loop
                if var[INSTRUCTION] == VARIABLE_DECLARATION:
                    self.evaluate_variable_declaration(var, local_fl_vars)
                elif var[INSTRUCTION] == VARIABLE_ASSIGNMENT:
                    self.evaluate_variable_assignment(var, [scope, local_fl_vars])

            # Evaluate condition statement
            while self.evaluate_ast(statement[COND], [scope, local_fl_vars])[VALUE]:
                # Evaluate for loop body until condition is met
                for f_statement in statement[BODY]:
                    self.handle_statement(f_statement, [scope, local_fl_vars])

                # Evaluate update block at end of for loop
                for f_update_statement in statement[UPDATE]:
                    self.handle_statement(f_update_statement, [scope, local_fl_vars])
      
        elif statement[INSTRUCTION] == IF:
            cond = self.evaluate_ast(statement[COND], scope)
            if cond[VALUE]:
                # Run body statements if conditions are met
                for b_statement in statement[BODY]:
                    self.handle_statement(b_statement, scope)
        elif statement[INSTRUCTION] == PRINT:
            self.evaluate_print(statement, scope)
        elif statement[INSTRUCTION] in [
            ADD, SUBTRACT, MULTIPLY, DIVIDE, '<', '>', '<=', '>=', '==', '!='
        ]:  
            statement = self.evaluate_ast(statement, scope)
        elif statement[INSTRUCTION] == FUNCTION_CALL:
            return self.evaluate_function_call(statement, scope)
        elif statement[INSTRUCTION] == RETURN:
            r_val = self.evaluate_ast(statement[VALUE], scope)
            print(f"return({r_val[VALUE]})")
            return r_val
        else:
            err = f"\t{statement[INSTRUCTION]} not ready"
            raise Exception(err)
    
    def evaluate_var_lookup(self, statement: dict, scope : dict | list[dict] = None):
        if type(scope) == dict:
            scope_list = [scope]
        else:
            scope_list = scope

        for s in scope_list:
            if statement[VALUE][NAME] in s:
                if statement[VALUE][INDEX] is not None:
                    return s[statement[VALUE][NAME]][VALUE][self.evaluate_ast(statement[VALUE][INDEX], scope)[VALUE]]
                return s[statement[VALUE][NAME]][VALUE]
        if statement[VALUE][NAME] in self.state.global_variables:
            if statement[VALUE][INDEX] is not None:
                return self.state.global_variables[statement[VALUE][NAME]][VALUE][self.evaluate_ast(statement[VALUE][INDEX], scope)[VALUE]]
            return self.state.global_variables[statement[VALUE][NAME]][VALUE]
        else:
            err = f"{statement[VALUE][NAME]} assigned before declaration."
            raise Exception(err)

    def evaluate_variable_declaration(self, statement: dict, scope: dict = None):

        if statement[POINTER]:
            size = self.evaluate_ast(statement[SIZE], scope)
            if statement[SIZE]:
                # Processes shortcuts: int a[5] = {0};
                if size[VALUE] > len(statement[VALUE]):
                    # Initializes an array of 0s
                    v = [{
                        TYPE: 'int',
                        VALUE: 0,
                        NEGATIVE: False
                    } for i in range(size[VALUE])]
                    for i in range(len(statement[VALUE])):
                        v[i] = self.evaluate_ast(statement[VALUE][i], scope)
                else:
                    v = [self.evaluate_ast(ast, scope) for ast in statement[VALUE]]
            scope[statement[NAME]] = {
                TYPE: statement[TYPE],
                POINTER: True,
                SIZE: size if size else {
                    TYPE: 'int',
                    VALUE: len(v),
                    NEGATIVE: False
                },
                VALUE: v
            }
        else:
            # Non pointer variable declarations
            scope[statement[NAME]] = {
                TYPE: statement[TYPE],
                POINTER: False,
                VALUE: self.evaluate_ast(statement[VALUE], scope)
            }

    def evaluate_variable_assignment(self, statement: dict, scope : dict | list[dict] = None):
        if type(scope) == dict:
            scope_list = [scope]
        else:
            scope_list = scope

        v = self.evaluate_ast(statement[VALUE], scope)

        for s in scope_list:
            if statement[NAME] in s:
                if s[statement[NAME]][POINTER]:
                    # When assigning arrays, treat SIZE as index
                    # Evaluate index
                    index = self.evaluate_ast(statement[SIZE], scope)

                    # Assign value at array index
                    s[statement[NAME]][VALUE][index[VALUE]] = v
                else:
                    s[statement[NAME]][VALUE] = v
                break
        else:
            if statement[NAME] in self.state.global_variables:
                self.state.global_variables[statement[NAME]][VALUE] = v
            else:
                err = f"{statement[NAME]} assigned before declaration."
                raise Exception(err)
    
    def evaluate_function_call(self, statement: dict, scope: dict | list[dict]) -> dict:
        # Input scope only required when evaluating arguments
        if type(scope) == dict:
            scope_list = [scope]
        else:
            scope_list = scope

        f_name = statement[VALUE][NAME]

        # Print function call to output
        print(f"{f_name}(", end="")
        # Initialize local variables from arguments
        var_list = []
        for i, arg in enumerate(statement[VALUE][ARGUMENTS]):
            evaluated = self.evaluate_ast(arg, scope)
            var_list.append(evaluated)
            if type(evaluated) == dict:
                print(f"{evaluated[VALUE]}", end="")
                if i < len(statement[VALUE][ARGUMENTS]) - 1:
                    print(", ", end="")
            else:
                print("[", end="")
                for j, e in enumerate(evaluated):
                    print(f"{e[VALUE]}", end="")
                    if j < len(evaluated) - 1:
                        print(", ", end="")
                print("]", end="")
                if i < len(statement[VALUE][ARGUMENTS]) - 1:
                    print(", ", end="")
        print(")")

        function_scope = {param[NAME]: {
            TYPE: param[TYPE],
            POINTER: param[POINTER],
            VALUE: var_list[index]
        } for index, param in enumerate(self.state.functions[f_name][PARAMETERS])}

        # Evaluate statements in function
        for s in self.state.functions[statement[VALUE][NAME]]['body']:
            r_val = self.handle_statement(s, function_scope)
            if s[INSTRUCTION] == RETURN:
                return r_val
        

    def evaluate_print(self, statement: dict, scope: dict | list[dict]):
        print(f"print(\"", end="")
        for string in statement[VALUE]:
            if type(string) == str:
                print(string, end="")
            else:
                print(string[TYPE], end="")
        print("\", ", end="")
        for index, arg in enumerate(statement[ARGUMENTS]):
            val = self.evaluate_ast(arg, scope)
        
            # Search variable from arg
            print(f"{val[VALUE]}", end="")

            if index < len(statement[ARGUMENTS]) - 1:
                print(", ", end="")
        print(")")

                

    def generate_asm(self):
        pass

    def print_tokens(self):
        while True:
            token = self.lexer.token()
            if not token:
                break
            print(f"{token.type} {token.value} {token.lineno}")

    def print_memory(self, file: str = None):
        """Prints state of internal memory when called"""
        if not file:
            for index, byte in enumerate(self.state.memory):
                if (index % 8 == 0) and (index):
                    print("\t", end="")
                if (index % 16 == 0) and (index):
                    print("")
                print(byte, end=" ")
        else:
            with open(file, 'w') as f:
                for index, byte in enumerate(self.state.memory):
                    if (index % 8 == 0) and (index):
                        f.write("\t")
                    if (index % 16 == 0) and (index):
                        f.write("\n")
                    f.write(f"{byte} ")



def main(fpath: str) -> None:
    interpreter = Interpreter(fpath)
    interpreter.tokenize()
    # interpreter.print_tokens()
    interpreter.print_memory(file="mem.txt")
    interpreter.generate_ast(debug=True)
    interpreter.interpret()

if __name__ == "__main__":
    argc = len(sys.argv)
    if (argc == 2):
        main(fpath=sys.argv[1])
    else:
        # main(fpath=f"{os.path.dirname(__file__)}/examples/e1.c")
        main(fpath=f"{os.path.dirname(__file__)}/example.c")