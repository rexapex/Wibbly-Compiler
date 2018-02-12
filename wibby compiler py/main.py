"""Copyright © James Sugden 2018"""
import lexer as lexer
import parser as parser

with open('../new syntax.wbly') as file:
    text = file.read()
    tokens, tokenTypes = lexer.genTokenStream(text)
    parser.genParseTree(tokens, tokenTypes)
