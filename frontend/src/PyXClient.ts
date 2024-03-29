
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
            if (data.id === undefined) { console.log('Cannot find id in response'); return; }
            if (data.data === undefined) { console.log('Cannot find data in response'); return; }
            if (this.requests[data.id] === undefined) { console.log('Cannot find request with id ' + data.id); return; }
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
    jsObjects: {[key: string]: any};
    constructor() {
        this.client = new PyXClient();
        this.renderableSetters = {};
        this.rootIDSetters = [];
        this.renderData = {};
        this.jsObjects = {};
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
        this.client.add_handler('jsobject_getattr', (data: any) => {
            if (data.id === undefined) { throw new Error('Cannot find id in jsobject_getattr'); }
            if (data.attr === undefined) { throw new Error('Cannot find attr in jsobject_getattr'); }
            if (this.jsObjects[data.id] === undefined) { throw new Error('Cannot find object with id ' + data.id); }
            let obj = this.jsObjects[data.id];
            for (const attr of data.attr) {
                obj = obj[attr];
            }
            if (typeof obj === 'object') {
                throw new Error('Using objects in jsobject_getattr is not supported yet');
            }
            return obj;
        });
    }
    
    private matchArgs(args: any, format: any): any {
        const result: any = {};
        for (let i in args) {
            if (format[i] === undefined) continue;
            if (typeof args[i] === 'object') {
                result[i] = this.matchArgs(args[i], format[i]);
            }
            else {
                result[i] = args[i];
            }
        }
        return result;
    }
    
    convert(node: any): any {
        if (node === null) {
            return null;
        }
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
        else if (typeof node === 'object' && node['__type__'] === 'callable') {
            const prevendDefault = node['preventDefault'] || false;
            const stopPropagation = node['stopPropagation'] || false;
            console.log(`Callable ${node['callableId']} has preventDefault=${prevendDefault} and stopPropagation=${stopPropagation}`)
            return (...args: any[]) => {
                if (prevendDefault) { args[0].preventDefault(); }
                if (stopPropagation) { args[0].stopPropagation(); }
                (async (...args: any[]) => {
                    const jsObjectID = Math.random().toString(36).substring(7);
                    this.jsObjects[jsObjectID] = args;
                    const format = node['preload'] || {};
                    const preloaded = this.matchArgs(args, format);
                    await this.client.request('callable_call', {id: node['callableId'], argId: jsObjectID, argCount: args.length, preload: preloaded});
                    delete this.jsObjects[jsObjectID];
                })(...args);
            }
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

