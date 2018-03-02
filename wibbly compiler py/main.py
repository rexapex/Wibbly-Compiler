#!/usr/bin/python3

"""Wibbly language compiler"""
"""Visit our webstite at www.origamisheep.com"""

import sys
import symbol_table as st
import lexer as lexer
import syntax_parser as parser
import semantic_analyser as analyser

__author__ = "James Sugden"
__copyright__ = "Copyright © James Sugden 2018"
__version__ = "0.0.1"

def parseArgs(args):
    inFilename = None
    if len(args) >= 2:
        inFilename = args[1]
    else:
        raise InputError('error: no input file given')
    return inFilename

def main(args):
    try:
        inFilename = parseArgs(args)
        with open(inFilename) as file:
            symbolTable = st.SymbolTable()
            text = file.read()
            tokens, tokenTypes = lexer.genTokenStream(text)
            try:
                wp = parser.WibblyParser()
                wp.parse(tokens, symbolTable)
            except parser.SyntaxValidException as e:
                print('Syntax Valid')
            except parser.SyntaxInvalidException as e:
                print('Syntax Error')
    except IOError as err:
        print(err)

if __name__ == '__main__':
    main(sys.argv)
