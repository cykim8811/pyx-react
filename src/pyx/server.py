
import tornado.web
import tornado.ioloop
import socketio

import asyncio
import os

import random

# Handle requests to client
class PyXRequestManager:
    def __init__(self, sio):
        self.requests = {}
        self.sio = sio
        @sio.event
        async def response(sid, data):
            if 'id' not in data: raise ValueError('Cannot find request id')
            if 'data' not in data: raise ValueError('Cannot find request data')
            if data['id'] in self.requests:
                self.requests[data['id']].set_result(data['data'])
                del self.requests[data['id']]
            else:
                raise ValueError(f'Cannot find request id: {data["id"]}')
    
    async def request(self, name, data):
        request_id = hex(random.randint(0, 0xffffffffffff))[2:]
        self.requests[request_id] = asyncio.Future()
        await self.sio.emit('request', {'id': request_id, 'name': name, 'data': data})
        return await self.requests[request_id]


# Handle requests from client
class PyXResponseManager:
    def __init__(self, sio):
        self.handlers = {}
        @sio.event
        async def request(sid, data):
            if 'id' not in data: raise ValueError('Cannot find request id')
            if 'name' not in data: raise ValueError('Cannot find request name')
            if 'data' not in data: raise ValueError('Cannot  find request data')
            if data['name'] not in self.handlers: raise ValueError(f'Cannot find request handler: {data["name"]}')
            try:
                response_data = await self.handlers[data['name']](sid, data['data'])
                await sio.emit('response', {'id': data['id'], 'data': response_data})
            except Exception as e:
                await sio.emit('response', {'id': data['id'], 'data': {'error': str(e)}})

    def add_handler(self, name, handler):
        self.handlers[name] = handler
    

class PyXServer:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode='tornado')
        
        self.routes = []
        self.routes.append((r"/socket.io/", socketio.get_tornado_handler(self.sio)))

        self.request_manager = PyXRequestManager(self.sio)
        self.response_manager = PyXResponseManager(self.sio)

    def __check_event_name(self, name):
        if name in ['response', 'request']:
            raise ValueError(f'Cannot use reserved event name: {name}')

    def add_route(self, route, handler):
        self.routes.append((route, handler))

    def add_static(self, route, path):
        self.routes.append((route, tornado.web.StaticFileHandler, {"path": path}))

    def event(self, func):
        self.__check_event_name(func.__name__)
        self.sio.event(func)
    
    def handler(self, func):
        self.__check_event_name(func.__name__)
        self.response_manager.add_handler(func.__name__, func)
    
    async def request(self, name, data):
        return await self.request_manager.request(name, data)
    
    def emit(self, name, data):
        return self.sio.emit(name, data)
    
    def spawn(self, func, *args, **kwargs):
        tornado.ioloop.IOLoop.current().spawn_callback(func, *args, **kwargs)
    
    def sleep(self, time):
        return tornado.gen.sleep(time)

    def run(self, host=None, port=None, verbose=True):
        host = host if host else os.environ.get('HOST', 'localhost')
        port = port if port else os.environ.get('PORT', 8080)
        app = tornado.web.Application(self.routes)
        app.listen(port, address=host)
        # TODO: Use logger instead of print
        if verbose: print('\033[92m' + f'PyX Server is running on http://{host}:{port}' + '\033[0m')
        tornado.ioloop.IOLoop.current().start()

