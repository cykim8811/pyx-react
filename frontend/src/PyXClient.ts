
import { ReactNode, createElement, useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { Renderable } from './Renderable';

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

    on(event: string, handler: any) {
        this.socket.on(event, handler);
    }
}

export class PyXApp{
    client: PyXClient;
    renderableSetters: {[key: string]: any};
    rootIDSetters: any[];
    renderData: {[key: string]: any};
    constructor() {
        this.client = new PyXClient();
        this.renderableSetters = {};
        this.rootIDSetters = [];
        this.renderData = {};
        this.client.on('renderable_update', (data: any) => {
            for (const id in data) {
                const renderable = this.convert(data[id]);
                this.renderData[id] = renderable;
                if (this.renderableSetters[id]) {
                    for (const setter of this.renderableSetters[id]) {
                        setter(renderable);
                    }
                }
            }
        });
        this.client.on('root_id', (data: any) => {
            for (const setter of this.rootIDSetters) {
                setter(data);
            }
        });
    }
    
    convert(node: any): any {
        if (Array.isArray(node)) {
            return node.map((n: any) => this.convert(n));
        }
        else if (typeof node === 'object' && !('__type__' in node)) {
            return Object.fromEntries(Object.entries(node).map(([key, value]) => [key, this.convert(value)]));
        }
        else if (typeof node === 'object' && node['__type__'] === 'element') {
            return createElement(node['tag'], this.convert(node['props']), ...(this.convert(node['children'])));
        }
        else if (typeof node === 'object' && node['__type__'] === 'renderable') {
            return createElement(Renderable, {id: node['renderableId'], app: this});
        }
        else {
            return node;
        }
    }

    useRenderable(id: string|null): ReactNode {
        const [renderable, setRenderable] = useState<ReactNode>((id && this.renderData[id]) ? this.renderData[id] : null);
        useEffect(() => {
            if (!id) { return; }
            if (!this.renderableSetters[id]) {
                this.renderableSetters[id] = [];
            }
            this.renderableSetters[id].push(setRenderable);
            if (this.renderData[id]) {
                setRenderable(this.renderData[id]);
            }
            return () => {
                this.renderableSetters[id] = this.renderableSetters[id].filter((s: any) => s !== setRenderable);
                if (this.renderableSetters[id].length === 0) {
                    delete this.renderableSetters[id];
                }
            }
        }, [id]);
        return renderable;
    }

    useRootID(): string|null {
        const [rootID, setRootID] = useState<string|null>(null);
        useEffect(() => {
            this.rootIDSetters.push(setRootID);
            return () => {
                this.rootIDSetters = this.rootIDSetters.filter((s: any) => s !== setRootID);
            }
        }, []);
        return rootID;
    }
}

