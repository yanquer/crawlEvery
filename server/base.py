# coding: utf-8
import datetime
import json
from dataclasses import dataclass, asdict
from typing import Union


@dataclass
class SimpleModel(object):

    def get_dict(self):
        return asdict(self)

    def get_json_str(self):
        return json.dumps(self.get_dict())


@dataclass
class Result(SimpleModel):

    code: int = 0
    message: str = ""
    data: Union[dict, list] = None

    def get_dict(self):
        return asdict(self)


@dataclass
class WsResult(SimpleModel):

    type: str
    event: str
    data: any
    timestamp: str

    message: str = ""

    @classmethod
    def get_timestamp(cls) -> str:
        return datetime.datetime.now().isoformat()


