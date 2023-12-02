
import sys
import os

import tornado.web
import tornado.ioloop
import tornado.gen

from .hashID import hashObj
from .server import Server


class RenderableContainer:
    def __init__(self, renderable):
        self.renderable = renderable
        self.result = None
        self.children = set()
        self.dependencies = set()
        self.refCount = 0

class RenderableManager:
    def __init__(self, user):
        self.renderables = {}
        self.user = user

        self.__new_children = {}
    
    def decrementRefCount(self, renderable):
        renderableId = hashObj(renderable)
        self.renderables[renderableId].refCount -= 1
        if self.renderables[renderableId].refCount == 0:
            for child in self.renderables[renderableId].children:
                self.decrementRefCount(child)
            del self.renderables[renderableId]

    def update(self, renderable):
        renderableId = hashObj(renderable)
        if renderableId not in self.renderables:
            self.renderables[renderableId] = RenderableContainer(renderable)
        # TODO: Register getattr to check props
        render_result, new_children = self.convert(renderable.__render__(self.user))
        total_result = {
            renderableId: render_result
        }
        # TODO: Unregister getattr
        # TODO: Set dependencies
        self.renderables[renderableId].result = render_result
        added_children = new_children - self.renderables[renderableId].children
        removed_children = self.renderables[renderableId].children - new_children
        self.renderables[renderableId].children = new_children
        for child in added_children:
            childId = hashObj(child)
            if childId not in self.renderables:
                self.renderables[childId] = RenderableContainer(child)
            self.renderables[childId].refCount += 1
            total_result[childId] = self.update(child)
        for child in removed_children:
            self.decrementRefCount(child)
        return total_result


    def convert(self, element):
        self.__new_children = set()
        converted = self.__convert(element)
        return converted, self.__new_children

    def __convert(self, element):
        if type(element) is dict and '__type__' not in element:
            return {
                key: convert(value)
                for key, value in element.items()
            }
        elif type(element) is dict and element['__type__'] == 'element':
            return {
                '__type__': 'element',
                'tag': element['tag'],
                'props': convert(element['props']),
                'children': convert(element['children'])
            }
        elif hasattr(element, '__render__'):
            self.__new_children.add(element)
            return {
                '__type__': 'renderable',
                'renderableId': hashObj(element)
            }
        elif type(element) is list:
            return [convert(child) for child in element]
        elif type(element) is tuple:
            return tuple(convert(child) for child in element)
        elif type(element) in [str, int, float, bool]:
            return str(element)
        else:
            return element
        

class User:
    def __init__(self, sid):
        self.sid = sid

class App:
    def __init__(self, component):
        self.component = component
        self.server = Server()
        self.__init_server()

        self.users = {}
    
    def __init_server(self):
        self.__init_files()
        self.__init_routes()
        self.__init_user_handlers()
        self.__init_request_handlers()
    
    def __init_files(self):
        running_dir = sys.path[0]
        module_dir = os.path.dirname(os.path.realpath(__file__))

        # Copy assets to running directory if not exists
        if not os.path.isdir(running_dir + "/public"):
            os.mkdir(running_dir + "/public")
        if not os.path.isfile(running_dir + "/public/index.html"):
            os.system(f"cp {module_dir}/assets/index.html {running_dir}/public/index.html")
        if not os.path.isfile(running_dir + "/public/favicon.ico"):
            os.system(f"cp {module_dir}/assets/favicon.ico {running_dir}/public/favicon.ico")

    def __init_routes(self):
        running_dir = sys.path[0]
        module_dir = os.path.dirname(os.path.realpath(__file__))

        # Add routes
        self.server.add_single_file_handler("/favicon.ico", running_dir + "/public/favicon.ico")
        self.server.add_single_file_handler("/", running_dir + "/public/index.html")
        self.server.add_static_file_handler(r"/public/(.*)", running_dir + "/public")
    
    def __init_user_handlers(self):
        # Initialize user handlers
        @self.server.event
        def connect(sid, environ):
            self.users[sid] = User(sid)
            self.onConnect(self.users[sid])
        
        @self.server.event
        def disconnect(sid):
            self.onDisconnect(self.users[sid])
            del self.users[sid]

    def __init_request_handlers(self):
        # Initialize request handlers
        pass
            


    def run(self, host=None, port=None, verbose=True):
        self.server.run(host, port, verbose=verbose)


    
    def onConnect(self, user):
        pass

    def onDisconnect(self, user):
        pass

