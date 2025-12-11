# coding: utf-8
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
from datetime import datetime

from starlette.middleware.cors import CORSMiddleware

from .manager import global_ws_manager
from ..base import WsReceive
from ..defines import app


_LOGGER = logging.getLogger(__name__)


app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket 端点
@app.websocket("/ws/room")
async def websocket_chat(websocket: WebSocket, user_id: str = None):
    # 连接 默认就是订阅模式, 后面有空再分出来
    user_id = await global_ws_manager.connect(websocket, user_id)

    try:
        # 发送欢迎消息
        welcome_msg = json.dumps({
            "type": "welcome",
            "event": "welcome",
            "message": f"用户 {user_id} 进入!",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })
        await global_ws_manager.send_personal_message(welcome_msg, websocket)

        # 主消息循环
        while True:
            data = await websocket.receive_text()

            # 解析消息
            try:
                message_data = json.loads(data)
                from ..service.ws_service_handler import WS_SERVICE_HANDLER

                await WS_SERVICE_HANDLER.handle_message(
                    WsReceive.from_json(message_data)
                )
            except json.JSONDecodeError:
                # 处理纯文本消息
                msg = f'not support msg {data}'
                # await global_ws_manager.broadcast_json(text_message)
                _LOGGER.info(msg)

    except WebSocketDisconnect:
        # 断开连接处理
        global_ws_manager.disconnect(websocket)

        disconnect_msg = {
            "type": "user_left",
            "user_id": user_id,
            "message": f"用户 {user_id} 已离开",
            "timestamp": datetime.now().isoformat()
        }
        _LOGGER.info(disconnect_msg)



