
from pyx import createElement, App

class Counter:
    def __init__(self):
        self.count = 0

    def increment(self, event):
        self.count += 1

    def __render__(self, user):
        return createElement('div', {},
            createElement('button', {'onClick': self.increment}, 'Increment'),
            createElement('p', {}, f'Count: {self.count}')
        )

app = App(Counter())

app.run()

