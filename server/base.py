# coding: utf-8
import datetime
from dataclasses import dataclass, asdict
from typing import Union

from common.base import SimpleModel


@dataclass
class Result(SimpleModel):

    code: int = 0
    message: str = ""
    data: Union[dict, list] = None

    def get_dict(self):
        return asdict(self)


@dataclass
class WsResult(SimpleModel):

    timestamp: str
    data: any

    type: str = ""
    event: str = ""
    message: str = ""

    @classmethod
    def get_timestamp(cls) -> str:
        return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")


@dataclass
class RoomWsResult(WsResult):
    """ 当前有哪些直播间正在监听 """
    type: str = "room"
    event: str = "room"


@dataclass
class LogWsResult(WsResult):
    """ 运行日志 """
    type: str = "log"
    event: str = "log"


@dataclass
class GiftWsResult(WsResult):
    type: str = "gift"
    event: str = "gift"


@dataclass
class RoomTotalWsResult(WsResult):
    """ 直播间阶段汇总 """
    type: str = "room_total"
    event: str = "room_total"


@dataclass
class WsReceive(SimpleModel):

    event: str = ""
    data: any = None








