
import sys
import os

import tornado.web
import tornado.ioloop
import tornado.gen

from .hashID import hashObj
from .server import Server


class SetterListener:
    def __init__(self):
        self.renderableClasses = set()
        self.handlers = {}
        self.old_setattrs = {}
    
    def addHandler(self, renderableClass, handler):
        if renderableClass not in self.handlers:
            self.handlers[renderableClass] = set()
            old_setattr = renderableClass.__setattr__
            def new_setattr(self, name, value):
                old_setattr(self, name, value)
                for handler in self.handlers[renderableClass]:
                    handler(self, name, value)
            renderableClass.__setattr__ = new_setattr
            self.renderableClasses.add(renderableClass)
            self.old_setattrs[renderableClass] = old_setattr
        self.handlers[renderableClass].add(handler)


# Used to listen for changes in renderable classes
setterListener = SetterListener()


class RenderableContainer:
    def __init__(self, renderable):
        self.renderable = renderable
        self.children = set()
        self.dependencies = set()
        self.refCount = 0

class RenderableManager:
    def __init__(self, user):
        self.renderables = {}
        self.user = user

        self.__new_children = {}
        self.__registered_renderable_classes = set()

    def incrementRefCount(self, renderable):
        renderableId = hashObj(renderable)
        if renderableId not in self.renderables:
            self.renderables[renderableId] = RenderableContainer(renderable)
        self.renderables[renderableId].refCount += 1
    
    def decrementRefCount(self, renderable):
        renderableId = hashObj(renderable)
        self.renderables[renderableId].refCount -= 1
        if self.renderables[renderableId].refCount == 0:
            for child in self.renderables[renderableId].children:
                self.decrementRefCount(child)
            del self.renderables[renderableId]
    
    def registerSetattrHandler(self, renderable):
        renderableClass = renderable.__class__
        if renderableClass in self.__registered_renderable_classes: return
        self.__registered_renderable_classes.add(renderableClass)
        def handler(renderable, attrName, attrValue):
            self.handleAttributeChange(renderable, attrName, attrValue)
        setterListener.addHandler(renderableClass, handler)

    def update(self, renderable):
        renderableId = hashObj(renderable)
        if renderableId not in self.renderables:
            self.renderables[renderableId] = RenderableContainer(renderable)
        # TODO: Add user data dependency
        old_getattr = renderable.__class__.__getattribute__
        used_attrs = set()
        def new_getattr(self, name):
            used_attrs.add(name)
            return old_getattr(self, name)
        __renderable_class = renderable.__class__
        __renderable_class.__getattribute__ = new_getattr
        
        render_result, new_children = self.convert(renderable.__render__(self.user))
        total_result = {
            renderableId: render_result
        }
        __renderable_class.__getattribute__ = old_getattr
        self.registerSetattrHandler(renderable)
        self.renderables[renderableId].dependencies = used_attrs
        added_children = new_children - self.renderables[renderableId].children
        removed_children = self.renderables[renderableId].children - new_children
        self.renderables[renderableId].children = new_children
        for child in added_children:
            self.incrementRefCount(child)
            total_result[hashObj(child)] = self.update(child)
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
    
    def handleAttributeChange(self, renderable, attrName, attrValue):
        renderableId = hashObj(renderable)
        if renderableId not in self.renderables: return
        if attrName not in self.renderables[renderableId].dependencies: return
        # TODO: Send update to client
        print("EMIT", self.update(renderable))
        

class User:
    def __init__(self, sid):
        self.sid = sid
        self.renderableManager = RenderableManager(self)

    def handleAttributeChange(self, renderable, attrName):
        self.renderableManager.handleAttributeChange(renderable, attrName)

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

