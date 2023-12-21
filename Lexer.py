import re

class Lex:
    def __init__(self, lex_type:str, lex_value:str, line:int):
        self.type = lex_type
        self.value = lex_value
        self.line = line

class LexicalAnalyzer:
    def __init__(self, filename: str):
        self.token_names = {
            "KWORD": "KWORD",
            "IDENT": "IDENT",
            "OPER": "OPER",
            "DELIM": "DELIM",
            "TYPE": "TYPE",
            "INT": "INT",
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

        self.keywords = {"begin", "end", "if", "else", "for", "to",
                         "step", "next", "while", "readln", "writeln",
                         "true", "false"}
        self.delimiters = {";", ",", "[", "]", "(", ")", "{", "}"}

        self.arithmetic = {"+", '-', '*', '/', "&", "|"}
        self.operators = {":", "=", "!", "<", ">"}
        self.types = {"%", "!", "$"}


        self.lexeme_list = []
        self.eof_state = False
        self.current_state = self.states["H"]
        self.symbol = ""
        self.err_lex = ""
        self.line = 0
        self.fgetc = self.fgetc_generator(filename)

    def getLexeme(self):
        self.current_state = self.states["H"]

        if self.symbol == "" and not self.eof_state:
            self.symbol, self.eof_state, self.line = next(self.fgetc)
        while not self.eof_state:
            if self.current_state == self.states["H"]:
                while not self.eof_state and self.symbol in {" ", "\n", "\t", "\r", ""}:
                    self.symbol, self.eof_state, self.line = next(self.fgetc)
                if self.symbol.isalpha():
                    self.current_state = self.states["WORD"]
                elif self.symbol.isdigit():
                    self.current_state = self.states["NUM"]
                elif self.symbol in self.delimiters:
                    self.current_state = self.states["DLM"]
                elif self.symbol in (self.types | self.operators | self.arithmetic):
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
                 #   return self.add_ident(self.add_token(self.token_names["IDENT"], buf), True, False)
                    return self.add_token(self.token_names["IDENT"], buf)


            elif self.current_state == self.states["NUM"]:
                buf = [self.symbol]
                self.symbol, self.eof_state, self.line = next(self.fgetc)

                while ((not self.eof_state)
                       and self.symbol in "ABCDEFabcdefoOdDhH0123456789.eE+-"):
                    buf.append(self.symbol)
                    self.symbol, self.eof_state, self.line = next(self.fgetc)

                buf = ''.join(buf)
                is_n, token_num = self.is_num(buf)
                if is_n:
                    return self.add_token(token_num, buf)
                else:
                    self.err_lex = buf
                    self.current_state = self.states["ERR"]


            elif self.current_state == self.states["DLM"]:
                # self.delimiters = {";", ",", "[", "]", "(", ")", "{", "}"}
                temp_symbol = self.symbol
                self.symbol = ""
                return self.add_token(self.token_names["DELIM"], temp_symbol)


            elif self.current_state == self.states["OPER"]:
              # self.operators = {":", ":=", "=", "==", "!", "!=", "<", "<=", ">", ">=", }
              # self.arithmetic = {"+", '-', '*', '/',  "||", "&&" }
              # self.types = {"%", "!", "$"}

                if self.symbol == "/":
                    temp_symbol = self.symbol
                    self.symbol, self.eof_state, self.line = next(self.fgetc)

                    if not self.eof_state and self.symbol == "*":
                        self.symbol = ""
                        self.current_state = self.states["COMM"]
                    elif not self.eof_state and self.symbol in {" ", "\n", "\t"}:
                        #  return self.add_token(self.token_names["ARITHM"], "/")
                        return self.add_token(self.token_names["OPER"], "/")
                    elif not self.eof_state:
                        self.err_lex = (temp_symbol + self.symbol)
                        self.current_state = self.states["ERR"]


                elif self.symbol == "!":
                    self.symbol, self.eof_state, self.line = next(self.fgetc)
                    if not self.eof_state and self.symbol == "=":
                        self.symbol = ""
                        return self.add_token(self.token_names["OPER"], "!=")
                    elif not self.eof_state and self.symbol in {" ", "\n", "\t"}:
                        self.symbol = ""
                        return self.add_token(self.token_names["TYPE"], "!")
                    elif not self.eof_state:
                        return self.add_token(self.token_names["OPER"], "!")

                elif self.symbol in {"%", "$"}:
                    temp_symbol = self.symbol
                    self.symbol = ""
                    return self.add_token(self.token_names["TYPE"], temp_symbol)
                elif self.symbol in {"+", "-", "*"}:
                    temp_symbol = self.symbol
                    self.symbol = ""
                    return self.add_token(self.token_names["OPER"], temp_symbol)
                else:
                    temp_symbol = self.symbol
                    self.symbol, self.eof_state, self.line = next(self.fgetc)
                    operator = temp_symbol + self.symbol
                  #  print(operator)

                    if operator in {"==", ">=", "<=", "||", "&&", ":="}:
                        self.symbol = ""
                        return self.add_token(self.token_names["OPER"], operator)
                    elif temp_symbol in {"<", ">"}:
                        self.symbol = ""
                        return self.add_token(self.token_names["OPER"], temp_symbol)
                    else:
                     #   self.err_lex = operator
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

            elif self.current_state == self.states["ERR"]:
                if self.err_lex == "":
                    self.err_lex = self.symbol
                self.symbol = ""
                print(f"Неопознанная лексема: \"{self.err_lex}\", в строке {self.line}.")
                exit(1)

        if self.eof_state:
           # print("returned @")
            return self.add_token("@", "@")

    def fgetc_generator(self, filename: str):
        with open(filename) as fin:
            file = list(fin.read())
            file.append('\n')
         #   print(file)
            pointer_line = 1
            for i in range(len(file)):
                yield file[i], i == (len(file) - 1), pointer_line
                if file[i] == "\n":
                    pointer_line += 1

    def is_num(self, digit):
        if re.match(r"(^\d+[Ee][+-]?\d+$|^\d*\.\d+([Ee][+-]?\d+)?$)", digit):
            return True, "REAL"
        elif re.match(r"^[01]+[Bb]$", digit):
            return True, "INT"
        elif re.match(r"^[01234567]+[Oo]$", digit):
            return True, "INT"
        elif re.match(r"^\d+[dD]?$", digit):
            return True, "INT"
        elif re.match(r"^\d[0-9ABCDEFabcdef]*[Hh]$", digit):
            return True, "INT"
        else:
            return False, False

    def add_token(self, token_name, token_value):
        lexeme = Lex(token_name, token_value, self.line)
        self.lexeme_list.append(lexeme.type + ": " + lexeme.value)
        return lexeme