# coding: utf-8
import os
from typing import Union

import pandas as pd


def read_xlsx(file_name: str, *,
              sheet_name: Union[str, int] = 0,
              ) -> dict:
    """
        sheet_name
            特定工作表 或者 按索引读取
    """
    df = pd.read_excel(
        file_name,
        sheet_name=sheet_name,
    )

    # 读 房间名, 房间号
    return dict(zip(
        df['房间号'],
        df['房间名'],
    ))


def get_rooms():
    room_dat = read_xlsx('resources/meta/统计.xlsx')
    room_ids = list(room_dat.keys())

    max_room = 5
    if env_max_room := os.environ.get('S_HY_MAX_TASKS'):
        if env_max_room.isdigit():
            max_room = int(env_max_room)

    used = [str(x) for x in room_ids][:max_room]

    return used


