# coding: utf-8
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



