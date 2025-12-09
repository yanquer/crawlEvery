
// @ts-ignore
// import {WebSocket, Client} from "rpc-websockets"


import type {WsResponse} from "./base.ts";

export class WsClient{

    static shared: WsClient | undefined;

    constructor(wsUrl: string) {
        this.doInit(wsUrl)
    }

    ws: WebSocket | undefined;
    wsReady: Promise<void> | undefined;
    waiter: any

    protected doInit(wsUrl: string):void{
        // this.ws = new Client('ws://localhost:8080', )

        this.wsReady = new Promise<void>(resolve => {
            this.waiter = resolve;
        })

        this.ws = new WebSocket(wsUrl, )
        this.ws.onopen = (ev) => {
            console.log('WebSocket connected');
            console.log(`ready ${ev.type}`);
            this.waiter()
        }
        this.ws.onmessage = async (ev) => {
            console.log('WebSocket onmessage');
            // console.log(`onmessage ${ev.type} ${ev.data}`);
            await this.handleEvent(ev)
        }
    }

    protected async handleEvent(
        event: MessageEvent
    ){
        console.log(`handleEvent Received ${event.type} data ${event.data}`);

        let repJson: WsResponse = {} as WsResponse;
        try {
            repJson = JSON.parse(event.data);
        } catch (e) {
            console.error(`Received JSON data to error ${e} with data ${event.data}`);
        }

        const listeners = this.subscribeMap.get(repJson.type)
        if (listeners && listeners.length > 0) {
            for (const listener of listeners) {
                listener(repJson).then().catch(e => {
                    console.error(`Unhandled event ${event}, error: ${e} with ${event.type}`, )
                })
            }
        }
    }

    protected subscribeMap = new Map<string, Array<(data: WsResponse) => Promise<any>>>();
    async subscribe(method: string, callable: (data: WsResponse) => Promise<any>):Promise<() => Promise<void>>{
        await this.wsReady
        console.log(`subscribe ${method}: ${callable}`)
        this.ws?.send(method)

        if (!this.subscribeMap.has(method)) {
            this.subscribeMap.set(method, []);
        }
        this.subscribeMap.get(method)?.push(callable)
        return async () => await this.unsubscribe(method)
    }

    async unsubscribe(method: string, ):Promise<void>{
        await this.wsReady
        console.log(`unsubscribe ${method}: ${method}`)
        this.ws?.send(`un${method}`)
        // await this.ws.unsubscribe(method)
        if (this.subscribeMap.has(method)) {
            this.subscribeMap.set(method, []);
        }
    }

}



