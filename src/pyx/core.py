
from starlette.applications import Starlette

class PyX(Starlette):
    def __init__(self, component):
        self.component = component
        super().__init__()
        

