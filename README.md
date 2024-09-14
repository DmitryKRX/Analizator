# Модель распознавания модельного языка программирования

Включает в себя: 

— лексический анализ;

— синтаксический анализ;

— семантический анализ.


## Грамматические правила модельного языка


PROGRAM → “{“ {/ (DESCRIPTION | OPERATOR); /} “}” 

DESCRIPTION → TYPE IDENTIFICATOR {, IDENTIFICATOR}

OPERATOR → COMPOSITE_OPER | ASSIGN_OPER | IF_OPER | FOR_CYCLE_OPER |

WHILE_CYCLE_OPER | READLN_OPER | WRITELN_OPER

COMPOSITE_OPER → begin OPERATOR {; OPERATOR} end  

ASSIGN_OPER → IDENTIFICATOR := EXPRESSION  

IF_OPER → if “(“ EXPRESSTION “)” OPERATOR [else OPERATOR]  

FOR_CYCLE_OPER → for ASSIGN_OPER to EXPRESSION [step EXPRESSION] OPERATOR next  

WHILE_CYCLE_OPER → while “(“ EXPRESSION “)” OPERATOR  

READLN_OPER → readln IDENTIFICATOR {, IDENTIFICATOR} 

WRITELN_OPER → writeln EXPRESSION {, EXPRESSION}    

EXPRESSION → OPERAND {RELATION_GROUP OPERAND} 

OPERAND → SUMMAND {ADDITION_GROUP SUMMAND}

SUMMAND → MULTIPLIER {MULTIP_GROUP MULTIPLIER} 

MULTIPLIER → IDENTIFICATOR | NUMBER | LOGIC_CONST | UNARY_OPER MULTIPLIER | “(“ EXPRESSION “)” 

TYPE → % | ! | $

IDENTIFICATOR → LETTER {LETTER | DIGIT} 

LOGIC_CONST → true | false 

RELATION_GROUP → != | == | < | <= | > | >=  

ADDITION_GROUP → + | - | || 

MULTIP_GROUP → * | / | &&  

UNARY_OPER → ! 

NUMBER → INT | REAL 

INT → BINARY | OCTA | DECIMAL | HEXA 

BINARY → {/ 0 | 1 /} (B | b) 

OCTA → {/ 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 /} (O | o) 

DECIMAL → {/ DIGIT /} [D | d]  

HEXA → DIGIT {DIGIT | A | B | C | D | E | F | a | b | c | d | e | f} (H | h) 

REAL → NUM_STRING ORDER | [NUMBER_STRING] . [NUM_STRING] [ORDER] 

NUM_STRING → {/ DIGIT /} 

ORDER → (E | E) [+ | -] NUM_STRING  


## Диаграмма состояний конечного автомата

![image](https://github.com/user-attachments/assets/9285563c-ba3e-4220-bf92-ec557524aba9)

— Состояние **“H”** отвечает за начальное состояние анализатора. В нем
считывается следующий символ до тех пор, пока встречаются знаки проблема,
табуляции, перехода на следующую строку или возврата каретки. В нем
определяется следующее состояние анализатора, по определенным входным
символам.

— Состояние **“WORD”** активируется, когда в состояние **“H”** попадает буква.
Активно оно до тех пор, пока не встретится знак пробела, табуляции или
перехода на следующую строку. В этом состоянии анализатора определяются
ключевые слова или идентификаторы.

— Состояние **“NUM”** активируется, когда в состояние **“H”** попадает цифра.
Данный блок определяет целочисленные и вещественные числа. Если на вход
блоку **“NUM”** попадает пробел, знак табуляции или знак переноса на следующую
строку, он возвращается в состояние **“H”**. Если попадается любой иной символ,
выбирается состояние ошибки **“ERR”**.

— Состояние **“DLM”** активируется, когда в состояние **“H”** попадает один из
определенных символов-разделителей. Классифицировав данную лексему,
автомат возвращается в состояние **“H”**.

— Состояние **“OPER”** активируется, когда в состояние **“H”** попадает один из
символов-операторов или арифметических операций. На данном этапе
считывается следующий символ и на его основе определяется следующее
состояние: если получилась конструкция “/*”, автомат переключается в
состояние комментария **“COMM”**, если получилась конструкция, определенная
модельным языком, возвращается состояние “H”. Иначе вызывается состояние
“ERR”.

— Состояние **“COMM”** ответственно за комментарий в программе.
Анализатор считывает все символы до тех пор, пока не дойдет до конструкции
“*/”. Далее он переходит в состояние **“H”**.

— Состояние **“ERR”** может активироваться из состояний **“NUM”**, **“OPER”**
или **“H”**. Выводит сообщение о лексической ошибке и прекращает выполнение
программы.


### Запуск

Для запуска требуется Python версии не ниже 3.7.

Запуск производится через файл **main.py**.

Код модельного языка считывается из файла **file.txt**.
