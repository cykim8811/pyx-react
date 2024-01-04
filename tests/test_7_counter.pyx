
import pyx

class Counter:
    def __init__(self):
        self.count = 0

    async def increment(self, event):
        k = await event.altKey
        if k:
            self.count -= 1
        else:
            self.count += 1

    def __render__(self, user):
        return (
            <div>
                <p>Count: {self.count}</p>
                <button onClick={self.increment}>Increment</button>
            </div>
        )

app = pyx.App(Counter())

app.run()

