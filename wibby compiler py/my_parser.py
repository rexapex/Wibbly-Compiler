"""Syntax parser of the Wibbly language compiler"""
"""Visit our webstite at www.origamisheep.com"""

import sys

__author__ = "James Sugden"
__copyright__ = "Copyright © James Sugden 2018"
__version__ = "0.0.1"

class SyntaxInvalidException(Exception):
    pass

class SyntaxValidException(Exception):
    pass

class Rule:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

# class ParseTree:
#     def __init__(self):
#         self.root = TreeNode('file')
#
# class TreeNode:
#     def __init__(self, value):
#         self.left = None
#         self.right = None
#         self.value = value;

# WibblyParser is a LL(2) Top-Down Syntax Parser
class WibblyParser:
    def __init__(self):
        self.lookahead = None
        self.lookahead2 = None
        self.tokens = None
        self.tokenIndex = 0
        self.terminals = ['IDENTIFIER', 'STRING_LIT', 'NUMBER_LIT', '(', ')', '.', ',', '"', '\'', '<=', '>=', '=', '<', '>', 'if', 'else', 'then', 'while', 'for', 'in', 'break', 'continue']
        self.terminals += ['return', 'do', 'end', 'wibbly', 'wobbly', 'true', 'false', 'empty', 'class', 'module', 'get', 'set', 'int', 'big', 'float', 'string', 'bool', 'func', 'me', 'import']

    def parse(self, tokens):
        self.tokens = tokens

        # remove all comments since they are irrelevant
        for tok in tokens:
            if tok.type == 'LINE_COMMENT':
                self.tokens.remove(tok)

        self.tokenIndex = 0

        # parse the token stream
        print('\nSyntax Parser')
        if len(tokens) > 0:
            self.lookahead, self.lookahead2 = self.nextTerminal()
            self.globalStatements()

    def nextToken(self):
        self.tokenIndex += 1
        if self.tokenIndex >= len(self.tokens):
            self.done()

    def nextTerminal(self):
        termIndex = self.tokenIndex
        newLookahead1 = None
        while(termIndex < len(self.tokens)):
            if (self.tokens[termIndex].type == 'IDENTIFIER' or self.tokens[termIndex].type == 'STRING_LIT' or self.tokens[termIndex].type == 'NUMBER_LIT') or (self.tokens[termIndex].text in self.terminals):
                if newLookahead1 is None:
                    newLookahead1 = self.tokens[termIndex]
                else:
                    return newLookahead1, self.tokens[termIndex]
            termIndex += 1
        if not newLookahead1 is None:
            return newLookahead1, None
        # no terminals left therefore done parsing
        self.done()

    # match any number of global statements consecutively
    def globalStatements(self):
        self.globalStatement()
        if self.lookahead.text == 'import' or self.lookahead.text == 'class' or self.lookahead.text == 'module':
            self.globalStatements()

    # match the non-terminal globalStatement
    def globalStatement(self):
        if self.lookahead.text == 'import':
            self.match('import')
            self.match('STRING_LIT')
        elif self.lookahead.text == 'class':
            self.classStatement()
        elif self.lookahead.text == 'module':
            self.match('module')
            self.match('IDENTIFIER')
            self.block()
            self.match('module')

    def classStatement(self):
        self.match('class')
        self.match('IDENTIFIER')
        self.parameterList()
        self.block()
        self.match('class')

    def block(self):
        self.match('do')
        self.statements()
        self.match('end')

    def statements(self):
        self.statement()
        if self.lookahead.type == 'IDENTIFIER' or self.lookahead.text == 'func' or self.lookahead.text == 'class':
            self.statements()

    def statement(self):
        if self.lookahead.text == 'wibbly':
            self.wibblyStatement()
        if self.lookahead.type == 'IDENTIFIER':                                 # could either be a variable decleration or assignment (both handled by variableDeclerations), or a function call
            if not self.lookahead2 is None and self.lookahead2.text == '(':     # must be a function call (hopefully)
                self.functionCall()
            else:
                self.variableDeclerations()
        elif self.lookahead.text == 'func':
            self.functionDecleration()
        elif self.lookahead.text == 'class':            # nested classes are allowed
            self.classStatement()

    def wibblyStatement(self):
        pass

    def functionCall(self):
        self.match('IDENTIFIER')
        self.argumentList()

    def argumentList(self):
        self.match('(')
        if self.lookahead.text != ')':  # doesn't have to be any arguments in the list
            self.expressions()
        self.match(')')

    def functionDecleration(self):
        self.match('func')
        if self.tokens[self.tokenIndex].type == 'IDENTIFIER':   # optional function identifier (anonymous functions possible)
            self.match('IDENTIFIER')
        self.parameterList()
        self.block()
        self.match('func')

    # match the non-terminal parameterList
    def parameterList(self):
        self.match('(')
        self.variableDeclerations()
        self.match(')')

    def variableDeclerations(self):
        if self.lookahead.type == 'IDENTIFIER':     # list could be empty
            self.variableDecleration()
            if self.lookahead.text == ',':
                self.match(',')
                self.variableDeclerations()

    def variableDecleration(self):
        self.match('IDENTIFIER')
        if self.lookahead.text == ':':  # variable has optional type
            self.match(':')
            self.variableType()
        if self.lookahead.text == '=':  # variable has optional assignment
            self.match('=')
            self.expression()

    def variableType(self):
        if self.lookahead.type == 'IDENTIFIER':      # type could be a class in which case the text will be an identifier
            self.match('IDENTIFIER')
        elif self.lookahead.text == 'int':
            self.match('int')
        elif self.lookahead.text == 'float':
            self.match('float')
        elif self.lookahead.text == 'string':
            self.match('string')
        elif self.lookahead.text == 'bool':
            self.match('bool')
        elif self.lookahead.text == 'event':
            self.match('event')
        elif self.lookahead.text == 'big':           # big is a modifier to int and float types
            self.match('big')
            if self.lookahead.text == 'int':
                self.match('int')
            elif self.lookahead.text == 'float':
                self.match('float')

    def expressions(self):
        self.expression()
        if self.lookahead.text == ',':      # more than 1 expression
            self.match(',')
            self.expression()

    def expression(self):
        if self.lookahead.text == '+':      # add
            self.expression()
            self.match('+')
            self.expression()
        elif self.lookahead.text == '-':    # subtract
            self.expression()
            self.match('-')
            self.expression()
        elif self.lookahead.text == '*':    # multiply
            self.expression()
            self.match('*')
            self.expression()
        elif self.lookahead.text == '/':    # divide
            self.expression()
            self.match('/')
            self.expression()
        elif self.lookahead.text == '**':
            self.expression()
            self.match('**')
            self.expression()
        elif self.lookahead.text == '%':    # remainder
            self.expression()
            self.match('%')
            self.expression()
        elif self.lookahead.text == '%%':   # integer divide
            self.expression()
            self.match('%')
            self.expression()
        elif self.lookahead.text == '==':
            self.expression()
            self.match('==')
            self.expression()
        elif self.lookahead.text == '<':
            self.expression()
            self.match('<')
            self.expression()
        elif self.lookahead.text == '>':
            self.expression()
            self.match('>')
            self.expression()
        elif self.lookahead.text == '<=':
            self.expression()
            self.match('<=')
            self.expression()
        elif self.lookahead.text == '>=':
            self.expression()
            self.match('>=')
            self.expression()
        elif self.lookahead.text == '~==':
            self.expression()
            self.match('~==')
            self.expression()
        elif self.tokens[self.tokenIndex].type == 'IDENTIFIER':
            self.match('IDENTIFIER')
        elif self.tokens[self.tokenIndex].type == 'STRING_LIT':
            self.match('STRING_LIT')
        elif self.tokens[self.tokenIndex].type == 'NUMBER_LIT':
            self.match('NUMBER_LIT')

    # match a terminal
    def match(self, terminal):
        if (self.lookahead.type == 'IDENTIFIER' or self.lookahead.type == 'STRING_LIT' or self.lookahead.type == 'NUMBER_LIT') and terminal == self.lookahead.type:
            print('matched ' + terminal)
            self.nextToken()
            if not self.lookahead2 is None:
                self.lookahead, self.lookahead2 = self.nextTerminal()
            else:
                self.done()
        elif self.lookahead.text == terminal:
            print('matched ' + terminal)
            self.nextToken()
            if not self.lookahead2 is None:
                self.lookahead, self.lookahead2 = self.nextTerminal()
            else:
                self.done()
        else:
            #print('lookahead at exit = ' + self.lookahead.text + ", " + self.lookahead.type)
            #print('lookahead2 at exit = ' + self.lookahead2.text + ", " + self.lookahead2.type)
            self.done()

    def done(self):
        if self.tokenIndex < len(self.tokens):
            raise SyntaxInvalidException()
        else:
            raise SyntaxValidException()

def getRules():
    # define a set of rules (productions)
    rules = []
    # a file is list of global statements
    rules.append(Rule('file', ['glob_statements']))
    # a global statements can be one or more global statements
    rules.append(Rule('glob_statements', ['glob_statements', 'glob_statement']))
    rules.append(Rule('glob_statements', ['glob_statement']))
    # a global statement can be an import statement or an encapsulator
    rules.append(Rule('glob_statement', ['import_statement']))
    rules.append(Rule('glob_statement', ['encapsulator']))
    # an encapsulator is can only be a class statement in the current version
    rules.append(Rule('encapsulator', ['class_statement']))
    # a class is made of the class keyword, followed by a name followed by a parameter list followed by do, followed by any number of statements followed by end class
    rules.append(Rule('class_statement', ['KEYWORD=class', 'IDENTIFIER', 'parameter_list', 'KEYWORD=do', 'statements', 'KEYWORD=end', 'KEYWORD=class']))
    # a parameter list is a list of variable declerations enclosed by parentheses
    rules.append(Rule('parameter_list', ['DELIM=(', 'variable_declerations', 'DELIM=)']))
    # a variable declerations is a list of comma separated variable declerations or a single variable decleration
    rules.append(Rule('variable_declerations', ['variable_declerations', 'DELIM=,', 'variable_decleration']))
    rules.append(Rule('variable_declerations', ['variable_decleration']))
    # a variable decleration has an identifier, and optionally has a type
    rules.append(Rule('variable_decleration', ['IDENTIFIER']))
    rules.append(Rule('variable_decleration', ['IDENTIFIER', 'DELIM=:', 'variable_type']))
    # a variable assignment assigns an the value of an expression to a variable
    rules.append(Rule('variable_assignment', ['variable_decleration', 'BIN_OP==', 'expr']))
    # a statements can be one statement or many statements
    rules.append(Rule('statements', ['statements', 'statement']))
    rules.append(Rule('statements', ['statement']))
    # a statement can be many things
    rules.append(Rule('statement', ['variable_decleration']))
    rules.append(Rule('statement', ['variable_assignment']))
    rules.append(Rule('statement', ['func_definition']))
    # a function definition is the following... (a function can be named or anonymous)
    rules.append(Rule('func_definition', ['KEYWORD=func', 'parameter_list', 'KEYWORD=do', 'statements', 'KEYWORD=end', 'KEYWORD=func']))
    rules.append(Rule('func_definition', ['KEYWORD=func', 'IDENTIFIER', 'parameter_list', 'KEYWORD=do', 'statements', 'KEYWORD=end', 'KEYWORD=func']))
    # an expression is any statement which returns a value
    rules.append(Rule('expr', ['string_expr']))
    rules.append(Rule('expr', ['number_expr']))
    rules.append(Rule('expr', ['func_call']))
    # a function call is a function name followed by and argument list
    rules.append(Rule('func_call', ['IDENTIFIER', 'arg_list']))
    # an argument list is a list of expressions enclosed in parentheses
    rules.append(Rule('arg_list', ['DELIM=(', 'expr_list', 'DELIM=)']))
    # an expression list is a list of expressions separated by commas or a single expression
    rules.append(Rule('expr_list', ['expr_list', 'DELIM=,', 'expr']))
    rules.append(Rule('expr_list', ['expr']))
    # a string expression can be a string literal or multiple string literals appended together
    rules.append(Rule('string_expr', ['string_expr', 'BIN_OP=+', 'STRING_LIT']))
    rules.append(Rule('string_expr', ['STRING_LIT']))
    # a number expression can be a number literal or an algebraic expression
    rules.append(Rule('number_expr', ['NUMBER_LIT']))
    rules.append(Rule('number_expr', ['algebraic_expr']))
    # an algebraic expression is what you think...
    return rules

# def interpret(self, tokens):
#     index = 0
#     while index < len(tokens):
#         token = tokens[index]
#         index, valid = parseToken(token, tokens, index)
#         if valid == False:
#             print('error: cannot be compiled')
#
# def isTextExpected(token, expecting):
#     if expecting is None:
#         return True, None
#     else:
#         expected = False
#         index = 0
#         for option in expecting:
#             if len(option) > 0 and token.text == option[0]:
#                 return True, index
#             index += 1
#     return False, None
#
# def isTypeExpected(token, expecting):
#     if expecting is None:
#         return True, None
#     else:
#         expected = False
#         index = 0
#         for option in expecting:
#             if len(option) > 0 and token.type == option[0]:
#                 return True, index
#             index += 1
#     return False, None
#
# def parseNonTerminal(tokens, index, expecting):
#     if not expecting is None and len(expecting) > 0:
#         for option in expecting:
#             if len(option) > 0:
#                 valid = True
#                 if option[0] == 'parameter_list':
#                     print('parameter list')
#                     del option[0]
#                     index, valid = parseToken(tokens[index], tokens, index, [['(', 'variable_declerations', ')']])
#                 elif option[0] == 'variable_declerations':
#                     print('variable declerations')
#                     del option[0]
#                     index, valid = parseToken(tokens[index], tokens, index, [['variable_decleration'], ['variable_decleration', ',', 'variable_declerations']])
#                 elif option[0] == 'variable_decleration':
#                     print('variable decleration')
#                     del option[0]
#                     index, valid = parseToken(tokens[index], tokens, index, [['IDENTIFIER'], ['IDENTIFIER', ':', 'variable_type']])
#
#                 if not valid:
#                     continue
#     return index
#
# def parseToken(token, tokens, index, expecting = None):
#     index = parseNonTerminal(tokens, index, expecting)
#     if not expecting is None:
#         print(expecting)
#         for option in expecting:
#             if len(option) == 0:
#                 return index, True
#     print('expecting ' + str(expecting))
#     textExpected, textExpectedAt = isTextExpected(token, expecting)
#     typeExpected, typeExpectedAt = isTypeExpected(token, expecting)
#     #print(token.type + ' ' + token.text)
#     if token.text == 'import' and expecting is None:
#         index += 1
#         parseToken(tokens[index], tokens, index, [['STRING_LIT']])
#     elif token.text == 'class' and expecting is None:
#         print('class declerartion')
#         index += 1
#         parseToken(tokens[index], tokens, index, [['IDENTIFIER', 'parameter_list', 'do', 'statements', 'end', 'class']])
#     elif token.text == 'do' and textExpected:
#         print('do something')
#         index += 1
#         del expecting[textExpectedAt][0]
#         parseToken(tokens[index], tokens, index, expecting)
#     elif token.type == 'IDENTIFIER' and typeExpected and not expecting is None:
#         print('identifier ' + token.text)
#         index += 1
#         del expecting[typeExpectedAt][0]
#         parseToken(tokens[index], tokens, index, expecting)
#     elif token.type == 'DELIM' and textExpected and not expecting is None:
#         print('delimeter ' + token.text)
#         index += 1
#         del expecting[textExpectedAt][0]
#         parseToken(tokens[index], tokens, index, expecting)
#     else:
#         print('not expected')
#         return index, False
#     return index, True


# def scanTokens(tokens, rules):
#     # scan tokens until the left-most terminal is found
#     index = 0
#     while index < len(tokens):
#         token = tokens[index]
#         # compare whether the token equals the rhs of some rule
#         expandToken(tokens, index)
#         break
#             # if len(rule.rhs) == 1 and rule.rhs[0] == getInTerminalForm(token):
#             #     print('found matching rule: ' + token.text)
#             #     # TODO - return to the beginning to scan for the next left-most terminal
#
#         # move on to the next token
#         index += 1
#
# def expandToken(tokens, index):
#     token = tokens[index]
#     for rule in rules:
#         if rule.lhs == getInTerminalForm(token):
#             print('found: ' + rule.lhs)
#         else:
#             expandToken('')
#
# def getInTerminalForm(token):
#     if token.tokenType == 'IDENTIFIER' or token.tokenType == 'STRING_LIT' or token.tokenType == 'NUMBER_LIT':
#         return token.tokenType
#     else:
#         return token.tokenType + '=' + token.text
