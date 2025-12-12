# coding: utf-8
import logging

from common.utils import read_xlsx
from server.base import WsReceive


_LOGGER = logging.getLogger(__name__)


class WsServiceHandler(object):

    _inited = False
    async def init_rooms(self):
        """ 第一次链的时候, 开直播间 """
        if self._inited:
            return
        self._inited = True
        from .gift_service import GIFT_SERVICE

        room_dat = read_xlsx('resources/meta/统计.xlsx')
        room_ids = list(room_dat.keys())
        room_ids_str = ','.join(room_ids)
        await GIFT_SERVICE.check_rooms(room_ids_str)

    async def handle_message(self, ws_data: WsReceive):
        from server.service.gift_service import GIFT_SERVICE

        _LOGGER.debug(f"Received message: {ws_data}",)

        if ws_data.event == "room":
            await GIFT_SERVICE.notify_room()


WS_SERVICE_HANDLER = WsServiceHandler()



