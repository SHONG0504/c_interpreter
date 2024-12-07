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

        print(f"{len(state.global_variables)} Global Variables:")
        print(json.dumps(state.global_variables, indent=4))
        print(f"\n\n{len(state.functions)} Functions:")
        print(json.dumps(state.functions, indent=4))
        return

    def generate_flow_graph(self):
        # if 'main' in state.functions:
        #     print(f"main: {state['main']['body']}")
        pass

    def interpret(self):
        print("Start of program")
        if not state.main_call:
            print("There is nothing to run")
            return

        for inum, statement in enumerate(state.main_call):
            print(f"{inum}: {statement}")

    def generate_asm(self):
        pass

    def print_tokens(self):
        while True:
            token = self.lexer.token()
            if not token:
                break
            print(f"{token.type} {token.value} {token.lineno}")



def main(fpath: str) -> None:
    interpreter = Interpreter(fpath)
    interpreter.tokenize()
    interpreter.print_tokens()
    interpreter.generate_ast(debug=True)
    interpreter.generate_flow_graph()
    # interpreter.interpret()

if __name__ == "__main__":
    argc = len(sys.argv)
    if (argc == 2):
        main(fpath=sys.argv[1])
    else:
        main(fpath=f"{os.path.dirname(__file__)}/examples/e1.c")