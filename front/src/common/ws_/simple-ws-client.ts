
// @ts-ignore
// import {WebSocket, Client} from "rpc-websockets"


import type {WsRequest, WsResponse} from "./base.ts";
import {Barrier} from "../barrier.ts";

export class WsClient{

    static shared: WsClient | undefined;

    constructor(wsUrl: string) {
        this.doInit(wsUrl)
    }

    ws: WebSocket | undefined;
    wsReadyWaiter: Barrier<any> = new Barrier<any>();

    protected doInit(wsUrl: string):void{
        // this.ws = new Client('ws://localhost:8080', )

        this.ws = new WebSocket(wsUrl, )
        this.ws.onopen = (ev) => {
            console.log('WebSocket connected');
            console.log(`ready ${ev.type}`);
            // this.waiter()
            // this.ws?.send('hello')
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

        // 处理连接成功消息    {"type":"connected"}
        if (repJson.type === 'connected'){
            console.log('Received WebSocket connected');
            await this.wsReadyWaiter?.pass(undefined)
        }

        const listeners = this.subscribeMap.get(repJson.type)
        // console.log(`listeners ${listeners}`)
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
        await this.wsReadyWaiter?.wait()
        console.log(`subscribe ${method}`)

        // todo: 有一个 bug , 给 ws 服务端发了消息后, 就有几率收不到消息了
        // this.ws?.send(method)

        if (!this.subscribeMap.has(method)) {
            this.subscribeMap.set(method, []);
        }
        if (this.subscribeMap.get(method)?.indexOf(callable) === -1) {
            this.subscribeMap.get(method)?.push(callable)
        }
        // this.subscribeMap.get(method)?.push(callable)
        return async () => await this.unsubscribe(method)
    }

    async send(methodData: WsRequest,): Promise<void> {
        await this.wsReadyWaiter?.wait()
        const datsStr = JSON.stringify(methodData)
        console.log(`send ${datsStr}`)
        this.ws?.send(datsStr)
    }

    async unsubscribe(method: string, ):Promise<void>{
        await this.wsReadyWaiter?.wait()
        console.log(`unsubscribe ${method}: ${method}`)
        this.ws?.send(`un${method}`)
        // await this.ws.unsubscribe(method)
        if (this.subscribeMap.has(method)) {
            this.subscribeMap.set(method, []);
        }
    }

}



