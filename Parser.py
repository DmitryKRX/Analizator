from Lexer import *

class Parser:
    def __init__(self, filename: str):
        self.curr_lex = None
        self.lexer = LexicalAnalyzer(filename)

        self.curr_expressions = []
        self.last_type = ""
        self.id_list = {"INT": [], "REAL": [], "BOOL": []}

    def compare_type(self, item: str):
        if self.curr_lex.type != item:
            self.exception()

    def compare_value(self, item: str):
        if self.curr_lex.value != item:
            self.exception(item)

    def exception(self, expected=""):
        if expected == "":
            print(f"Синтаксическая ошибка: '{self.curr_lex.value}', в строке {self.curr_lex.line}")
        else:
            print(f"Синтаксическая ошибка: '{self.curr_lex.value}', в строке {self.curr_lex.line}, ожидалось: '{expected}'")
        exit(1)

    def semantic_exception(self, description="", line=None):
        if line is None:
            line = self.curr_lex.line
        print(f"Семантическая ошибка в строке {line}: {description}")
        exit(1)

    def get_type_by_value(self, search_value):
        for key in self.id_list:
            if search_value in self.id_list[key]:
                return key
        return None

    def analyze(self):
        self.curr_lex = self.lexer.getLexeme()
        return self.PROGRAM()

    # <программа>::= «{» {/ (<описание> | <оператор>) ; /} «}»
    def PROGRAM(self):
        self.compare_value("{")
        self.curr_lex = self.lexer.getLexeme()

        if self.curr_lex.type == "TYPE":
            self.DESCRIPTION()
        else:
            self.OPERATOR()

        while self.curr_lex.value == ";":
            self.curr_lex = self.lexer.getLexeme()
            if self.curr_lex.type == "TYPE":
                self.DESCRIPTION()
            elif self.curr_lex.value == "}":
                break
            else:
                self.OPERATOR()
        self.compare_value("}")
        self.curr_lex = self.lexer.getLexeme()

        if (self.curr_lex.value == "@"):
            return True
        else:
            self.exception()

    # <описание>::= <тип> <идентификатор> { , <идентификатор> }
    def DESCRIPTION(self):
        self.TYPE()
        self.IDENTIFICATOR(True)
        while self.curr_lex.value == ",":
            self.curr_lex = self.lexer.getLexeme()
            self.IDENTIFICATOR(True)

    # <тип>::= % | ! | $    ((int float bool))
    def TYPE(self):
        if self.curr_lex.value == "%":
            self.last_type = "INT"
        elif self.curr_lex.value == "!":
            self.last_type = "REAL"
        elif self.curr_lex.value == "$":
            self.last_type = "BOOL"
        else: self.exception()

        self.curr_lex = self.lexer.getLexeme()

    # <идентификатор>::= <буква> {<буква> | <цифра>}
    def IDENTIFICATOR(self, from_description: bool):
        self.compare_type("IDENT")
        isIn = False
        if from_description:
            for key in self.id_list:
                if self.curr_lex.value in self.id_list[key]:
                    isIn = True
                    break
            if isIn:
                self.semantic_exception("Повторное объявление идентификатора.")

            self.id_list[self.last_type].append(self.curr_lex.value)
        else:
            for key in self.id_list:
                if self.curr_lex.value in self.id_list[key]:
                    isIn = True
                    break
            if not isIn:
                self.semantic_exception("Идентификатор не объявлен.")

        self.curr_lex = self.lexer.getLexeme()

    # <оператор>::= <составной> | <присваивания> | <условный>
    # | <фиксированного_цикла> | <условного_цикла> | <ввода> | <вывода>
    def OPERATOR(self):
        if self.curr_lex.value == "begin":
            self.COMPOSITE_OPER()
        elif self.curr_lex.value == "if":
            self.IF_OPER()
        elif self.curr_lex.value == "for":
            self.FOR_CYCLE_OPER()
        elif self.curr_lex.value == "while":
            self.WHILE_CYCLE_OPER()
        elif self.curr_lex.value == "readln":
            self.READLN_OPER()
        elif self.curr_lex.value == "writeln":
            self.WRITELN_OPER()
        elif self.curr_lex.type == 'IDENT':
            self.ASSIGN_OPER()
        else:
            self.exception()


    # <составной>::= begin <оператор> { ; <оператор> } end
    def COMPOSITE_OPER(self):
        self.curr_lex = self.lexer.getLexeme()
        self.OPERATOR()

        while self.curr_lex.value == ";":
            self.curr_lex = self.lexer.getLexeme()
            self.OPERATOR()

        self.compare_value("end")
        self.curr_lex = self.lexer.getLexeme() #################



    # <присваивания>::= <идентификатор> := <выражение>
    def ASSIGN_OPER(self):
        self.curr_expressions = []
        ident = self.curr_lex.value
        self.IDENTIFICATOR(False)

        curr_id_type = self.get_type_by_value(ident)
        self.compare_value(":=")
        self.curr_lex = self.lexer.getLexeme()
        ident = self.curr_lex
        self.EXPRESSION()

        for expr in self.curr_expressions:
            if curr_id_type == "INT" and (expr == "REAL" or expr == "BOOL"):
                self.semantic_exception("Несоответствие типов", ident.line )
            if curr_id_type == "REAL" and (expr == "BOOL"):
                self.semantic_exception("Несоответствие типов", ident.line)
            if curr_id_type == "BOOL" and (expr == "REAL" or expr == "INT"):
                self.semantic_exception("Несоответствие типов", ident.line)


    # <условный>::= if «(»<выражение> «)» <оператор> [else <оператор>]
    def IF_OPER(self):
        self.curr_lex = self.lexer.getLexeme()
        self.compare_value("(")
        self.curr_lex = self.lexer.getLexeme()
        self.EXPRESSION()
        self.compare_value(")")
        self.curr_lex = self.lexer.getLexeme()
        self.OPERATOR()

        if self.curr_lex.value == "else":
            self.curr_lex = self.lexer.getLexeme()
            self.OPERATOR()


    # <фиксированного_цикла>::= for <присваивания> to <выражение> [step
    # <выражение>] <оператор> next
    def FOR_CYCLE_OPER(self):
        self.curr_lex = self.lexer.getLexeme()
        self.ASSIGN_OPER()
        self.compare_value("to")
        self.curr_lex = self.lexer.getLexeme()
        self.EXPRESSION()

        if self.curr_lex.value == "step":
            self.curr_lex = self.lexer.getLexeme()
            self.EXPRESSION()

        self.OPERATOR()
        self.compare_value("next")
        self.curr_lex = self.lexer.getLexeme() ##### спорная операция!!!!!!

    # <условного_цикла>::= while «(»<выражение> «)» <оператор>
    def WHILE_CYCLE_OPER(self):
        self.curr_lex = self.lexer.getLexeme()
        self.compare_value("(")

        self.curr_lex = self.lexer.getLexeme()
        self.EXPRESSION()

        self.compare_value(")")
        self.curr_lex = self.lexer.getLexeme()
        self.OPERATOR()

    # <ввода>::= readln идентификатор {, <идентификатор> }
    def READLN_OPER(self):
        self.curr_lex = self.lexer.getLexeme()
        self.IDENTIFICATOR(False)

        while self.curr_lex.value == ",":
            self.curr_lex = self.lexer.getLexeme()
            self.IDENTIFICATOR(False)


    # <вывода>::= writeln <выражение> {, <выражение> }
    def WRITELN_OPER(self):
        self.curr_lex = self.lexer.getLexeme()
        self.EXPRESSION()

        while self.curr_lex.value == ",":
            self.curr_lex = self.lexer.getLexeme()
            self.EXPRESSION()


    # <выражение>::= <операнд>{<операции_группы_отношения> <операнд>}
    def EXPRESSION(self):
        self.OPERAND()
        while self.curr_lex.value in {"!=", "==", "<", "<=", ">", ">="}:
            self.curr_lex = self.lexer.getLexeme()
            self.OPERAND()


    # <операнд>::= <слагаемое> {<операции_группы_сложения> <слагаемое>}
    def OPERAND(self):
        self.SUMMAND()
        while self.curr_lex.value in {"+", "-", "||"}:
            self.curr_lex = self.lexer.getLexeme()
            self.SUMMAND()


    # <слагаемое>::= <множитель> {<операции_группы_умножения> <множитель>}
    def SUMMAND(self):
        self.MULTIPLIER()
        while self.curr_lex.value in {"*", "/", "&&"}:
            self.curr_lex = self.lexer.getLexeme()
            self.MULTIPLIER()

    # <множитель>::= <идентификатор> | <число> | <логическая_константа> |
    # <унарная_операция> <множитель> | «(»<выражение>«)»
    def MULTIPLIER(self):
        if self.curr_lex.type in {"IDENT", "INT", "REAL"}:
            if self.curr_lex.type == "IDENT":
                curr_id_type = self.get_type_by_value(self.curr_lex.value)
                self.IDENTIFICATOR(False)
                self.curr_expressions.append(curr_id_type)
            else:
                self.curr_expressions.append(self.curr_lex.type)
                self.curr_lex = self.lexer.getLexeme()
        elif self.curr_lex.value in {"true", "false"}:
            self.curr_expressions.append("BOOL")
            self.curr_lex = self.lexer.getLexeme()
        elif self.curr_lex.value == "!":
            self.curr_lex = self.lexer.getLexeme()
            self.MULTIPLIER()
        else:
            self.compare_value("(")
            self.curr_lex = self.lexer.getLexeme()
            self.EXPRESSION()
            self.compare_value(")")
            self.curr_lex = self.lexer.getLexeme()
