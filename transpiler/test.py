
from lark import Lark

from lark.indenter import PythonIndenter
from lark import Token, Lark, Tree
from lark.reconstruct import Reconstructor
from lark.indenter import PythonIndenter

# Official Python grammar by Lark
python_parser3 = Lark.open_from_package('lark', 'python.lark', ['grammars'],
                                        parser='lalr', postlex=PythonIndenter(), start='file_input',
                                        maybe_placeholders=False    # Necessary for reconstructor
                                        )

SPACE_AFTER = set(',+-*/~@<>="|:')
SPACE_BEFORE = (SPACE_AFTER - set(',:')) | set('\'')


def special(sym):
    return Token('SPECIAL', sym.name)

def postproc(items):
    stack = ['\n']
    actions = []
    last_was_whitespace = True
    for item in items:
        if isinstance(item, Token) and item.type == 'SPECIAL':
            actions.append(item.value)
        else:
            if actions:
                assert actions[0] == '_NEWLINE' and '_NEWLINE' not in actions[1:], actions

                for a in actions[1:]:
                    if a == '_INDENT':
                        stack.append(stack[-1] + ' ' * 4)
                    else:
                        assert a == '_DEDENT'
                        stack.pop()
                actions.clear()
                yield stack[-1]
                last_was_whitespace = True
            if not last_was_whitespace:
                if item[0] in SPACE_BEFORE:
                    yield ' '
            yield item
            last_was_whitespace = item[-1].isspace()
            if not last_was_whitespace:
                if item[-1] in SPACE_AFTER:
                    yield ' '
                    last_was_whitespace = True
    yield "\n"


class PythonReconstructor:
    def __init__(self, parser):
        self._recons = Reconstructor(parser, {'_NEWLINE': special, '_DEDENT': special, '_INDENT': special})

    def reconstruct(self, tree):
        return self._recons.reconstruct(tree, postproc)

kwargs = dict(postlex=PythonIndenter(), start='file_input', maybe_placeholders=False)
parser = Lark(open("pyx.lark"), parser='lalr', **kwargs)

with open("example.pyx", "r") as f:
    code = f.read()

tree = parser.parse(code)

from lark.visitors import Transformer

class PyxToPy(Transformer):
    def pyx(self, args):
        tree_tag = args[0]
        tree_attr_dict = args[1]
        tree_child = args[2].children
        
        return Tree(
            "funccall",
            [
                Tree(
                    "getattr",
                    [
                        Tree(
                            "var",
                            [
                                Tree(Token("RULE", "name"), [Token("NAME", "pyx")])
                            ],
                        ),
                        Tree(Token("RULE", "name"), [Token("NAME", "createElement")]),
                    ],
                ),
                Tree(
                    Token("RULE", "arguments"),
                    [
                        tree_tag,
                        tree_attr_dict,
                        *tree_child,
                    ],
                ),
            ],
        )


    
    def pyx_tag(self, args):
        return Tree(Token("RULE", "string"), [Token("STRING", f"'{args[0].value}'")])
    
    def pyx_attr(self, args):
        key = args[0].value
        if len(args) == 1:
            return Tree(
                Token("RULE", "key_value"),
                [
                    Tree(
                        "var",
                        [
                            Tree(
                                Token("RULE", "name"),
                                [Token("NAME", key)],
                            )
                        ],
                    ),
                    Tree("const_true", []),
                ],
            )
        elif isinstance(args[1], Tree):
            return Tree(
                Token("RULE", "key_value"),
                [
                    Tree(
                        "var",
                        [
                            Tree(
                                Token("RULE", "name"),
                                [Token("NAME", key)],
                            )
                        ],
                    ),
                    args[1].children[0],
                ],
            )
        else:
            return Tree(
                Token("RULE", "key_value"),
                [
                    Tree(
                        "var",
                        [
                            Tree(
                                Token("RULE", "name"),
                                [Token("NAME", key)],
                            )
                        ],
                    ),
                    Tree(
                        Token("RULE", "string"),
                        [args[1]],
                    ),
                ],
            )
        
    def pyx_attr_list(self, args):
        return Tree(
            "dict",
            args
        )
    
    def pyx_text(self, args):
        return Tree(
            Token("RULE", "string"),
            [Token("STRING", f"'{args[0].value}'")],
        )
    
    def pyx_child(self, args):
        return args[0]
    
    def pyx_child_python_expr(self, args):
        return args[0]



pyx_to_py = PyxToPy()
tree = pyx_to_py.transform(tree)

# Rebuild code
code = PythonReconstructor(python_parser3).reconstruct(tree)
print(code)

