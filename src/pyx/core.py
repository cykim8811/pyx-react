
from starlette.applications import Starlette
from starlette.responses import FileResponse
from starlette.routing import Route


import os

static_dir = os.path.join(os.path.dirname(__file__), 'static/frontend')

class PyX(Starlette):
    def __init__(self, component):
        self.component = component
        super().__init__()

        self.add_route('/', self.index)
        self.add_route('/{file_path:path}', self.static)

    async def index(self, request):
        return FileResponse(os.path.join(static_dir, 'index.html'))

    async def static(self, request):
        return FileResponse(os.path.join(static_dir, request.path_params['file_path']))
        

