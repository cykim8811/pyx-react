from parsimonious.grammar import Grammar

# General grammatical elements and rules:
#
# * Strings with double quotes (") denote SOFT KEYWORDS
# * Strings with single quotes (') denote KEYWORDS
# * Upper case names (NAME) denote tokens in the Grammar/Tokens file
# * Rule names starting with "invalid_" are used for specialized syntax errors
#     - These rules are NOT used in the first pass of the parser.
#     - Only if the first pass fails to parse, a second pass including the invalid
#       rules will be executed.
#     - If the parser fails in the second phase with a generic syntax error, the
#       location of the generic failure of the first pass will be used (this avoids
#       reporting incorrect locations due to the invalid rules).
#     - The order of the alternatives involving invalid rules matter
#       (like any rule in PEG).
#
# Grammar Syntax (see PEP 617 for more information):
#
# rule_name: expression
#   Optionally, a type can be included right after the rule name, which
#   specifies the return type of the C or Python function corresponding to the
#   rule:
# rule_name[return_type]: expression
#   If the return type is omitted, then a void * is returned in C and an Any in
#   Python.
# e1 e2
#   Match e1, then match e2.
# e1 | e2
#   Match e1 or e2.
#   The first alternative can also appear on the line after the rule name for
#   formatting purposes. In that case, a | must be used before the first
#   alternative, like so:
#       rule_name[return_type]:
#            | first_alt
#            | second_alt
# ( e )
#   Match e (allows also to use other operators in the group like '(e)*')
# [ e ] or e?
#   Optionally match e.
# e*
#   Match zero or more occurrences of e.
# e+
#   Match one or more occurrences of e.
# s.e+
#   Match one or more occurrences of e, separated by s. The generated parse tree
#   does not include the separator. This is otherwise identical to (e (s e)*).
# &e
#   Succeed if e can be parsed, without consuming any input.
# !e
#   Fail if e can be parsed, without consuming any input.
# ~
#   Commit to the current alternative, even if it fails to parse.
#

peg_grammar = Grammar(r"""
    file = whitespace? (rule / comment)* whitespace?

    comment = "#" ~"[^\n]*" newline?

    rule = rule_name whitespace? ":" whitespace? expression whitespace? newline?

    rule_name = ~"[a-zA-Z_][a-zA-Z_0-9]*"

    expression = sequence (whitespace? "/" whitespace? sequence)*

    sequence = prefix*

    prefix = ("&" / "!" / "~")? suffix

    suffix = primary ("*" / "+" / "?")?

    primary = rule_name / string / ("(" whitespace? expression whitespace? ")")

    string = "\"" (~"\"" / "\\\"")* "\""

    whitespace = ~"\s+"

    newline = ~"[\r\n]+"
"""

)

# 예제 사용
example_peg = """
rule: expression
# comment

# another comment
    
"""

parsed = peg_grammar.parse(example_peg)
print(parsed)

