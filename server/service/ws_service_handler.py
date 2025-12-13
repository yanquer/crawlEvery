# coding: utf-8
import logging
import os

from common.utils import read_xlsx, get_rooms
from server.base import WsReceive

_LOGGER = logging.getLogger(__name__)


class WsServiceHandler(object):
    _inited = False

    async def init_rooms(self):
        """ 第一次链的时候, 开直播间 """
        # 检查一下如果没有直播间, 就重新初始化
        from .gift_service import GIFT_SERVICE
        if not GIFT_SERVICE.check_room_ids:
            self._inited = False

        if self._inited:
            return
        self._inited = True

        used = get_rooms()

        room_ids_str = ','.join(used)
        await GIFT_SERVICE.check_rooms(room_ids_str)

    async def handle_message(self, ws_data: WsReceive):
        from server.service.gift_service import GIFT_SERVICE

        _LOGGER.debug(f"Received message: {ws_data}", )

        if ws_data.event == "room":
            await GIFT_SERVICE.notify_room()


WS_SERVICE_HANDLER = WsServiceHandler()
