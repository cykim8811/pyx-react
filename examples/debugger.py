
from pyx import App, createElement


listRenderers = {}


typeColors = {
    'int': 'rgb(30, 64, 255)',
    'float': 'rgb(30, 144, 255)',
    'str': 'rgb(192, 96, 32)',
    'bool': 'rgb(0, 0, 0)',
}

def renderObject(target, user):
    if type(target) in [int, float, str, bool]:
        return createElement('div', {
            'style': {
                'padding': '0em',
                'display': 'inline-block',
                'color': typeColors[type(target).__name__],
            }
        }, str(target))
    elif type(target) == list:
        return renderList(target, user)
    elif type(target) == dict:
        return renderDict(target, user)
    else:
        return createElement('div', {}, str(target))

def renderList(target, user):
    return createElement('table', {
        'style': {
            'borderLeft': '1px solid rgba(0, 0, 0, 0.1)',
        }
    },
        createElement('tbody', {},
        createElement('tr', {
            'style': {
                'verticalAlign': 'top'
            }
        },
            createElement('td', {
                'style': {
                    'padding': '0em'
                },
                'colSpan': '3'
            }, '<list>')
        ),
            *[createElement('tr', {
                'style': {
                }
            },
                createElement('td', {
                    'style': {
                        'fontWeight': 'bold',
                        'verticalAlign': 'top',
                        'color': typeColors[type(i).__name__],
                    }
                }, str(i)),
                createElement('td', {
                    'style': {
                        'padding': '0em',
                        'verticalAlign': 'top',
                        'fontWeight': 'bold',
                    }
                }, ':'),
                createElement('td', {
                    'style': {
                        'paddingLeft': '0.5em',
                    }
                }, renderObject(target[i], user))
            ) for i in range(len(target))]
        )
    )

def renderDict(target, user):
    return createElement('table', {
        'style': {
            'borderLeft': '1px solid rgba(0, 0, 0, 0.1)',
        }
    },
        createElement('tbody', {},
        createElement('tr', {
            'style': {
                'verticalAlign': 'top'
            }
        },
            createElement('td', {
                'style': {
                    'padding': '0em'
                },
                'colSpan': '3'
            }, '<dict>')
        ),
            *[createElement('tr', {
                'style': {
                }
            },
                createElement('td', {
                    'style': {
                        'fontWeight': 'bold',
                        'verticalAlign': 'top',
                        'color': typeColors[type(key).__name__],
                    }
                }, str(key)),
                createElement('td', {
                    'style': {
                        'padding': '0em',
                        'verticalAlign': 'top',
                        'fontWeight': 'bold',
                    }
                }, ':'),
                createElement('td', {
                    'style': {
                        'paddingLeft': '0.5em',
                    }
                }, renderObject(target[key], user))
            ) for key in target]
        )
    )

import code
import sys

class InterpreterWrapper:
    def __init__(self):
        self.value = "data = [1, \"Hello, World!\", {'a': 3, 'b': 4}]\n"
        self.inputValue = ''
        self.interpreter = code.InteractiveConsole(globals())
    
    async def onInput(self, event):
        self.inputValue = await event.target.value
    
    async def onKeyDown(self, event):
        if await event.key == 'Enter':
            self.value += ">>> " + self.inputValue + "\n"
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = sys.stderr = self
            self.interpreter.push(self.inputValue)
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.inputValue = ''
            event.user.forceUpdate(app)
        
    def write(self, text):
        self.value += text
    
    def __render__(self, user):
        return createElement('div', {
            'style': {
                'display': 'flex',
                'flexDirection': 'column',
                'width': '20em',
            }
        },
            createElement('textarea', {
                'style': {
                    'width': '100%',
                    'height': '10em',
                    'border': '1px solid rgba(0, 0, 0, 0.1)',
                    'backgroundColor': 'rgba(0, 0, 0, 0.05)',
                    'padding': '0.5em',
                    'fontFamily': 'monospace',
                    'fontSize': '1em',
                    'resize': 'none',
                },
                'value': self.value,
                'readOnly': True,
            }),
            createElement('textarea', {
                'style': {
                    'width': '100%',
                    'height': str(self.inputValue.count('\n') * 1.15 + 1.2) + 'em',
                    'border': '1px solid rgba(0, 0, 0, 0.1)',
                    'backgroundColor': 'rgba(0, 0, 0, 0.05)',
                    'padding': '0.5em',
                    'fontFamily': 'monospace',
                    'fontSize': '1em',
                    'resize': 'none',
                },
                'value': self.inputValue,
                'onInput': self.onInput,
                'onKeyDown': self.onKeyDown,
            }),
        )
        
class Debugger(App):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.interpreter = InterpreterWrapper()
    
    def __render__(self, user):
        return createElement('div', {
            'style': {
                'width': '100%',
                'height': '100%',
                'backgroundColor': 'white',
                'padding': '1em'
            }
        },
            self.interpreter,
            renderObject(self.root, user)
        )

data = [1, "Hello, World!", {'a': 3, 'b': 4}]

app = Debugger(data)
app.run()

