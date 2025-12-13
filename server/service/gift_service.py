# coding: utf-8
import asyncio
import copy
import logging
import os
import random
from asyncio import StreamReader
from asyncio.subprocess import Process
from typing import Dict, List, Set, Optional, Union

from common.defines import ROOM_OUT_MSG_HEADER, IS_DEBUG_MODE
from common.file_obs_async import global_file_monitor
from .message_center import MESSAGE_CENTER
from ..base import Result, WsResult, RoomTotalWsResult, LogWsResult, GiftWsResult
from ..defines import PROJECT_ROOT

_LOGGER = logging.getLogger(__name__)


class CrawlOutputHandler(object):
    check_room_ids: Set[str]

    _need_always_msg: Dict[str, Union[WsResult, List[WsResult]]] = []
    async def need_always_send(self):
        """ 有些消息需要一直发, 来解决前端刷新页面后就没了的情况 """
        while 1:
            await self._handle_always_msg()
            await asyncio.sleep(1)

    async def _handle_always_msg(self, ):
        for ws_ret in self._need_always_msg.values():
            if ws_ret:
                if isinstance(ws_ret, WsResult):
                    await MESSAGE_CENTER.handle_message(ws_ret)
                elif isinstance(ws_ret, list):
                    for one in ws_ret:
                        if isinstance(one, WsResult):
                            await MESSAGE_CENTER.handle_message(one)

    # 实时读取标准输出
    async def read_stream(self, stream: StreamReader, stream_name: str):
        """读取并解析流数据"""
        while True:
            line = await stream.readline()
            if not line:
                break
            line = line.decode().strip()
            _LOGGER.debug(f"[{stream_name}] {line}")

            # todo: 临时放这, 随机发
            if random.choice([True, False]):
                await self._handle_always_msg()
            if line and ROOM_OUT_MSG_HEADER in line:
                ret = GiftWsResult(
                    timestamp=WsResult.get_timestamp(),
                    data=line.split(ROOM_OUT_MSG_HEADER)[1].strip(),
                )
                self._need_always_msg["gift"] = ret
            else:
                ret = LogWsResult(
                    timestamp=WsResult.get_timestamp(),
                    data=line,
                )

            # print(line)
            await MESSAGE_CENTER.handle_message(ret)
            # await MESSAGE_CENTER.notify_room(self.check_room_ids)


class GiftService(object):
    """ 解析指定的虎牙直播间

        room_ids 直播间id, 浏览器中 url 的最后一串字符
    """

    def __init__(self, ):
        self.check_room_ids = set()
        self.run_tasks: Dict[str, Optional[Process]] = {}

        self._output_handler = CrawlOutputHandler()

        # self._start_check_new_msg()

    _already_create = False
    def create_task(self):
        if self._already_create:
            return
        self._already_create = True
        # asyncio.create_task(MESSAGE_CENTER.send_alive_message())
        asyncio.create_task(self._output_handler.need_always_send())

    async def check_rooms(self, room_ids: str):

        tmp_ids = set()
        for room_id in room_ids.split(','):
            room_id = room_id.strip()
            if room_id in self.check_room_ids:
                continue
                # return False, f'{room_id} already checked'
            tmp_ids.add(room_id)

        self.check_room_ids.update(tmp_ids)
        await self.notify_room()

        asyncio.create_task(self._start_check(",".join(list(tmp_ids))))
        return True, None

    async def _start_check(self, room_ids: str):
        _env = copy.deepcopy(os.environ)
        _env.update({
            'CE_FS_CHECK_ROOMS': room_ids
        })

        process = await asyncio.create_subprocess_exec(
            # 'python3',
            '/usr/src/app/.venv/bin/python' if not IS_DEBUG_MODE else "python3",
            'main.py',
            env=_env,
            cwd=PROJECT_ROOT,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            # start_new_session=True,
        )
        self.run_tasks[room_ids] = process

        # 并发读取stdout和stderr
        await asyncio.gather(
            self._output_handler.read_stream(process.stdout, "stdout"),
            self._output_handler.read_stream(process.stderr, "stderr")
        )

        stdout, stderr = await process.communicate()

        ret = True
        if process.returncode != 0:
            ret = False

        # 进程结束后, 需要移除对应的直播间
        self.run_tasks[room_ids] = None
        for room_id in room_ids.split(','):
            self.check_room_ids.remove(room_id)
        # 发消息
        await MESSAGE_CENTER.notify_room(room_ids=self.check_room_ids)

        return ret

    async def clear(self):

        for t in self.run_tasks.values():
            try:
                if t:
                    t.kill()
            except Exception as e:
                _LOGGER.warning(f'Failed to kill {t} error: {e}')

        self.run_tasks = {}
        self.check_room_ids = set()


    _check_file = ''

    async def _start_check_new_msg(self):
        ...

        global_file_monitor.start_monitoring(
            self._check_file,
            recursive=False,
        )
        global_file_monitor.register_handler('modified', self._check_change_file)
        global_file_monitor.register_handler('created', self._check_change_file)

    async def _check_change_file(self, event_data):
        ...


    async def _check_new_msg(self):
        ...

        # while 1:
        #     await asyncio.sleep(1)
        #
        #     if os.path.exists(self._check_file):
        #         ret = Result()
        #         global_ws_manager.broadcast_json(ret.get_dict())

    async def notify_room(self, ):
        await MESSAGE_CENTER.notify_room(self.check_room_ids)


GIFT_SERVICE = GiftService()


