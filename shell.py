from tokenizer import NumberTokenizer, Lexer, WhitespacesTokenizer, ParenTokenizer, OperatorTokenizer
from parser import Parser
from interpreter import Interpreter

tokenizers = [
    WhitespacesTokenizer(),
    NumberTokenizer(),
    OperatorTokenizer(),
    ParenTokenizer(),
]

skip = 'whitespace',

action = lambda string: print(Interpreter(Parser(Lexer(tokenizers, string, *skip))))

while True:
    text = input(">>> ")
    if not text:
        break
    action(text)
