
from lark import Lark

from lark.indenter import PythonIndenter
from lark import Token, Lark, Tree
from lark.reconstruct import Reconstructor
from lark.visitors import Transformer

py3_parser = Lark.open_from_package(
    'lark',
    'python.lark',
    ['grammars'],
    parser='lalr',
    postlex=PythonIndenter(),
    start='file_input',
    maybe_placeholders=False
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
                        Token("RULE", "string"),
                        [Token("STRING", f"'{key}'")]
                    ),
                    Tree("const_true", []),
                ],
            )
        elif isinstance(args[1], Tree):
            return Tree(
                Token("RULE", "key_value"),
                [
                    Tree(
                        Token("RULE", "string"),
                        [Token("STRING", f"'{key}'")]
                    ),
                    args[1].children[0],
                ],
            )
        else:
            return Tree(
                Token("RULE", "key_value"),
                [
                    Tree(
                        Token("RULE", "string"),
                        [Token("STRING", f"'{key}'")]
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
        print(args)
        str_value = ''.join(args)
        # Escape as html string
        str_value = str_value.replace('\\', '\\\\')
        str_value = str_value.replace('"', '\\"')
        str_value = str_value.replace("'", "\\'")
        str_value = str_value.replace('\n', '\\n')
        str_value = str_value.replace('\r', '\\r')
        str_value = str_value.replace('\t', '\\t')
        str_value = str_value.replace('\b', '\\b')
        str_value = str_value.replace('\f', '\\f')

        return Tree(
            Token("RULE", "string"),
            [Token("STRING", f"'{str_value}'")]
        )
    
    def pyx_child(self, args):
        return args[0]
    
    def pyx_child_python_expr(self, args):
        return args[0]


kwargs = dict(postlex=PythonIndenter(), start='file_input', maybe_placeholders=False)
pyx_parser = Lark(open("pyx.lark"), parser='lalr', **kwargs)

pyx_to_py = PyxToPy()
py3_reconstructor = PythonReconstructor(py3_parser)


def transpile_string(code):
    pyx_tree = pyx_parser.parse(code)
    py3_tree = pyx_to_py.transform(pyx_tree)
    print(py3_tree.pretty())
    code = py3_reconstructor.reconstruct(py3_tree)
    return code


import os

pyx_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".pyx"):
            pyx_files.append(os.path.join(root, file))


for pyx_file in pyx_files:
    with open(pyx_file, "r") as f:
        code = f.read()
    
    transpiled_code = transpile_string(code)
    
    py_file = pyx_file[:-4] + ".x.py"
    with open(py_file, "w") as f:
        f.write(transpiled_code)

