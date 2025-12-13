

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


// 统计消息
export interface GiftShowTableRow{

    // 轮次
    time_round: string
    // 直播间号
    room_id: string
    // 名称
    room_name: string
    // 环游个数
    word_count?: number
    // 环游合计
    word_count_total?: number
}


