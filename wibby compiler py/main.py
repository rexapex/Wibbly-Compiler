"""Copyright © James Sugden 2018"""
import lexer as lexer
import my_parser as parser

with open('../valid file.wbly') as file:
    text = file.read()
    tokens, tokenTypes = lexer.genTokenStream(text)
    parser.genParseTree(tokens, tokenTypes)
