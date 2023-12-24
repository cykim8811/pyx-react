
import sys
import os

import tornado.web
import tornado.ioloop
import tornado.gen

from .utils.hashID import hashObj
from .server import Server


class StateHolder:
    pass

class SetterListener:
    def __init__(self):
        self.renderableClasses = set()
        self.handlers = {}
        self.old_setattrs = {}
    
    def addHandler(self, renderableClass, handler):
        if renderableClass not in self.handlers:
            self.handlers[renderableClass] = set()
            old_setattr = renderableClass.__setattr__
            def new_setattr(target, name, value):
                old_setattr(target, name, value)
                for handler in self.handlers[renderableClass]:
                    handler(target, name, value)
            renderableClass.__setattr__ = new_setattr
            self.renderableClasses.add(renderableClass)
            self.old_setattrs[renderableClass] = old_setattr
        self.handlers[renderableClass].add(handler)


# Used to listen for changes in renderable classes
setterListener = SetterListener()


class FunctionPreloadManager:
    def __init__(self):
        self.functions = {}
    
    def identifyFunction(self, func):
        funcRepr = func.__repr__()
        return funcRepr

    def getPreloadArgs(self, func):
        funcId = self.identifyFunction(func)
        if funcId not in self.functions: return {}
        return self.functions[funcId]

    def useAttr(self, func, attrPath):
        funcId = self.identifyFunction(func)
        needUpdate = False
        if funcId not in self.functions:
            self.functions[funcId] = {}
            needUpdate = True
        target = self.functions[funcId]
        for attr in attrPath:
            if attr not in target:
                target[attr] = {}
                needUpdate = True
            target = target[attr]
        return needUpdate

class ResourceContainer:
    def __init__(self, resource):
        self.resource = resource
        self.children = {}
        self.dependencies = set()
        self.user_dependencies = set()
        self.refCount = 0
        self.updateHandler = []

class ResourceManager:
    def __init__(self, user):
        self.resources = {}
        self.user = user

        self.functionPreloadManager = FunctionPreloadManager()

        self.__new_children = {}
        self.__registered_renderable_classes = set()

    def incrementRefCount(self, renderable):
        resourceId = hashObj(renderable)
        if resourceId not in self.resources:
            self.resources[resourceId] = ResourceContainer(renderable)
        self.resources[resourceId].refCount += 1
    
    def decrementRefCount(self, renderable):
        resourceId = hashObj(renderable)
        self.resources[resourceId].refCount -= 1
        if self.resources[resourceId].refCount == 0:
            for child in self.resources[resourceId].children:
                self.decrementRefCount(child)
            del self.resources[resourceId]
    
    def registerSetattrHandler(self, renderable):
        renderableClass = renderable.__class__
        if renderableClass in self.__registered_renderable_classes: return
        self.__registered_renderable_classes.add(renderableClass)
        def handler(renderable, attrName, attrValue):
            self.handleAttributeChange(renderable, attrName, attrValue)
        setterListener.addHandler(renderableClass, handler)
    
    def registerUserSetitemHandler(self, renderable):
        # self.user.addHandler(renderable, self.handleAttributeChange)
        pass

    def update(self, renderable):
        renderableId = hashObj(renderable)
        if renderableId not in self.resources:
            self.resources[renderableId] = ResourceContainer(renderable)
        
        old_getattr = renderable.__class__.__getattribute__
        old_user_getitem = User.__getitem__
        used_attrs = set()
        used_user_items = set()
        def new_getattr(self, name):
            used_attrs.add(name)
            return old_getattr(self, name)
        def new_user_getitem(self, name):
            used_user_items.add(name)
            return old_user_getitem(self, name)
        __renderable_class = renderable.__class__
        __renderable_class.__getattribute__ = new_getattr
        User.__getitem__ = new_user_getitem
        render_result, new_children = self.convert(renderable.__render__(self.user))
        total_result = {
            renderableId: render_result
        }
        __renderable_class.__getattribute__ = old_getattr
        User.__getitem__ = old_user_getitem
        self.registerSetattrHandler(renderable)
        self.registerUserSetitemHandler(renderable)
        self.resources[renderableId].dependencies = used_attrs
        self.resources[renderableId].user_dependencies = used_user_items
        added_children = {k: v for k, v in new_children.items() if k not in self.resources[renderableId].children}
        removed_children = {k: v for k, v in self.resources[renderableId].children.items() if k not in new_children}
        self.resources[renderableId].children = new_children
        for childID in added_children:
            child = added_children[childID]
            self.incrementRefCount(child)
            if hasattr(child, '__render__'):
                total_result.update(self.update(child))
            if hasattr(child, '__call__'):
                self.resources[childID].updateHandler.append(lambda: self.user.forceUpdate(renderable))
        for childID in removed_children:
            child = removed_children[childID]
            self.decrementRefCount(child)
        return total_result

    def convert(self, element):
        self.__new_children = {}
        converted = self.__convert(element)
        return converted, self.__new_children

    def __convert(self, element):
        if type(element) is dict and '__type__' not in element:
            return {
                key: self.__convert(value)
                for key, value in element.items()
            }
        elif type(element) is dict and element['__type__'] == 'element':
            return {
                '__type__': 'element',
                'tag': element['tag'],
                'props': self.__convert(element['props']),
                'children': self.__convert(element['children'])
            }
        elif hasattr(element, '__render__'):
            self.__new_children[hashObj(element)] = element
            return {
                '__type__': 'renderable',
                'renderableId': hashObj(element)
            }
        elif hasattr(element, '__call__'):
            self.__new_children[hashObj(element)] = element
            preloadArgs = self.functionPreloadManager.getPreloadArgs(element)
            return {
                '__type__': 'callable',
                'callableId': hashObj(element),
                'preload': preloadArgs
            }
        elif type(element) is list:
            return [self.__convert(child) for child in element]
        elif type(element) is tuple:
            return tuple(self.__convert(child) for child in element)
        elif type(element) in [str, int, float, bool]:
            return str(element)
        else:
            return element
    
    def handleAttributeChange(self, renderable, attrName, attrValue):
        renderableId = hashObj(renderable)
        if renderableId not in self.resources: return
        if attrName not in self.resources[renderableId].dependencies: return
        self.user.sendUpdate(renderable)
    
    def handleUserItemChange(self, attrName, attrValue):
        for renderableId in self.resources:
            if attrName not in self.resources[renderableId].user_dependencies: continue
            self.user.sendUpdate(self.resources[renderableId].resource)
        

class User:
    def __init__(self, sid, root, server):
        self.sid = sid
        self.root = root
        self.server = server
        self.resourceManager = ResourceManager(self)
        self.server.spawn(self.emit, 'root_id', hashObj(root))
        self.sendUpdate(self.root)
        self.data = {}
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.handleAttributeChange(key, value)
        self.data[key] = value

    def handleAttributeChange(self, attrName, attrValue):
        self.resourceManager.handleUserItemChange(attrName, attrValue)
    
    def emit(self, event, data):
        return self.server.emit(event, data, room=self.sid)
    
    def sendUpdate(self, renderable):
        async def sendToClient():
            update = self.resourceManager.update(renderable)
            await self.emit('renderable_update', update)
        self.server.spawn(sendToClient)
    
    async def request(self, name, data):
        return await self.server.request(name, data, room=self.sid)
    
    def forceUpdate(self, target):
        self.sendUpdate(target)


class JSObject:
    def __init__(self, id, user, parent=None, attr=None):
        self._id = id
        self.user = user
        self._parent = parent
        self._attr = attr
        self._listeners = set()
        self._cache = {}

    def get_data_from_cache(self, path):
        if len(path) == 0:
            return self._cache
        else:
            target = self._cache
            for attr in path:
                if attr not in target: return None
                target = target[attr]._cache
            return target

    async def get_attr(self, path):
        if self._parent is None:
            cacheData = self.get_data_from_cache(path)
            if cacheData is not None:
                return cacheData
            for listener in self._listeners: listener(path)
            res = await self.user.request('jsobject_getattr', {'id': self._id, 'attr': path})
            self.load_data(res, path)
            return res
        else:
            result = await self._parent.get_attr([self._attr] + path)
            return result
        
    def load_data(self, data, path=[]):
        if len(path) > 0:
            for attr in path[::-1]:
                data = {attr: data}
        if type(data) is not dict:
            self._cache = data
            return
        for key, value in data.items():
            self._cache[key] = JSObject(self._id, self.user, self, key)
            self._cache[key].load_data(value)

    def __await__(self):
        result = self.get_attr([]).__await__()
        return result
    
    def __getitem__(self, key):
        key = str(key)
        newObject = JSObject(self._id, self.user, self, key)
        return newObject

    def __getattr__(self, name):
        name = str(name)
        newObject = JSObject(self._id, self.user, self, name)
        return newObject

    def attachAttrUseListener(self, func, functionPreloadManager):
        def listener(path):
            needUpdate = functionPreloadManager.useAttr(func, path)
            if needUpdate:
                for handler in self.user.resourceManager.resources[hashObj(func)].updateHandler:
                    handler()
                print("Force update")
        self._listeners.add(listener)

class App:
    def __init__(self, component=None):
        if component is not None:
            assert hasattr(component, '__render__'), 'Component must have __render__ method'
        self.component = component if component is not None else self
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
        self.server.add_single_file_handler("/public/pyx.js", module_dir + "/assets/pyx.js")
        self.server.add_single_file_handler("/", running_dir + "/public/index.html")
        self.server.add_static_file_handler(r"/public/(.*)", running_dir + "/public")
    
    def __init_user_handlers(self):
        # Initialize user handlers
        @self.server.event
        def connect(sid, environ):
            self.users[sid] = User(sid, self.component, self.server)
            self.onConnect(self.users[sid])
            self.users = self.users
        
        @self.server.event
        def disconnect(sid):
            self.onDisconnect(self.users[sid])
            del self.users[sid]
            self.users = self.users

    def __init_request_handlers(self):
        # Initialize Callable Handlers
        @self.server.handler
        async def callable_call(sid, data):
            user = self.users[sid]
            callableId = data['id']
            argId = data['argId']
            argCount = data['argCount']
            callableObj = user.resourceManager.resources[callableId].resource
            preload = data['preload'] if 'preload' in data else {}
            argObj = JSObject(argId, user)
            argObj.load_data(preload)
            argObj.attachAttrUseListener(callableObj, user.resourceManager.functionPreloadManager)
            # for handler in user.resourceManager.resources[callableId].updateHandler:
            #     handler()

            result = await callableObj(*[argObj[i] for i in range(argCount)])

            return result


    def run(self, host=None, port=None, verbose=True):
        self.server.run(host, port, verbose=verbose)
    

    def __render__(self, user):
        return createElement('div', {}, "Default App")
    
    def onConnect(self, user):
        pass

    def onDisconnect(self, user):
        pass

