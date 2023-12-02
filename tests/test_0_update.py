
import pyx

class B:
    def __init__(self):
        self.x = 1

    def __render__(self, user):
        return self.x
    
globalB = B()

class A:
    def __init__(self):
        self.b = globalB

    def __render__(self, user):
        return self.b

class Root:
    def __init__(self):
        self.a1 = A()
        self.a2 = A()

    def __render__(self, user):
        return pyx.createElement('div', {}, 
            self.a1,
            self.a2,
            'Hello world!'
        )

root = Root()
app = pyx.App(root)

async def test():
    await app.server.sleep(10)
    print(1)
    globalB.x = 2
    await app.server.sleep(5)
    print(2)
    root.a1.b = "HIHI"
    await app.server.sleep(5)
    print(3)
    root.a2 = "Hello"
    await app.server.sleep(5)
    print(4)
    root.a1 = "Hi"



app.server.spawn(test)

app.run('0.0.0.0')

