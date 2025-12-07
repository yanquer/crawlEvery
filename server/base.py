# coding: utf-8
from dataclasses import dataclass, asdict
from typing import Union


@dataclass
class Result(object):

    code: int = 0
    message: str = ""
    data: Union[dict, list] = None

    def get_dict(self):
        return asdict(self)
