# coding: utf-8
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio
from datetime import datetime
import uuid

from ..defines import app


_LOGGER = logging.getLogger(__name__)


class ConnectionManager(object):
    """WebSocket 连接管理器"""

    def __init__(self):
        # 存储所有活跃连接
        self.active_connections: List[WebSocket] = []
        # 存储用户信息
        self.user_connections: Dict[str, WebSocket] = {}
        self.connection_users: Dict[WebSocket, dict] = {}

    async def connect(self, websocket: WebSocket, user_id: str = None):
        """接受新连接"""
        await websocket.accept()
        self.active_connections.append(websocket)

        # 生成用户ID（如果未提供）
        if not user_id:
            user_id = str(uuid.uuid4())

        user_info = {
            "id": user_id,
            "connected_at": datetime.now().isoformat(),
            "websocket": websocket
        }

        self.user_connections[user_id] = websocket
        self.connection_users[websocket] = user_info

        # 通知其他用户新用户加入
        await self.broadcast_user_list()
        return user_id

    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        # 获取用户信息
        user_info = self.connection_users.get(websocket)
        if user_info:
            user_id = user_info["id"]
            del self.user_connections[user_id]
            del self.connection_users[websocket]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """发送私聊消息"""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """广播给所有连接"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # 移除无效连接
                self.disconnect(connection)

    async def broadcast_json(self, data: dict):
        """广播 JSON 数据"""
        message = json.dumps(data, ensure_ascii=False)
        await self.broadcast(message)

    async def send_to_user(self, user_id: str, message: str):
        """发送消息给特定用户"""
        websocket = self.user_connections.get(user_id)
        if websocket:
            await self.send_personal_message(message, websocket)

    async def broadcast_user_list(self):
        """广播在线用户列表"""
        online_users = [
            {
                "id": user_info["id"],
                "connected_at": user_info["connected_at"]
            }
            for user_info in self.connection_users.values()
        ]

        message = {
            "type": "user_list",
            "users": online_users,
            "count": len(online_users),
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_json(message)


# 创建全局连接管理器
global_ws_manager = ConnectionManager()


