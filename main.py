'''
import re
from typing import NamedTuple

# class LexType(NamedTuple):
#     LEX_NULL: str
#     # КЛЮЧЕВЫЕ СЛОВА
#     LEX_INT: str
#     LEX_FLOAT: str
#     LEX_BOOL: str
#     #ОПЕРАТОРЫ И РАЗДЕЛИТЕЛИ
#     LEX_PLUS: str
#     LEX_MINUS: str
#     LEX_SLASH: str
#     LEX_TIMES: str
#     LEX_EQ: str
#     LEX_LESS: str
#     LEX_GREAT: str
#     LEX_LEQ: str
#     LEX_GEQ: str
#     LEX_NEQ: str
#     LEX_NOT: str
#     LEX_AND: str
#     LEX_OR: str



class States(NamedTuple):
    H: str
    ID: str
    NUM: str
    DLM: str
    COMM: str
    OPER: str
    ERR: str


class Tokens(NamedTuple):
    KWORD: str
    IDENT: str
    NUM: str
    OPER: str
    DELIM: str
    NUM2: str
    NUM8: str
    NUM10: str
    NUM16: str
    REAL: str
    TYPE: str
    ARITH: str

class Lex:
    def __init__(self, lex_type:str, lex_value:str, line:int):
        self.lex_type = lex_type
        self.lex_value = lex_value
        self.line = line

    def toString(self):
        return f"{self.lex_type}, {self.lex_value}"
    def getType(self):
        return self.lex_type
    def getValue(self):
        return self.lex_value
    def getLine(self):
        return self.line
class Ident:
    def __init__(self, lex: Lex, declared: bool, assigned: bool):
        self.lex = lex
        self.declared = declared
        self.assigned = assigned

    def getType(self):
        return self.id_type
    def isDeclared(self):
        return self.declared
    def isAssigned(self):
        return self.assigned
    def lex_type(self):
        return self.lex.getType()
    def lex_value(self):
        return self.lex.getValue()
    def lex_line(self):
        return self.lex.getLine()

class LexicalAnalyser:

    def __init__(self, filename: str):
        self.token_names = {
            "KWORD": "KWORD",
            "IDENT": "IDENT",
            "OPER": "OPER",
            "DELIM": "DELIM",
            "TYPE": "TYPE",
            "ARITHM": "ARITHM",
            "INT_2": "INT_2",
            "INT_8": "INT_8",
            "INT_10": "INT_10",
            "INT_16": "INT_16",
            "REAL": "REAL"
        }
        self.states = {
            "H" : "H",
            "WORD" : "WORD",
            "NUM" : "NUM",
            "DLM" : "DLM",
            "COMM" : "COMM",
            "OPER" : "OPER",
            "ERR" : "ERR"
        }

        self.keywords = {"begin": 1, "end": 2, "if": 3, "else": 4, "for": 5, "to": 6,
                         "step": 7, "next": 8, "while": 9, "readln": 10, "writeln": 11,
                         "true": 12, "false" : 13}
        self.types = {"%", "!", "$"}  # +
        self.arithmetic = {"+", '-', '*', '/',  "||", "&&" }
        self.delimiters = {";", ",", "[", "]", "(", ")", "{", "}", "/"}
        self.operators = {":", ":=", "=", "==", "!", "!=", "<", "<=", ">", ">=", }

        self.lexeme_list = []
        self.id_list = []
        self.eof_state = False
        self.current_state = self.states["H"]
        self.symbol = ""
        self.err_lex = ""
        self.line = 0
        self.fgetc = self.fgetc_generator(filename)

    def getLexeme(self):
        self.current_state = self.states["H"]
        self.err_lex = ""
        if self.symbol == "" and not self.eof_state:
            self.symbol, self.eof_state, self.line = next(self.fgetc)
        while not self.eof_state:
            if self.current_state == self.states["H"]:
                while not self.eof_state and self.symbol in {" ", "\n", "\t", ""}:
                    self.symbol, self.eof_state, self.line = next(self.fgetc)
                if self.symbol.isalpha():
                    self.current_state = self.states["WORD"]
                elif self.symbol.isdigit():
                    self.current_state = self.states["NUM"]
                elif self.symbol in (self.delimiters | self.arithmetic | self.types):
                    self.current_state = self.states["DLM"]
                elif self.symbol in self.operators:
                    self.current_state = self.states["OPER"]
                else:
                    self.current_state = self.states["ERR"]


            elif self.current_state == self.states["WORD"]:
                buf = [self.symbol]
                if not self.eof_state:
                    self.symbol, self.eof_state, self.line = next(self.fgetc)
                else:
                    break

                while not self.eof_state and (self.symbol.isalpha() or self.symbol.isdigit()):
                    buf.append(self.symbol)
                    self.symbol, self.eof_state, self.line = next(self.fgetc)
                buf = ''.join(buf)
                if buf in self.keywords:
                    return self.add_token(self.token_names["KWORD"], buf)
                else:
                    return self.add_ident(self.add_token(self.token_names["IDENT"], buf), True, False)


            elif self.current_state == self.states["NUM"]:
                buf = [self.symbol]
                if not self.eof_state:
                    self.symbol, self.eof_state, self.line = next(self.fgetc)
                else:
                    break

                while ((not self.eof_state)
                       and self.symbol in "ABCDEFabcdefoOdDhH0123456789.eE+-"):
                    buf.append(self.symbol)
                    self.symbol, self.eof_state, self.line = next(self.fgetc)

                buf = ''.join(buf)
                is_n, token_num = self.is_num(buf)
                if is_n:
                    self.symbol = ""
                    return self.add_token(token_num, buf)
                else:
                    self.err_lex = buf
                    self.current_state = self.states["ERR"]


            elif self.current_state == self.states["DLM"]:
                if self.symbol in self.delimiters:
                    if self.symbol == "/":
                        self.symbol, self.eof_state, self.line = next(self.fgetc)

                        if not self.eof_state and self.symbol == "*":
                            self.symbol = ""
                            self.current_state = self.states["COMM"]
                        else:
                            return self.add_token(self.token_names["ARITHM"], "/")
                    else:
                        temp_symbol = self.symbol
                        self.symbol = ""
                        return self.add_token(self.token_names["DELIM"], temp_symbol)
                elif self.symbol in self.types:
                    temp_symbol = self.symbol
                    self.symbol = ""
                    return self.add_token(self.token_names["TYPE"], temp_symbol)
                else:
                    temp_symbol = self.symbol
                    self.symbol = ""
                    return self.add_token(self.token_names["ARITHM"], temp_symbol)


            elif self.current_state == self.states["OPER"]:
              # self.operators = {":", ":=", "=", "==", "!", "!=", "<", "<=", ">", ">=", }
                temp_symbol = self.symbol
                if not self.eof_state:

                    self.symbol, self.eof_state, self.line = next(self.fgetc)
                    operator = temp_symbol + self.symbol

                    if operator in self.operators:
                        self.symbol = ""
                        return self.add_token(self.token_names["OPER"], operator)
                    else:
                       # if "!" in operator or "=" in operator:

                        if temp_symbol != "=":
                            return self.add_token(self.token_names["OPER"], temp_symbol)
                        else:
                            self.err_lex = temp_symbol
                            self.current_state = self.states["ERR"]

                elif self.symbol != ":" and self.symbol != "=":
                    return self.add_token(self.token_names["OPER"], self.symbol)
                else:
                    self.err_lex = temp_symbol
                    self.current_state = self.states["ERR"]


            elif self.current_state == self.states["COMM"]:
                while not self.eof_state:
                    self.symbol, self.eof_state, self.line = next(self.fgetc)
                    if self.symbol == "*":
                        self.symbol, self.eof_state, self.line = next(self.fgetc)
                        if self.symbol == "/":
                            self.symbol = ""
                            self.current_state = self.states["H"]
                            break
              #  if self.eof_state and self.current_state == self.states["COMM"]:
              #      self.err_lex = "Отсутствует конец комментария"
               #     self.current_state = self.states["ERR"]

            elif self.current_state == self.states["ERR"]:
                if self.err_lex != "":
                    self.err_lex = self.symbol
                self.symbol = ""
                print(f"Неопознанная лексема: \"{self.err_lex}\", в строке {self.line}.")
                return False

        if self.eof_state:
            return "@"

    def is_num(self, digit):
        if re.match(r"(^\d+[Ee][+-]?\d+$|^\d*\.\d+([Ee][+-]?\d+)?$)", digit):
            return True, "REAL"
        elif re.match(r"^[01]+[Bb]$", digit):
            return True, "INT_2"
        elif re.match(r"^[01234567]+[Oo]$", digit):
            return True, "INT_8"
        elif re.match(r"^\d+[dD]?$", digit):
            return True, "INT_10"
        elif re.match(r"^\d[0-9ABCDEFabcdef]*[Hh]$", digit):
            return True, "INT_16"
        else:
            return False, False

    def add_token(self, token_name, token_value):
        lexeme = Lex(token_name, token_value, self.line)
        self.lexeme_list.append(lexeme)
        return lexeme

    def add_ident(self, lexeme: Lex, declared:bool, assigned:bool):
        identificator = Ident(lexeme, declared, assigned)
        self.id_list.append(identificator)
        return identificator

    def fgetc_generator(self, filename: str):
        with open(filename) as fin:
            file = list(fin.read())
            file.append('\n')
            print(file)
            pointer_line = 1
            for i in range(len(file)):
                yield file[i], i == (len(file) - 1), pointer_line
                if file[i] == "\n":
                    pointer_line += 1

'''

from Lexer import *

lexer = LexicalAnalyser("file.txt")
while True:
    if (lexer.getLexeme() == "@"):
        break
print('\nend')

token_names = {
    "KWORD": "KWORD",
    "IDENT": "IDENT",
    "OPER": "OPER",
    "DELIM": "DELIM",
    "TYPE": "TYPE",
    "ARITHM": "ARITHM",
    "INT_2": "INT_2",
    "INT_8": "INT_8",
    "INT_10": "INT_10",
    "INT_16": "INT_16",
    "REAL": "REAL"
}
result = {i: [] for i in token_names.keys()}
for i in lexer.lexeme_list:
   result[i.lex_type].append(i.lex_value)

for i in result:
    print(i, ":", result[i])
