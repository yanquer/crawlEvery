# coding: utf-8
import json
from dataclasses import dataclass, asdict
from typing import Union


@dataclass
class SimpleModel(object):

    def get_dict(self):
        return asdict(self)

    def get_json_str(self):
        return json.dumps(self.get_dict())

    @classmethod
    def from_json(cls, data: Union[str, dict]):
        if data:
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.decoder.JSONDecodeError:
                    data = {}

            data: dict = data

            return cls(**{k: v for k,v in data.items() if k in cls.__dataclass_fields__})

        return None

