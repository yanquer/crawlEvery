# coding: utf-8
import logging

from server.base import WsReceive


_LOGGER = logging.getLogger(__name__)


class WsServiceHandler(object):


    async def handle_message(self, ws_data: WsReceive):
        from server.service.gift_service import GIFT_SERVICE

        _LOGGER.debug(f"Received message: {ws_data}",)

        if ws_data.event == "room":
            await GIFT_SERVICE.notify_room()


WS_SERVICE_HANDLER = WsServiceHandler()



