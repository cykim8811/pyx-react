from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

peg_grammar = Grammar(r"""
    file = ws? (rule / comment / trailer)* ws?
    comment = "#" ~"[^\n]*" newline?
    rule = (rule_name ws? ("[" type "]" )?  ws? ("(" name ")")? ws? ":" ws? "|"? ws? expression ws? newline?)
    trailer = ("@trailer" ws? "\'\'\'" ~"[^\']*" "\'\'\'" ws? newline?)
    type = ~"[a-zA-Z_][a-zA-Z_0-9]*" "*"?
    rule_name = ~"[a-zA-Z_][a-zA-Z_0-9]*"
    action = "{" ("'}'" / ~"[^}]")* "}"
    expression = sequence (ws? "|" ws? sequence)*
    sequence = (variable (wsNotNewline variable)*) (ws? action)?
    variable = ((name ("[" type "]")? ws? '=' ws?)? prefix)
    prefix = "~" / (("&&" / "&" / "!" / "~")? suffix)
    suffix = primary (suffix_chars / split)?
    suffix_chars = ("*" / "+" / "?")
    split = "." primary "+"
    primary = name
        / string
        / bracketed
    bracketed = (ws? "(" ws? expression ws? ")")
        / (ws? "[" ws? expression ws? "]")
    name = ~"[a-zA-Z_][a-zA-Z_0-9]*"
    string = ("\"" ~"[^\"]*" "\"") / ("\'" ~"[^\']*" "\'")
    ws = (~"\s+" comment?)+
    wsNotNewline = (" " / "\t" / "\v" / "\f")+
    newline = ~"[\r\n]+"
"""
)


with open("python.gram", "r") as f:
    example_peg = f.read()

parsed = peg_grammar.parse(example_peg)

class PEGVisitor(NodeVisitor):
    def visit(self, node):
        return self.visit_file(node)
    
    def visit_file(self, node):
        res = ""
        for child in node.children[1].children[60:80]:
            if child.children[0].expr_name == 'comment':
                res += self.visit_comment(child.children[0])
            elif child.children[0].expr_name == 'rule':
                res += self.visit_rule(child.children[0])
            elif child.children[0].expr_name == 'trailer':
                res += self.visit_trailer(child.children[0])
        return res
    
    def visit_comment(self, node):
        return ""
    
    def visit_trailer(self, node):
        return ""

    def visit_rule(self, node):
        rule_name = ""
        expression = ""
        for child in node.children:
            if child.expr_name == 'rule_name':
                rule_name = self.visit_rule_name(child)
            elif child.expr_name == 'expression':
                expression = self.visit_expression(child)
        return f"{rule_name} = {expression}\n"
    
    def visit_rule_name(self, node):
        return node.text

    def visit_expression(self, node):
        res = ""
        for child in node.children:
            seq = self.visit_sequence(child)
            res += (" / " + f"({seq})") if (seq != "" and res != "") else (f"({seq})" if seq != "" else "")
        return res
    
    def visit_sequence(self, node):
        if node.expr_name == 'sequence':
            res = ""
            for child in node.children:
                if len(child.children) == 0:
                    continue
                res += (self.visit_sequence(child) + " ") or ""
            return res
        elif node.expr_name == 'variable':
            return self.visit_variable(node)
        elif node.expr_name == 'action':
            return self.visit_action(node)
        else:
            res = ""
            for child in node.children:
                seq = self.visit_sequence(child)
                if seq.replace(" ", "").replace("\n", "") == "": continue
                res += (seq + " ") or ""
            return res
        
    def visit_variable(self, node):
        res = ""
        for child in node.children:
            if child.expr_name == 'prefix':
                res += self.visit_prefix(child)
        return res
    
    def visit_action(self, node):
        return "# ACTION\n"
    
    def visit_prefix(self, node):
        global indent
        res = ""
        for child in node.children:
            if child.expr_name == 'suffix':
                dres, is_split = self.visit_suffix(child)
                res += dres
            elif len(node.children) == 0:
                res += node.text
            else:
                res += self.visit_prefix(child)
        return res
    
    def visit_suffix(self, node):
        res = ""
        is_split = False
        for child in node.children:
            if child.expr_name == 'primary':
                res += self.visit_primary(child)
            elif child.expr_name == 'suffix_chars':
                res += self.visit_suffix_chars(child)
            elif child.expr_name == 'split':
                res = self.visit_split(child)
                is_split = True
                return res, is_split
            elif len(child.children) == 0:
                res += child.text
            else:
                dres, dsplit = self.visit_suffix(child)
                if dsplit:
                    if res == "":
                        res = dres.text
                    else:
                        if type(dres) != str: dres = dres.text
                        if type(res) != str: res = res.text
                        res = f"({dres} ({res} {dres})*)"
                else:
                    res += dres
                is_split = dsplit or is_split
        return res, is_split
    
    def visit_suffix_chars(self, node):
        return node.text

    def visit_split(self, node):
        return node.children[1]
    
    def visit_primary(self, node):
        return node.text
    
        

visitor = PEGVisitor()
#res = visitor.visit(parsed)
#print(res)


from pyx import App, createElement


class TextViewApp(App):
    def __init__(self, text):
        self.text = text
        super().__init__()
    
    def __render__(self, user):
        return createElement('pre', {
            'style': {
                'fontFamily': 'monospace',
                'whiteSpace': 'pre-wrap',
                'wordWrap': 'break-word',
                'fontSize': '16px',
                'color': 'rgb(64, 64, 64)',
            }
        }, self.text)







import parsimonious


def htmlformat(text):
    return text.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "\\n")

expanded_map = {}

def node_render(self, user):
    global depth
    if id(self) not in expanded_map: expanded_map[id(self)] = False
    def onClick(e):
        expanded_map[id(self)] = not expanded_map[id(self)]
        user.forceUpdate(self)
    return createElement("div", {
        'style': {
            'border': '1px solid black',
            'padding': '3px',
            'margin': '3px',
        }},
        createElement("div", {
            'style': {
                'color': 'blue' if expanded_map[id(self)] else 'rgb(96, 96, 192, 1)',
                'fontWeight': 'bold',
                'userSelect': 'none',
                'cursor': 'pointer',
            },
            'onClick': onClick
        }, f"[{self.expr_name}]"),
        *([createElement("pre", {
            'style': {
                'color': 'gray'
            }
        }, htmlformat(self.text))] if not expanded_map[id(self)] else self.children)
    )

parsimonious.nodes.Node.__render__ = node_render

parsed = parsed.children[1].children[60:80]

class TreeViewApp(App):
    def __init__(self, tree):
        self.tree = tree
        super().__init__()
    
    def __render__(self, user):
        return createElement('div', {}, *self.tree)

parsedWhole = peg_grammar.parse(example_peg)





val = ""
visitor = PEGVisitor()
for i in range(20):
    visited = visitor.visit(parsedWhole)
    val += visited

try:
    Grammar(val)
except Exception as e:
    print(e)

app = TextViewApp(val)
app.run()




visitor = PEGVisitor()
for i in range(20):
    visited = visitor.visit(parsedWhole)
    print(visited)

app = TreeViewApp(parsed)
app.run()

