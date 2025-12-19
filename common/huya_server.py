# coding: utf-8
import logging
from typing import Dict

import requests

from common.common_util.components.async_.http_ import async_http_post, async_http_get

_LOGGER = logging.getLogger(__name__)


class HuYaServer(object):

    message_url = 'https://hy.wepxtop.online/v1/message/'
    room_url = 'https://hy.wepxtop.online/v1/live/'

    @classmethod
    async def get_need_handle_room_a(cls) -> Dict[str, str]:
        """ 获取需要爬的直播间 """
        async with async_http_get(
                url=cls.room_url,
                without_ssl=True,
        ) as resp:
            if resp:
                if resp.status == 200:
                    _LOGGER.info(f'获取需要爬的直播间成功')
                    return await resp.json()
                else:
                    text_ = await resp.text()
                    _LOGGER.info(f'获取需要爬的直播间失败, {text_}')
            else:
                _LOGGER.error(f'获取需要爬的直播间失败, 请检查, ')

        return {}

    @classmethod
    def get_need_handle_room(cls) -> Dict[str, str]:
        """ 同步 获取需要爬的直播间 """
        resp = requests.get(
            url=cls.room_url,
            verify=False,
        )

        if resp:
            if resp.status_code == 200:
                _LOGGER.info(f'获取需要爬的直播间成功')
                return resp.json()
            else:
                text_ = resp.text
                _LOGGER.info(f'获取需要爬的直播间失败, {text_}')
        else:
            _LOGGER.error(f'获取需要爬的直播间失败, 请检查, ')

        return {}

    @classmethod
    async def upload_item(cls, item: 'GiftInfoItem'):
        """ 上传到服务器 """
        _LOGGER.debug(f'_upload_item: {item}')
        async with async_http_post(
                url=cls.message_url,
                without_ssl=True,
                json_data=dict(
                    user_name=item.user_name,
                    up_name=item.up_name,
                    action=item.action,
                    num=item.num,
                    gift_name=item.gift_name,
                    room=item.room,
                    time=item.time,
                    time_second_to_end=item.time_second_to_end,
                    # time_round=item.time_round,
                )
        ) as resp:
            if resp:
                if resp.status == 204:
                    _LOGGER.info(f'上传成功')
                else:
                    text_ = await resp.text()
                    _LOGGER.info(f'上传失败, {text_}')
            else:
                _LOGGER.error(f'上传失败, 请检查, ')


HU_YA_SERVER: HuYaServer = HuYaServer()

