

from lark import Lark

l = Lark(r'''
?start: (pyx | code | WS)*

pyx.1:
    | pyx_tag_start pyx_tag_end
    | pyx_tag_start pyx_body? pyx_tag_end
    | pyx_tag_self_closing

pyx_tag_start: /</ pyx_tag_name pyx_attrs? />/

pyx_tag_end: /<\// pyx_tag_name />/

pyx_tag_self_closing: /</ pyx_tag_name pyx_attrs? /\/>/

pyx_tag_name: /[a-zA-Z_][a-zA-Z0-9_\-]*/

pyx_attrs: pyx_attr+

pyx_attr: pyx_attr_name /=/ pyx_attr_value

pyx_attr_name: /[a-zA-Z_][a-zA-Z0-9_\-]*/

pyx_attr_value: pyx_attr_value_string | pyx_attr_value_code

pyx_attr_value_string: /"[^"]*"/ | /'[^']*'/

pyx_attr_value_code: /{/ pyx_attr_value_code_body /}/

pyx_attr_value_code_body: /[^}]+/   # TODO: allow nested braces

pyx_body: (pyx | code | WS)+

code.0: /./

WS: /[ \t\n\r]+/

''')

res = l.parse("""
if a<b:
    print('c')
c = (<a><b>asdf</b>t</a>
""")

from pyx import App, createElement

import lark

def node_value(node):
    if isinstance(node, lark.tree.Tree):
        return "".join(node_value(c) for c in node.children)
    else:
        return node

def visit(node):
    if node.data == "pyx":
        return visit_pyx(node)
    res = ""
    for child in node.children:
        if isinstance(child, lark.tree.Tree):
            res += visit(child)
        else:
            res += child
    return res

def visit_pyx(node):
    tag_name = None
    for t in node.find_data("pyx_tag_name"):
        tag_name = node_value(t)
    return f"<PYX: {tag_name}>"

print(visit(res))

def tree_render(self, user):
    return createElement('pre', {}, self.pretty())

def text_render(self, user):
    return createElement('pre', {}, self.pretty())

lark.tree.Tree.__render__ = text_render

app = App(res)
app.run(host='0.0.0.0', port=7002)



