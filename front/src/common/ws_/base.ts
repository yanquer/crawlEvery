

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

    // 上轮环游个数
    last_word_count?: number
    // 上轮环游合计
    last_word_count_total?: number

    // 环游差值
    word_count_sub?: number

    // 心动鸭
    duck_count?: number
    duck_count_total?: number

    // 上轮心动鸭
    last_duck_count?: number
    last_duck_count_total?: number

    // 环游 - 心动鸭 差值
    world_sub_duck?: number

}


