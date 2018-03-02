"""Syntax parser of the Wibbly language compiler"""
"""Visit our webstite at www.origamisheep.com"""

import sys
# import networkx as nx
# import matplotlib.pyplot as plt

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

class Node:
    def __init__(self):
        self.children = []
        self.parent = None

class TerminalNode(Node):
    def __init__(self, token):
        Node.__init__(self)
        self.token = token

class NonTerminalNode(Node):
    def __init__(self, name):
        Node.__init__(self)
        self.name = name

# WibblyParser is a LL(2) Top-Down Syntax Parser
class WibblyParser:
    def __init__(self):
        self.rootNode = None
        self.lookahead = None
        self.lookahead2 = None
        self.symbolTable = None
        self.tokens = None
        self.tokenIndex = 0
        self.terminals = ['IDENTIFIER', 'STRING_LIT', 'NUMBER_LIT', '(', ')', '.', ',', '"', '\'', '<=', '>=', '=', '<', '>', 'if', 'else', 'then', 'while', 'for', 'in', 'break', 'continue']
        self.terminals += ['return', 'do', 'end', 'wibbly', 'wobbly', 'true', 'false', 'empty', 'class', 'module', 'get', 'set', 'int', 'big', 'float', 'string', 'bool', 'func', 'me', 'import']

    def parse(self, tokens, symbolTable):
        self.tokens = tokens

        # remove all comments since they are irrelevant
        for tok in tokens:
            if tok.type == 'LINE_COMMENT':
                self.tokens.remove(tok)

        self.tokenIndex = 0
        self.rootNode = NonTerminalNode('root')
        self.currentNode = self.rootNode
        self.symbolTable = symbolTable

        # parse the token stream
        print('\nSyntax Parser')
        if len(tokens) > 0:
            self.lookahead, self.lookahead2 = self.nextTerminal()
            self.globalStatements(self.rootNode)
        self.done()

    def nextToken(self):
        self.tokenIndex += 1
        if self.tokenIndex >= len(self.tokens):
            self.done()

    def nextTerminal(self):
        if self.tokenIndex < len(self.tokens) - 1:
            return self.tokens[self.tokenIndex], self.tokens[self.tokenIndex+1]
        elif self.tokenIndex < len(self.tokens):
            return self.tokens[self.tokenIndex], None
        self.done()

    # match any number of global statements consecutively
    def globalStatements(self, parentNode):
        self.globalStatement(parentNode)
        if self.lookahead.text == 'import' or self.lookahead.text == 'class' or self.lookahead.text == 'module':
            self.globalStatements(parentNode)

    # match the non-terminal globalStatement
    def globalStatement(self, parentNode):
        if self.lookahead.text == 'import':
            self.importStatement(parentNode)
        elif self.lookahead.text == 'class':
            self.classDefinition(parentNode)
        elif self.lookahead.text == 'module':
            self.moduleDefinition(parentNode)
        return None

    def importStatement(self, parentNode):
        importNode = NonTerminalNode('import_statement')
        self.match('import', importNode)
        self.match('STRING_LIT', importNode)
        parentNode.children.append(importNode)

    def classDefinition(self, parentNode):
        classNode = NonTerminalNode('class_definition')
        self.match('class', classNode)
        self.match('IDENTIFIER', classNode)
        self.parameterList(classNode)
        self.block(classNode)
        self.match('class', classNode)
        parentNode.children.append(classNode)

    def moduleDefinition(self, parentNode):
        moduleNode = NonTerminalNode('module_definition')
        self.match('module', moduleNode)
        self.match('IDENTIFIER', moduleNode)
        self.block(moduleNode)
        self.match('module', moduleNode)
        parentNode.children.append(moduleNode)

    def block(self, parentNode):
        blockNode = NonTerminalNode('block')
        self.match('do', blockNode)
        self.statements(blockNode)
        self.match('end', blockNode)
        parentNode.children.append(blockNode)

    def statements(self, parentNode):
        isEmpty = self.statement(parentNode)
        if isEmpty is None:
            self.statements(parentNode)

    def statement(self, parentNode):
        if self.lookahead.text == 'func':
            self.functionDecleration(parentNode)
        elif self.lookahead.text == 'for':
            self.forLoop(parentNode)
        elif self.lookahead.text == 'while':
            self.whileLoop(parentNode)
        elif self.lookahead.text == 'var':
            self.complexVariableDecleration(parentNode)
        elif self.lookahead.type == 'IDENTIFIER':
            self.complexIdentifierStatement(parentNode)
        elif self.lookahead.type == 'NUMBER_LIT' or self.lookahead.type == 'STRING_LIT' or self.lookahead.text == 'wibbly':
            self.expression(parentNode)
        else:
            return True

    def wibblyFunctionCall(self, parentNode):
        node = NonTerminalNode('wibbly_function_call')
        self.match('wibbly', node)
        self.complexIdentifier(node)
        self.argumentList(node)
        parentNode.children.append(node)

    def forLoop(self, parentNode):
        pass

    def whileLoop(self, parentNode):
        pass

    #def functionCall(self):
    #    if self.lookahead.text == 'wibbly':
    #        self.match('wibbly')
    #    self.complexIdentifier()
    #    self.argumentList()

    def argumentList(self, parentNode):
        argListNode = NonTerminalNode('argument_list')
        self.match('(', argListNode)
        if self.lookahead.text != ')':  # doesn't have to be any arguments in the list
            self.expressions(argListNode)
        self.match(')', argListNode)
        parentNode.children.append(argListNode)

    def functionDecleration(self, parentNode):
        funcDeclNode = NonTerminalNode('function_decleration')
        if self.lookahead.text == 'wibbly':
            self.match('wibbly', funcDeclNode)
        self.match('func', funcDeclNode)
        if self.lookahead.type == 'IDENTIFIER':   # optional function identifier (anonymous functions possible)
            self.complexIdentifier(funcDeclNode)
        self.parameterList(funcDeclNode)
        self.block(funcDeclNode)
        self.match('func', funcDeclNode)
        parentNode.children.append(funcDeclNode)

    # match the non-terminal parameterList
    def parameterList(self, parentNode):
        paramListNode = NonTerminalNode('parameter_list')
        self.match('(', paramListNode)
        self.simpleVariablesDeclerations(paramListNode)
        self.match(')', paramListNode)
        parentNode.children.append(paramListNode)

    def simpleVariablesDeclerations(self, parentNode):
        if self.lookahead.type == 'IDENTIFIER':     # list could be empty
            self.simpleVariablesDecleration(parentNode)
            if self.lookahead.text == ',':
                self.match(',', parentNode)
                self.simpleVariablesDeclerations(parentNode)

    def simpleVariablesDecleration(self, parentNode):
        varDecl = NonTerminalNode('simple_variable_decleration')
        self.match('IDENTIFIER', varDecl)
        if self.lookahead.text == ':':  # variable has optional type
            self.typeDecleration(varDecl)
        if self.lookahead.text == '=':  # variable has optional assignment
            self.variableAssignment(varDecl)
        parentNode.children.append(varDecl)

    def complexVariableDecleration(self, parentNode):
        varDecl = NonTerminalNode('complex_variable_decleration')
        self.match('var', varDecl)
        self.match('IDENTIFIER', varDecl)
        if self.lookahead.text == ':':  # variable has optional type
            self.typeDecleration(varDecl)
        if self.lookahead.text == '=':  # variable has optional assignment
            self.variableAssignment(varDecl)
        parentNode.children.append(varDecl)

    def complexIdentifier(self, parentNode):
        idNode = NonTerminalNode('complex_identifier')
        self.match('IDENTIFIER', idNode)
        if(self.lookahead.text == '.'):
            self.match('.', idNode)
            self.complexIdentifier(idNode)
        parentNode.children.append(idNode)

    def typeDecleration(self, parentNode):
        typeDecl = NonTerminalNode('type_decleration')
        self.match(':', typeDecl)
        self.variableType(typeDecl)
        parentNode.children.append(typeDecl)

    # returns true iff the next token is an assignment
    def variableAssignment(self, parentNode):
        asgNode = NonTerminalNode('variable_assignment')
        if self.lookahead.text == '=':
            self.match('=', asgNode)
            self.expression(asgNode)
        elif self.lookahead.text == '+=':
            self.match('+=', asgNode)
            self.expression(asgNode)
        elif self.lookahead.text == '-=':
            self.match('-=', asgNode)
            self.expression(asgNode)
        elif self.lookahead.text == '*=':
            self.match('*=', asgNode)
            self.expression(asgNode)
        elif self.lookahead.text == '/=':
            self.match('/=', asgNode)
            self.expression(asgNode)
        elif self.lookahead.text == '%=':
            self.match('%=', asgNode)
            self.expression(asgNode)
        elif self.lookahead.text == '++':
            self.match('++', asgNode)
        elif self.lookahead.text == '--':
            self.match('--', asgNode)
        else:
            return False
        parentNode.children.append(asgNode)
        return True

    def variableType(self, parentNode):
        typeNode = NonTerminalNode('variable_type')
        self.variableModifier(typeNode)
        if self.lookahead.type == 'IDENTIFIER':      # type could be a class in which case the text will be an identifier
            self.match('IDENTIFIER', typeNode)
        elif self.lookahead.text == 'int':
            self.match('int', typeNode)
        elif self.lookahead.text == 'float':
            self.match('float', typeNode)
        elif self.lookahead.text == 'string':
            self.match('string', typeNode)
        elif self.lookahead.text == 'bool':
            self.match('bool', typeNode)
        elif self.lookahead.text == 'event':
            self.match('event', typeNode)
        parentNode.children.append(typeNode)

    def variableModifier(self, parentNode):
        if self.lookahead.text == 'big':             # modifier is either big or nothing
            self.match('big', parentNode)

    def expressions(self, parentNode):
        self.expression(parentNode)
        if self.lookahead.text == ',':      # more than 1 expression
            self.match(',', parentNode)
            self.expressions(parentNode)

    def complexIdentifierStatement(self, parentNode):   # a  statement beginning with a complex identifier
        complNode = NonTerminalNode('complex_identifier_statement')
        self.complexIdentifier(complNode)
        isAssignment = self.variableAssignment(complNode)
        if isAssignment == False:
            self.expression(complNode)
        parentNode.children.append(complNode)

    def expression(self, parentNode):
        exprNode = NonTerminalNode('expression')
        if self.lookahead.text == '+':      # add
            self.expressionLeaf(exprNode)
            self.match('+', exprNode)
            self.expression(exprNode)
        elif self.lookahead.text == '-':    # subtract
            self.expressionLeaf(exprNode)
            self.match('-', exprNode)
            self.expression(exprNode)
        elif self.lookahead.text == '*':    # multiply
            self.expressionLeaf(exprNode)
            self.match('*', exprNode)
            self.expression(exprNode)
        elif self.lookahead.text == '/':    # divide
            self.expressionLeaf(exprNode)
            self.match('/', exprNode)
            self.expression(exprNode)
        elif self.lookahead.text == '**':
            self.expressionLeaf(exprNode)
            self.match('**', exprNode)
            self.expression(exprNode)
        elif self.lookahead.text == '%':    # remainder
            self.expressionLeaf(exprNode)
            self.match('%', exprNode)
            self.expression(exprNode)
        elif self.lookahead.text == '%%':   # integer divide
            self.expressionLeaf(exprNode)
            self.match('%', exprNode)
            self.expression(exprNode)
        elif self.lookahead.text == '==':
            self.expressionLeaf(exprNode)
            self.match('==', exprNode)
            self.expression(exprNode)
        elif self.lookahead.text == '!=':
            self.expressionLeaf(exprNode)
            self.match('!=', exprNode)
            self.expression(exprNode)
        elif self.lookahead.text == '<':
            self.expressionLeaf(exprNode)
            self.match('<', exprNode)
            self.expression(exprNode)
        elif self.lookahead.text == '>':
            self.expressionLeaf(exprNode)
            self.match('>', exprNode)
            self.expression(exprNode)
        elif self.lookahead.text == '<=':
            self.expressionLeaf(exprNode)
            self.match('<=', exprNode)
            self.expression(exprNode)
        elif self.lookahead.text == '>=':
            self.expressionLeaf(exprNode)
            self.match('>=', exprNode)
            self.expression(exprNode)
        elif self.lookahead.text == '~==':
            self.expressionLeaf(exprNode)
            self.match('~==', exprNode)
            self.expression(exprNode)
        else:
            self.expressionLeaf(exprNode)
        parentNode.children.append(exprNode)

    def expressionLeaf(self, parentNode):
        leafNode = NonTerminalNode('expression_leaf')
        if self.lookahead.text == 'wibbly':        # must be a wibbly function call
            self.wibblyFunctionCall(leafNode)
        elif self.lookahead.type == 'STRING_LIT':
            self.match('STRING_LIT', leafNode)
        elif self.lookahead.type == 'NUMBER_LIT':
            self.match('NUMBER_LIT', leafNode)
        elif self.lookahead.text == '(':
            self.argumentList(leafNode)
        if self.lookahead.text == 'as':
            self.variableCast(leafNode)
        parentNode.children.append(leafNode)

    def variableCast(self, parentNode):
        castNode = NonTerminalNode('variable_cast')
        self.match('as', castNode)
        self.variableType(castNode)
        parentNode.children.append(castNode)

    # match a terminal
    def match(self, terminal, parentNode):
        if self.lookahead.text == terminal or ((self.lookahead.type == 'IDENTIFIER' or self.lookahead.type == 'STRING_LIT' or self.lookahead.type == 'NUMBER_LIT') and terminal == self.lookahead.type):
            print('matched ' + terminal)
            node = TerminalNode(self.tokens[self.tokenIndex])
            parentNode.children.append(node)
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
        #print('\nParse Tree')
        #self.printTree(self.rootNode)
        #print()
        #self.makeTree(self.rootNode)

        if self.tokenIndex < len(self.tokens):
            raise SyntaxInvalidException()
        else:
            raise SyntaxValidException()

    # def makeTree(self, rootNode):
    #     G = nx.Graph()
    #     self.addNode(G, rootNode, 0)
    #     pos = nx.spring_layout(G)
    #     #nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_color = values, node_size = 500)
    #     nx.draw_networkx_labels(G, pos)
    #     #nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color='r', arrows=True)
    #     #nx.draw_networkx_edges(G, pos, edgelist=black_edges, arrows=False)
    #     plt.show()
    #
    # def addNode(self, graph, parentNode, nodeIndex):
    #     for child in parentNode.children:
    #         graph.add_edge(nodeIndex, nodeIndex+1)
    #         nodeIndex = self.addNode(graph, child, nodeIndex + 1)
    #     return nodeIndex
    #
    # def printTree(self, rootNode):
    #     for child in rootNode.children:
    #         if isinstance(child, NonTerminalNode):
    #             print(child.name, end=' ')
    #         else:
    #             print(child.token.type, end=' ')
    #     print()
    #     for child in rootNode.children:
    #         self.printTree(child)

# def getRules():
#     # define a set of rules (productions)
#     rules = []
#     # a file is list of global statements
#     rules.append(Rule('file', ['glob_statements']))
#     # a global statements can be one or more global statements
#     rules.append(Rule('glob_statements', ['glob_statements', 'glob_statement']))
#     rules.append(Rule('glob_statements', ['glob_statement']))
#     # a global statement can be an import statement or an encapsulator
#     rules.append(Rule('glob_statement', ['import_statement']))
#     rules.append(Rule('glob_statement', ['encapsulator']))
#     # an encapsulator is can only be a class statement in the current version
#     rules.append(Rule('encapsulator', ['class_statement']))
#     # a class is made of the class keyword, followed by a name followed by a parameter list followed by do, followed by any number of statements followed by end class
#     rules.append(Rule('class_statement', ['KEYWORD=class', 'IDENTIFIER', 'parameter_list', 'KEYWORD=do', 'statements', 'KEYWORD=end', 'KEYWORD=class']))
#     # a parameter list is a list of variable declerations enclosed by parentheses
#     rules.append(Rule('parameter_list', ['DELIM=(', 'variable_declerations', 'DELIM=)']))
#     # a variable declerations is a list of comma separated variable declerations or a single variable decleration
#     rules.append(Rule('variable_declerations', ['variable_declerations', 'DELIM=,', 'variable_decleration']))
#     rules.append(Rule('variable_declerations', ['variable_decleration']))
#     # a variable decleration has an identifier, and optionally has a type
#     rules.append(Rule('variable_decleration', ['IDENTIFIER']))
#     rules.append(Rule('variable_decleration', ['IDENTIFIER', 'DELIM=:', 'variable_type']))
#     # a variable assignment assigns an the value of an expression to a variable
#     rules.append(Rule('variable_assignment', ['variable_decleration', 'BIN_OP==', 'expr']))
#     # a statements can be one statement or many statements
#     rules.append(Rule('statements', ['statements', 'statement']))
#     rules.append(Rule('statements', ['statement']))
#     # a statement can be many things
#     rules.append(Rule('statement', ['variable_decleration']))
#     rules.append(Rule('statement', ['variable_assignment']))
#     rules.append(Rule('statement', ['func_definition']))
#     # a function definition is the following... (a function can be named or anonymous)
#     rules.append(Rule('func_definition', ['KEYWORD=func', 'parameter_list', 'KEYWORD=do', 'statements', 'KEYWORD=end', 'KEYWORD=func']))
#     rules.append(Rule('func_definition', ['KEYWORD=func', 'IDENTIFIER', 'parameter_list', 'KEYWORD=do', 'statements', 'KEYWORD=end', 'KEYWORD=func']))
#     # an expression is any statement which returns a value
#     rules.append(Rule('expr', ['string_expr']))
#     rules.append(Rule('expr', ['number_expr']))
#     rules.append(Rule('expr', ['func_call']))
#     # a function call is a function name followed by and argument list
#     rules.append(Rule('func_call', ['IDENTIFIER', 'arg_list']))
#     # an argument list is a list of expressions enclosed in parentheses
#     rules.append(Rule('arg_list', ['DELIM=(', 'expr_list', 'DELIM=)']))
#     # an expression list is a list of expressions separated by commas or a single expression
#     rules.append(Rule('expr_list', ['expr_list', 'DELIM=,', 'expr']))
#     rules.append(Rule('expr_list', ['expr']))
#     # a string expression can be a string literal or multiple string literals appended together
#     rules.append(Rule('string_expr', ['string_expr', 'BIN_OP=+', 'STRING_LIT']))
#     rules.append(Rule('string_expr', ['STRING_LIT']))
#     # a number expression can be a number literal or an algebraic expression
#     rules.append(Rule('number_expr', ['NUMBER_LIT']))
#     rules.append(Rule('number_expr', ['algebraic_expr']))
#     # an algebraic expression is what you think...
#     return rules

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
