import os, sys
import ply
import graphviz

from lexer import *
from parser import *

class Interpreter:
    def __init__(self, fpath: str):
        self.fpath = fpath
        with open(fpath, 'r') as f:
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

    def generate_flow_graph(self):
        pass

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

if __name__ == "__main__":
    argc = len(sys.argv)
    if (argc == 2):
        main(fpath=sys.argv[1])
    else:
        main(fpath=os.path.abspath("./example.c"))