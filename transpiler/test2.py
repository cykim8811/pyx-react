
from lark import Lark
from lark.tree import Tree

l = Lark(r"""
start: _code
_code: (pyx _code) | (/./ _code) | _END

pyx_code: _pyx_code

_pyx_code:
    | _python_string _pyx_code
    | _text_not_braces _pyx_code

_text_not_braces: /[^{}]/

pyx: pyx_open

pyx_open: (/</ pyx_tag_name pyx_attrs* />/ body)

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
    | pyx_close

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
    return f"createElement(\"{tag_name}\", {visit_pyx_attrs(node)}, {visit_body(node)})"

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
                        print(child.data)
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
    for t in node.find_data("pyx_text"):
        return f"\"{_reconstruct(t)}\""
    for t in node.find_data("pyx_code"):
        return _reconstruct(t)

def postprocess(s):
    s = s.replace("$NL", "\n")
    s = s.replace("$TAB", "\t")
    s = s.replace("$SPACE", " ")
    s = s.replace("$END", "")
    return s

res = l.parse(preprocess("""
class Counter:
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1
    
    def __render__(self, user):
        return <div>
            <p>Count: {self.count}</p>
            <button onClick={self.increment}>Increment</button>
        </div>
"""))


print(reconstruct(res))


from pyx import App, createElement

class TextAPP(App):
    def __render__(self, user):
        return createElement('pre', {}, res.pretty())

app = TextAPP()
app.run(host='0.0.0.0', port=7002)

