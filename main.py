from Parser import *

parser = Parser("file.txt")
if parser.analyze() == True:
    print("Программа корректна!")
else:
    print("Программа некорректна!")