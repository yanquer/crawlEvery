

export interface WsResponse {
    type: string
    event: string
    data: any
    timestamp: string

    message: string
}


export interface WsRequest {
    event: string
    data?: any

}
