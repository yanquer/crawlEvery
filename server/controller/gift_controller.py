# coding: utf-8

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from ..base import Result
from ..defines import app
from ..service.gift_service import GIFT_SERVICE


@app.get("/gift/{room_ids}")
async def root(room_ids: str):
    # GIFT_SERVICE.create_task()
    await GIFT_SERVICE.check_rooms(room_ids)
    return Result(data={f"message": f"Hello {room_ids}"}).get_dict()


class GiftController(object):
    ...


# ####
# # ws
# @app.websocket("/rooms")
# async def get_rooms(websocket: WebSocket):
#






