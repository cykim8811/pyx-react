

from lark import Lark
from lark.tree import Tree

l = Lark(r"""
start: _code
_code: (pyx _code) | (/[^<$]+/ _code) | (/./ _code) | _END

pyx_code: _pyx_code

_pyx_code:
    | _python_string _pyx_code
    | pyx _pyx_code
    | /{/ _pyx_code /}/ _pyx_code
    | _text_before_braces
    | _text_multiple _pyx_code  # Might be unstable
    # | _text_not_braces _pyx_code

_text_multiple: /[^{}<]+/

_text_not_braces: /[^{}]/

_text_before_braces: /[^}](?!})/

pyx: pyx_open

pyx_open:
    | (/</ pyx_tag_name pyx_attrs* />/ body pyx_close)
    | (/</ pyx_tag_name pyx_attrs* /\/>/)

pyx_tag_name: NAME

pyx_attrs: WS? pyx_attr_name /=/ pyx_attr_value

pyx_attr_value:
    | string
    | "{" pyx_code "}"

pyx_attr_name: NAME

body: _body

_body:
    | pyx _body
    | body_value _body

body_value:
    | "{" pyx_code "}"
    | pyx_text

pyx_close: /<\// NAME />/
pyx_text: /[^<{]+/

string:
    | /f?"(?:[^"\\]|\\.)*"/
    | /f?'(?:[^'\\]|\\.)*'/

NAME: /[a-zA-Z_][a-zA-Z0-9_\-]*/

_END: "$END"

WS: (/\$TAB/ | /\$NL/ | /\$SPACE/)

_python_string:
    | string
    | python_multiline_string

python_multiline_string:
    | /f?\'\'\'(?:[^'\\]|\\.)*\'\'\'/
    | /f?\"\"\"(?:[^"\\]|\\.)*\"\"\"/

""")

def preprocess(s):
    s = s.replace("\n", "$NL")
    s = s.replace("\r", "")
    s = s.replace("\t", "$TAB")
    s = s.replace(" ", "$SPACE")
    s += "$END"
    return s

def reconstruct(node):
    return postprocess(_reconstruct(node))

def _reconstruct(node):
    if type(node) is Tree and node.data == "pyx":
        return visit_pyx(node)
    if isinstance(node, Tree):
        return "".join(_reconstruct(c) for c in node.children)
    else:
        return str(node)

def visit_pyx(node):
    tag_name = None
    for t in node.find_data("pyx_tag_name"):
        tag_name = _reconstruct(t)
    return f"pyx.createElement(\"{tag_name}\", {visit_pyx_attrs(node)}, {visit_body(node)})"

def visit_pyx_attrs(node):
    attrs = []
    for t in node.find_data("pyx_attrs"):
        attr_name = f'"{_reconstruct(next(t.find_data("pyx_attr_name")))}"'
        attr_value = _reconstruct(next(t.find_data("pyx_attr_value")))
        attrs.append(f"{attr_name}: {attr_value}")
        
    return "{" + ", ".join(attrs) + "}"

def visit_body(node):
    return "[" + ", ".join(_visit_body(node)) + "]"

def _visit_body(node):
    body = []
    for t in node.children:
        if isinstance(t, Tree):
            if t.data == "body":
                for child in t.children:
                    if isinstance(child, Tree):
                        if child.data == "pyx":
                            body.append(visit_pyx(child))
                        elif child.data == "body_value":
                            body.append(visit_body_value(child))
                        elif child.data == "pyx_close":
                            pass
                        else:
                            raise Exception(f"Unknown body child {child.data}")
                    else:
                        body.append(_reconstruct(child))
            else:
                body += _visit_body(t)
    return body

def visit_body_value(node):
    if node.children[0].data == "pyx_code":
        return visit_pyx_code(node.children[0])
    elif node.children[0].data == "pyx_text":
        rec = _reconstruct(node.children[0])
        rec = rec.replace("$NL", "\\n")
        return f"\"{rec}\""
    else:
        raise Exception(f"Unknown body_value child {node.children[0].data}")

def visit_pyx_code(node):
    return _reconstruct(node)

def postprocess(s):
    s = s.replace("$NL", "\n")
    s = s.replace("$TAB", "\t")
    s = s.replace("$SPACE", " ")
    s = s.replace("$END", "")
    return s


def transpile_string(s):
    tree = l.parse(preprocess(s))
    print(tree.pretty())
    return reconstruct(tree)


import os
import argparse

def transpile_path():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs='?', type=str, help="path to transpile", default=".")
    args = parser.parse_args()
    
    pyx_files = []
    if os.path.isfile(args.path):
        if args.path.endswith(".pyx"):
            pyx_files.append(args.path)
    elif os.path.isdir(args.path):
        for root, dirs, files in os.walk(args.path):
            for file in files:
                if file.endswith(".pyx"):
                    pyx_files.append(os.path.join(root, file))

    filecount_format_length = len(str(len(pyx_files)))

    for i, pyx_file in enumerate(pyx_files):
        idx = f"[{i+1:>{filecount_format_length}}/{len(pyx_files)}]"
        print(f"{idx} Transpiling {pyx_file} ...", end=" ")
        with open(pyx_file, "r") as f:
            code = f.read()
        
        transpiled_code = transpile_string(code)
        
        py_file = pyx_file[:-4] + ".x.py"
        with open(py_file, "w") as f:
            f.write(transpiled_code)
        print(f"Done. Transpiled code is saved at {py_file}")


