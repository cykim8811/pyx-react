
import pyx
from pyx import createElement

class App(pyx.App):
    def __init__(self):
        super().__init__()
        self.cursors = {}

    def onConnect(self, user):
        # Using self.cursors[user.sid] = Cursor() won't cause re-render
        self.cursors = {**self.cursors, user.sid: Cursor()}
    
    def onDisconnect(self, user):
        # Using del self.cursors[user.sid] won't cause re-render
        self.cursors = {k: v for k, v in self.cursors.items() if k != user.sid}
        
    async def onMouseMove(self, e):
        cx, cy = await e.clientX, await e.clientY
        self.cursors[e.user.sid].onMove(cx, cy)

    async def onLeave(self, e):
        self.cursors[e.user.sid].display = False

    async def onEnter(self, e):
        self.cursors[e.user.sid].display = True

    async def onChange(self, e):
        self.cursors[e.user.sid].name = await e.target.value

    def __render__(self, user):
        return createElement('div', {
            'onMouseMove': self.onMouseMove,
            'onMouseLeave': self.onLeave,
            'onMouseEnter': self.onEnter,
            'style': {
                'width': '100vw',
                'height': '50vh',
                'background': '#eee',
                'position': 'relative'
            }
        },
            createElement('input', {
                'onChange': self.onChange,
                'style': {
                    'position': 'fixed',
                    'left': '10px',
                    'top': '10px',
                    'width': '100px',
                    'height': '30px',
                    'border': '1px solid #000'
                }
            }),
            *[cursor for userId, cursor in self.cursors.items() if userId != user.sid]
        )


class Cursor:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.name = ''
        self.display = True
    
    def __render__(self, user):
        if not self.display: return createElement('div', {})
        return createElement('div', {
            'style': {
                'position': 'fixed',
                'left': str(self.x) + 'px',
                'top': str(self.y) + 'px',
                'width': '10px',
                'height': '10px',
                'background': '#000',
                'borderRadius': '50%',
                'pointerEvents': 'none'
            }
        },
            createElement('div', {
                'style': {
                    'position': 'absolute',
                    'left': '10px',
                    'top': '-10px',
                    'fontSize': '16px',
                    'pointerEvents': 'none'
                }
            }, self.name)
        )
    
    def onMove(self, x, y):
        self.x = x
        self.y = y

app = App()
app.run()

