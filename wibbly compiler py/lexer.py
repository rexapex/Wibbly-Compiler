"""Lexical analyser of the Wibbly language compiler"""
"""Visit our webstite at www.origamisheep.com"""

import re

__author__ = "James Sugden"
__copyright__ = "Copyright © James Sugden 2018"
__version__ = "0.0.1"

class Token:
    def __init__(self, tokenType, text, startIndex):
        self.type = tokenType
        self.text = text
        self.startIndex = startIndex

def genTokenStream(text):
    captureKeyword = '(\\b(?:if|else|then|while|for|in|break|continue|return|do|end|wibbly|wobbly|true|false|empty|class|module|get|set|int|big|float|string|bool|func|me|import)\\b)'
    captureNumber = '(\\b[0-9]+(?:.[0-9]+)?\\b)'
    captureComment = '(\\/\\/.*)'
    captureIdentifier = '(\\b[a-zA-Z_][a-zA-Z_0-9]*\\b)'
    captureString = '((?:".*?")|(?:\'.*?\'))'   # supports single and double quoted strings
    captureBinaryOperator = '(\\+=|-=|\\*=|/=|%=|=|\\+|-|\\*|/|\\*\\*|%|\\.)'
    captureUnaryOperator = '(\\+\\+|--)'
    captureDelimiters = '(,|\\(|\\)|:)'

    p = re.compile(captureComment + '|' + captureKeyword + '|' + captureNumber + '|' + captureIdentifier + '|' + captureString + '|' + captureBinaryOperator + '|' + captureUnaryOperator + '|' + captureDelimiters)
    iterator = p.finditer(text)

    tokenTypes = [None, 'LINE_COMMENT', 'KEYWORD', 'NUMBER_LIT', 'IDENTIFIER', 'STRING_LIT', 'BIN_OP', 'UN_OP', 'DELIM']
    tokens = []

    for match in iterator:
        # first group matches the whole text
        for i in range(1, p.groups + 1):
            if not match.group(i) is None:
                tokens.append(Token(tokenTypes[i], match.group(), match.start()))
                #tokens.append([i, match.start(), match.group()])
                break

    tokens.sort(key=lambda x: x.startIndex)

    for tok in tokens:
        print(tok.type + ':       ' + tok.text)

    return tokens, tokenTypes
