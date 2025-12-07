# coding: utf-8
from ..base import Result
from ..defines import app
from ..service.gift_service import GiftService

gift_service = GiftService()


@app.get("/gift/{room_ids}")
async def root(room_ids: str):

    return Result(data={f"message": f"Hello {room_ids}"}).get_dict()


class GiftController(object):
    ...







