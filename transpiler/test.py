

from lark import Lark

l = Lark(r'''
?start: (pyx | _code | _WS)*

pyx.1:
    | pyx_tag_start pyx_tag_end
    | pyx_tag_start pyx_body? pyx_tag_end
    | pyx_tag_self_closing

pyx_tag_start: "<" pyx_tag_name pyx_attrs? ">"

pyx_tag_end: "</" pyx_tag_name ">"

pyx_tag_self_closing: "<" pyx_tag_name pyx_attrs? "/>"

pyx_tag_name: /[a-zA-Z_][a-zA-Z0-9_\-]*/

pyx_attrs: pyx_attr+

pyx_attr: pyx_attr_name "=" pyx_attr_value

pyx_attr_name: /[a-zA-Z_][a-zA-Z0-9_\-]*/

pyx_attr_value: pyx_attr_value_string | pyx_attr_value_code

pyx_attr_value_string: /"[^"]*"/ | /'[^']*'/

pyx_attr_value_code: "{" pyx_attr_value_code_body "}"

pyx_attr_value_code_body: /[^}]+/   # TODO: allow nested braces

pyx_body: (pyx | _code | _WS)+

_code.0: /./

_WS: /[ \t\n\r]+/

''')

res = l.parse("""
if a<b:
    print('c')
c = <pa><he>asdf</he></pa>
""")

from pyx import App, createElement

import lark

def tree_render(self, user):
    return createElement('pre', {}, self.pretty())

def token_render(self, user):
    return createElement('span', {}, str(self))

lark.tree.Tree.__render__ = tree_render

app = App(res)
app.run(host='0.0.0.0', port=7002)

