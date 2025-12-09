# coding: utf-8
import asyncio
import logging
import random

from ..base import WsResult, RoomWsResult, LogWsResult
from ..ws_.manager import global_ws_manager

_LOGGER = logging.getLogger(__name__)


class MessageCenter(object):

    async def send_alive_message(self):
        """ 存活确认 """
        while True:
            _LOGGER.info(f'alive')
            cls_ = random.choice([RoomWsResult, LogWsResult])
            ret = cls_(
                data=["还活着"],
                timestamp=WsResult.get_timestamp(),
            )
            await global_ws_manager.broadcast_json(ret.get_dict())
            await asyncio.sleep(1)

    async def notify_room(self, room_ids: set):
        """ 提醒当前正在监听的直播间 """
        try:
            ret = RoomWsResult(
                data=room_ids,
                timestamp=WsResult.get_timestamp(),
            )
            await global_ws_manager.broadcast_json(ret.get_dict())
        except Exception as e:
            _LOGGER.error(f'_notify_room error: {e}')

    async def handle_message(self, message: WsResult):
        """ 通用的消息发送器 """
        await global_ws_manager.broadcast_json(message.get_dict())


MESSAGE_CENTER = MessageCenter()

