
import pyx
import importlib.util

spec = importlib.util.spec_from_file_location(name="render", location="./render.x.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)
renderObject = render.renderObject

class Floater:
    def __init__(self, screen, obj):
        self.x = 0
        self.y = 0
        self.screen = screen
        self._draggingUser = None
        self._dragOffsetX = 0
        self._dragOffsetY = 0
        self.obj = obj
    
    def setPosition(self, x, y):
        self.x = x
        self.y = y
        return self
    
    def onScreenMouseMove(self, ex, ey, user):
        if self._draggingUser == user:
            self.x = ex - self._dragOffsetX
            self.y = ey - self._dragOffsetY
            user['mousePos'] = (ex, ey)
        
    def onScreenMouseUp(self):
        self._draggingUser = None
        
    async def onMouseDown(self, event):
        self._draggingUser = event.user
        self._dragOffsetX = event.user['mousePos'][0] - self.x
        self._dragOffsetY = event.user['mousePos'][1] - self.y
    
    async def onMouseUp(self, event):
        self._draggingUser = None
    
    def __render__(self, user):
        return (
            <div style={{"position": "absolute", "left": f"{self.x}px", "top": f"{self.y}px", "width": "100px", "height": "100px",
            "backgroundColor": "green", "userSelect": "none"},
                "onMouseDown": self.onMouseDown,
                "key": id(self.obj)
                }>
                {renderObject(self.obj, user)}
            </div>
        )

class Screen:
    def __init__(self, app):
        self.floaterList = []
        self.addFloater("Hello World")
        self.addFloater(3)
        self.app = app
    
    def addFloater(self, obj):
        newFloater = Floater(self, obj)
        self.floaterList.append(newFloater)
        return newFloater
    
    def removeFloater(self, floater):
        self.floaterList.remove(floater)
        return floater

    async def onMouseMove(self, event):
        ex, ey = (await event.clientX), (await event.clientY)
        for floater in self.floaterList:
            floater.onScreenMouseMove(ex, ey, event.user)
        event.user['mousePos'] = (ex, ey)

    def onMouseUp(self, event):
        for floater in self.floaterList:
            floater.onScreenMouseUp()
    
    def onMouseLeave(self, event):
        event.user['mousePos'] = None
    
    def drawCursor(self, target, user):
        if 'mousePos' not in target.data or target['mousePos'] is None: return None
        ux, uy = target['mousePos']
        return (
            <span style={{"position": "absolute", "left": f"{ux - 2.5}px", "top": f"{uy - 2.5}px"}}>
                <div style={{"width": "5px", "height": "5px", "borderRadius": "2.5px", "pointerEvents": "none",
                "backgroundColor": "black", "userSelect": "none"},
                "key": target.sid}>
                </div>
                <span style={{"position": "absolute", "left": "4px", "top": "-24px", "pointerEvents": "none"}}>
                    {target.data['name'] if 'name' in target.data else "..."}
                </span>
            </span>
        )
    
    def __render__(self, user):
        return (
            <span>
                {self.floaterList}
                {[self.drawCursor(target, user) for target in self.app.users.values() if target != user]}
            </span>
        )

class App(pyx.App):
    def __init__(self):
        super().__init__()
        self.screen = Screen(self)
    
    async def onMouseMove(self, event):
        await self.screen.onMouseMove(event)

    def onMouseUp(self, event):
        self.screen.onMouseUp(event)

    def onMouseLeave(self, event):
        self.screen.onMouseLeave(event)
    
    def onConnect(self, user):
        user['name'] = "Anonymous"
        
    def __render__(self, user):
        return <div style={{"width": "100%", "height": "100%", "backgroundColor": "white"},
                "onMouseMove": self.onMouseMove,
                "onMouseUp": self.onMouseUp,
                "onMouseLeave": self.onMouseLeave,
        }>
            {self.screen}
        </div>


app = App()
app.run()

