
import { io, Socket } from 'socket.io-client';

// Handle requests to server
class PyXRequestManager{
    socket: Socket;
    requests: {[key: string]: any} = {};
    constructor(socket: Socket) {
        this.socket = socket;
        this.requests = {};
        this.socket.on('response', (data: any) => {
            if (!data.id) { console.log('Cannot find id in response'); return; }
            if (!data.data) { console.log('Cannot find data in response'); return; }
            if (!this.requests[data.id]) { console.log('Cannot find request with id ' + data.id); return; }
            this.requests[data.id](data.data);
            delete this.requests[data.id];
        });
    }

    async request(name: string, data: any): Promise<any> {
        return new Promise((resolve) => {
            const request_id = Math.random().toString(36).substring(7);
            this.requests[request_id] = resolve;
            this.socket.emit('request', {id: request_id, name, data});
        });
    }
}

// Handle requests from server
class PyXResponseManager{
    handlers: {[key: string]: any};
    constructor(socket: Socket) {
        this.handlers = {};
        socket.on('request', async (data: any) => {
            if (!data.id) { console.log('Cannot find id in request'); return; }
            if (!data.name) { console.log('Cannot find name in request'); return; }
            if (!data.data) { console.log('Cannot find data in request'); return; }
            if (!this.handlers[data.name]) { console.log('Cannot find handler for request ' + data.name); return; }
            try {
                const response = await this.handlers[data.name](data.data);
                socket.emit('response', {id: data.id, data: response});
            } catch (e) {
                console.log('Error in request ' + data.name + ': ' + e);
            }
        });
    }
    add_handler(name: string, handler: any) {
        if (this.handlers[name]) { console.error('Handler for request ' + name + ' already exists'); return; }
        this.handlers[name] = handler;
    }
}

export class PyXClient{
    socket: Socket;
    requestManager: PyXRequestManager;
    responseManager: PyXResponseManager;
    constructor() {
        this.socket = io();
        this.requestManager = new PyXRequestManager(this.socket);
        this.responseManager = new PyXResponseManager(this.socket);
    }

    async request(name: string, data: any): Promise<any> {
        return this.requestManager.request(name, data);
    }

    add_handler(name: string, handler: any) {
        this.responseManager.add_handler(name, handler);
    }
}

