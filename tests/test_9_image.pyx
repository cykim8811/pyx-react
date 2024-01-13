

import pyx
from PIL import Image

class TestApp(pyx.App):
    def __render__(self, user):
        img = Image.open('test.png')
        return (
            <div>
                <img src={img}></img>
            </div>
        )

app = TestApp()
app.run()

