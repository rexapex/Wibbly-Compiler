"""Copyright © James Sugden 2018"""

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

def genParseTree(tokens, tokenTypes):
    # comments are irrelevant
    for tok in tokens:
        if tokenTypes[tok[0]] == 'LINE_COMMENT':
            tokens.remove(tok)
    for tok in tokens:
        print(tokenTypes[tok[0]] + ':       ' + tok[2])
    # get a list of available rules (productions)
    rules = getRules()
    # shift and reduce (bottom up parser)
    print('\n\n\nSyntax Parser')
    for tokIndex in range(len(tokens)):
        tok = tokens[tokIndex]
        tokType = tokenTypes[tok[0]]
        for rule in rules:
            doesRuleMatch(tokIndex, tokType, rule, tokens)

# def expandNode(rules, node):
#     nodeFullyExpanded = True   # set to false if at least one rule exists which can be applied to the node
#     for rule in rules:
#         if rule.lhs == node.value:
#             nodeFullyExpanded = False
#
#             return expandNode()

def doesRuleMatch(tokenIndex, tokenType, rule, tokens):
    token = tokens[tokenIndex]
    if tokenType == 'KEYWORD':
        val = tokenType + '=' + token[2]    # token[2] contains the keyword name
        #print('found ' + val)
        for comp in rule.rhs:
            if comp == val:
                # the keyword appears in the rhs of rule, therefore, look ahead and see if rule is fully compatible
                rhs = list(rule.rhs)
                rhs.remove(comp)
                lookAhead(rhs, tokens, tokenIndex + 1)

def lookAhead(rhs, tokens, startIndex):
    newTokens = list(tokens)
    print('looking ahead')
    for i in range(startIndex, len(tokens)):
        for rule in rules:
            doesRuleMatch(i, tokenTypes[tokens[i][0]], rule, tokens)
    return newTokens

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
