
from pyx import App, createElement

class TestComponent:
    def __init__(self):
        self.count = 0
    
    def onClick(self, user):
        user["count"] += 1
        print("Clicked", user["count"])

    def __render__(self, user):
        return createElement(
            "div",
            {
                "onClick": lambda e: self.onClick(user)
            },
            f"Count: {user['count']}"
        )


class TestApp(App):
    def __init__(self):
        super().__init__()
        self.component = TestComponent()
    
    def onConnect(self, user):
        user["count"] = 0


    def __render__(self, user):
        return self.component



app = TestApp()
app.run()

