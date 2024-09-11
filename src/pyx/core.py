
from starlette.applications import Starlette
from starlette.responses import FileResponse
from starlette.routing import Route

import socketio

import os

static_dir = os.path.join(os.path.dirname(__file__), 'static/frontend')


class PyXResource:
    pass


class PyXComponent(PyXResource):
    pass


class PyXFunction(PyXResource):
    pass

class PyXClient:
    sio: socketio.AsyncServer
    sid: str

    def __init__(self, sio, sid):
        self.sio = sio
        self.sid = sid


class PyX(Starlette):
    component: object
    sio: socketio.AsyncServer
    clients: dict

    def __init__(self, component):
        self.component = component
        self.sio = socketio.AsyncServer(async_mode='asgi')
        self.clients = {}
        super().__init__()

        self.mount('/socket.io', socketio.ASGIApp(self.sio))

        self.sio.on('connect', self.connect)
        self.sio.on('disconnect', self.disconnect)
        self.sio.on('message', self.message)

        self.add_route('/', self.index)
        self.add_route('/{file_path:path}', self.static)


    async def index(self, request):
        return FileResponse(os.path.join(static_dir, 'index.html'))

    async def static(self, request):
        return FileResponse(os.path.join(static_dir, request.path_params['file_path']))

    async def connect(self, sid, environ):
        self.clients[sid] = PyXClient(self.sio, sid)

    async def disconnect(self, sid):
        del self.clients[sid]

    async def message(self, sid, data):
        print('message ', data)

