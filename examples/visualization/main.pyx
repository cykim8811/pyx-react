
import pyx

class Floater:
    def __init__(self, screen):
        self.x = 0
        self.y = 0
        self.screen = screen
        self._isDragging = False
        self._dragOffsetX = 0
        self._dragOffsetY = 0
        self._mousePos = (0, 0)
    
    def setPosition(self, x, y):
        self.x = x
        self.y = y
        return self
    
    def onScreenMouseMove(self, ex, ey):
        if self._isDragging:
            self.x = ex - self._dragOffsetX
            self.y = ey - self._dragOffsetY
        self._mousePos = (ex, ey)
        
    def onScreenMouseUp(self):
        self._isDragging = False
    
    def __render__(self, user):
        async def onMouseDown(event):
            self._isDragging = True
            self._dragOffsetX = self._mousePos[0] - self.x
            self._dragOffsetY = self._mousePos[1] - self.y
        onMouseDown.stopPropogation = True
        return (
            <div style={{"position": "absolute", "left": f"{self.x}px", "top": f"{self.y}px", "width": "100px", "height": "100px",
            "backgroundColor": "green", "userSelect": "none"},
                "onMouseDown": onMouseDown
                }>
                Hello World
            </div>
        )

class Screen:
    def __init__(self, app):
        self.floaterList = []
        self.addFloater(Floater(self).setPosition(100, 100))
        self.addFloater(Floater(self).setPosition(200, 200))
        self.app = app
    
    def addFloater(self, floater):
        self.floaterList.append(floater)
        return floater
    
    def removeFloater(self, floater):
        self.floaterList.remove(floater)
        return floater
    
    async def onMouseMove(self, event):
        ex, ey = (await event.clientX), (await event.clientY)
        for floater in self.floaterList:
            floater.onScreenMouseMove(ex, ey)

    async def onMouseUp(self, event):
        for floater in self.floaterList:
            floater.onScreenMouseUp()
    
    def __render__(self, user):
        return (
            <div style={{"width": "100%", "height": "100%", "backgroundColor": "white"},
                "onMouseMove": self.onMouseMove,
                "onMouseUp": self.onMouseUp
            }>
                {self.floaterList}
            </div>
        )

class App(pyx.App):
    def __init__(self):
        super().__init__()
        self.screen = Screen(self)

    def __render__(self, user):
        return self.screen


app = App()
app.run()

