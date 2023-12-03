
from pyx import createElement, App

class Counter:
    def __init__(self):
        self.count = 0

    async def increment(self, event):
        for i in range(100):
            await event.button
        if await event.altKey:
            self.count -= 1
        else:
            self.count += 1

    def __render__(self, user):
        return createElement('div', {},
            createElement('p', {}, f'Count: {self.count}'),
            createElement('button', {'onClick': self.increment}, 'Increment')
        )

app = App(Counter())

app.run()

