
import sys
import os
from .server import PyXServer

import tornado.web
import tornado.ioloop
import tornado.gen

class PyXApp:
    def __init__(self, component):
        self.component = component
        self.server = PyXServer()
        self.__init_server()
    
    def __init_server(self):
        # Initialize server routes
        running_dir = sys.path[0]
        module_dir = os.path.dirname(os.path.realpath(__file__))

        # Copy assets to running directory
        if not os.path.isdir(running_dir + "/public"):
            os.mkdir(running_dir + "/public")
        if not os.path.isfile(running_dir + "/public/index.html"):
            os.system(f"cp {module_dir}/assets/index.html {running_dir}/public/index.html")
        if not os.path.isfile(running_dir + "/public/favicon.ico"):
            os.system(f"cp {module_dir}/assets/favicon.ico {running_dir}/public/favicon.ico")

        # Add routes
        self.server.add_single_file_handler("/favicon.ico", running_dir + "/public/favicon.ico")
        self.server.add_single_file_handler("/", running_dir + "/public/index.html")
        self.server.add_static_file_handler(r"/public/(.*)", running_dir + "/public")

    def run(self, host=None, port=None, verbose=True):
        self.server.run(host, port, verbose=verbose)

