
import sys
import os

import tornado.web
import tornado.ioloop
import tornado.gen

from .server import Server

class App:
    def __init__(self, component):
        self.component = component
        self.server = Server()
        self.__init_server()
    
    def __init_server(self):
        self.__init_files()
        self.__init_routes()
    
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
    
    def __init_request_handlers(self):
        # Initialize request handlers
        pass
        

    def run(self, host=None, port=None, verbose=True):
        self.server.run(host, port, verbose=verbose)

