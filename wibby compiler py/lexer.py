"""Copyright © James Sugden 2018"""
import re

def genTokenStream(text):
    captureKeyword = '(\\b(?:if|else|then|while|for|in|break|continue|return|do|end|wibbly|wobbly|true|false|empty|open|close|print|println|class|get|set|int|big|float|string|bool|func|me)\\b)'
    captureNumber = '(\\b[0-9]+(?:.[0-9]+)?\\b)'
    captureComment = '(\\/\\/.*)'
    captureIdentifier = '(\\b[a-zA-Z_][a-zA-Z_0-9]*\\b)'
    captureString = '((?:".*?")|(?:\'.*?\'))'   # supports single and double quoted strings
    captureBinaryOperator = '(=|\\+|-|\\*|/|\\*\\*|%|\\+=|-=|\\*=|/=|%=|\\.)'
    captureUnaryOperator = '(\\+\\+|--)'
    captureDelimiters = '(,|\\(|\\)|\\:)'

    p = re.compile(captureComment + '|' + captureKeyword + '|' + captureNumber + '|' + captureIdentifier + '|' + captureString + '|' + captureBinaryOperator + '|' + captureUnaryOperator + '|' + captureDelimiters)
    iterator = p.finditer(text)

    tokenTypes = [None, 'LINE_COMMENT', 'KEYWORD', 'NUMBER', 'IDENTIFIER', 'STRING', 'BIN_OP', 'UN_OP', 'DELIM']
    tokens = []

    for match in iterator:
        # first group matches the whole text
        for i in range(1, p.groups + 1):
            if not match.group(i) is None:
                tokens.append([i, match.start(), match.group()])
                break

    tokens.sort(key=lambda x: x[1])

    for tok in tokens:
        print(tokenTypes[tok[0]] + ':       ' + tok[2])

    return tokens, tokenTypes
