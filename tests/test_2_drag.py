
from pyx import createElement, App

class Draggable:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.dragging = False

    async def startDrag(self, event):
        self.dragging = True
        self.x = await event.clientX - 32
        self.y = await event.clientY - 32

    def stopDrag(self, event):
        self.dragging = False

    async def drag(self, event):
        if self.dragging:
            self.x = await event.clientX - 32
            self.y = await event.clientY - 32

    def __render__(self, user):
        return createElement('div', {
            'onMouseDown': self.startDrag,
            'onMouseUp': self.stopDrag,
            'onMouseMove': self.drag,
            'style': {
                'position': 'absolute',
                'left': f'{self.x}px',
                'top': f'{self.y}px',
                'width': '100px',
                'height': '100px',
                'background': 'red'
            }
        })

class Main:
    def __init__(self):
        self.draggable = Draggable()

    def __render__(self, user):
        return createElement('div', {
                'style': {
                    'position': 'relative',
                    'width': '100vw',
                    'height': '100vh'
                }
        },
            self.draggable
        )

app = App(Main())

app.run()

