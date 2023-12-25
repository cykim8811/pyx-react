
from pyx import App, createElement


class TestApp(App):
    def __init__(self):
        super().__init__()
        self.doPreventDefault = False

    def __render__(self, user):
        def onContextMenu(e):
            print("Clicked!")
        onContextMenu.preventDefault = self.doPreventDefault

        async def onSelectChange(e):
            check = await e.target.checked
            self.doPreventDefault = check

        return createElement('div', {},
            createElement("input", {
                "type": "checkbox",
                "onChange": onSelectChange
            }),
            createElement(
                "div",
                {
                    "onContextMenu": onContextMenu,
                    "style": {
                        "backgroundColor": "lightblue",
                        "padding": "10px",
                    }
                },
                "Click me!"
            )
        )

app = TestApp()
app.run()

