"""Copyright © James Sugden 2018"""

class Rule:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

def genParseTree(tokens, tokenTypes):
    # define a set of rules (productions)
    rules = []
    # creating a list of global statements from a program
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
    # an expression is any statement which returns a value
    rules.append(Rule(''))

    return
