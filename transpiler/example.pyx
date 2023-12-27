
import pyx

class Counter:
    def __init__(self):
        self.count = 0
    
    def __render__(self, user):
        async def increment(e):
            if (await e.button) == 0:
                self.count += 1
            else:
                self.count -= 1
        return <div><button onClick={increment}>Increment</button><p>Count: <span style={{'color': 'rgb(32, 48, 196)', 'fontWeight': 'bold'}}>{self.count}</span></p></div>

app = pyx.App(Counter())
app.run()

