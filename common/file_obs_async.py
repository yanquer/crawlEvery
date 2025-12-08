# coding: utf-8


"""
    监听文件变化
"""
import logging


import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, DirCreatedEvent, FileCreatedEvent

from typing import Dict, List, Union

from datetime import datetime


_LOGGER = logging.getLogger(__name__)


class AsyncFileMonitor(object):
    """异步文件监控器"""

    def __init__(self):
        self.observer = None
        self.monitoring = False
        self.watched_paths = set()
        self.event_queue = asyncio.Queue(maxsize=1000)
        self.handlers: Dict[str, List[callable]] = {}
        self.file_stats = {}

    async def start_monitoring(self, path: str, recursive: bool = True):
        """开始监控目录"""
        if path in self.watched_paths:
            return {"status": "already_monitoring", "path": path}

        # 创建事件处理器
        handler = FileSystemEventHandler()

        # 动态绑定事件处理函数
        def make_handler(event_type):
            def handler_func(event):
                asyncio.run_coroutine_threadsafe(
                    self._process_event(event_type, event),
                    asyncio.get_event_loop()
                )

            return handler_func

        # 绑定各种事件
        handler.on_created = make_handler("created")
        handler.on_deleted = make_handler("deleted")
        handler.on_modified = make_handler("modified")
        handler.on_moved = make_handler("moved")

        # 启动observer（在单独的线程中）
        if self.observer is None:
            self.observer = Observer()

        self.observer.schedule(handler, path, recursive=recursive)

        if not self.monitoring:
            self.observer.start()
            self.monitoring = True

        self.watched_paths.add(path)

        # 启动事件处理任务
        asyncio.create_task(self._event_processor())

        return {"status": "started", "path": path}

    # 注意单例
    _file_last_visit_map: Dict[str, int] = {}
    async def _check_file_context(self, file_path: str):
        """ 暂时通过行号来识别 """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                last_pos = self._file_last_visit_map.get(file_path)
                if not last_pos:
                    return f.read()

        except Exception as e:
            self._file_last_visit_map[file_path] = 0
            _LOGGER.error(f'check file context failed: {e}')

    async def _process_event(self, event_type: str, event: Union[DirCreatedEvent, FileCreatedEvent]):
        """处理文件事件"""
        event_data = {
            # created modified deleted moved
            "type": event_type,
            "path": event.src_path,
            "is_directory": event.is_directory,
            "timestamp": datetime.now().isoformat(),
            "dest_path": getattr(event, 'dest_path', None),
            'new_data': None,
        }

        # 如果是文件, 检查下新增的内容有哪些
        if not event.is_directory:
            event_data['new_data'] = await self._check_file_context(event.src_path)

        # 放入事件队列
        try:
            await self.event_queue.put(event_data)
        except asyncio.QueueFull:
            print("事件队列已满，丢弃事件")

    async def _event_processor(self):
        """事件处理器"""
        while self.monitoring:
            try:
                # 从队列获取事件
                event_data = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)

                # 触发所有注册的处理函数
                for handler in self.handlers.get(event_data["type"], []):
                    try:
                        await handler(event_data)
                    except Exception as e:
                        _LOGGER.error(f"事件处理出错: {e}")

                # 更新文件统计
                self._update_file_stats(event_data)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                _LOGGER.error(f"事件处理器出错: {e}")

    def _update_file_stats(self, event_data):
        """更新文件统计"""
        path = event_data["path"]
        event_type = event_data["type"]

        if event_type == "created":
            self.file_stats[path] = {
                "created_at": event_data["timestamp"],
                "modified_at": event_data["timestamp"],
                "event_count": 1
            }
        elif event_type == "modified":
            if path in self.file_stats:
                self.file_stats[path]["modified_at"] = event_data["timestamp"]
                self.file_stats[path]["event_count"] += 1

    async def stop_monitoring(self, path: str = None):
        """停止监控"""
        if path and path in self.watched_paths:
            self.watched_paths.remove(path)

        if not self.watched_paths and self.observer:
            self.observer.stop()
            self.observer = None
            self.monitoring = False

        return {"status": "stopped", "path": path}

    def register_handler(self, event_type: str, handler: callable):
        """注册事件处理函数"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def get_monitoring_status(self):
        """获取监控状态"""
        return {
            "monitoring": self.monitoring,
            "watched_paths": list(self.watched_paths),
            "queue_size": self.event_queue.qsize(),
            "file_stats": len(self.file_stats)
        }


# 创建全局监控器实例
global_file_monitor = AsyncFileMonitor()

# WebSocket 实时推送文件变化
# from fastapi import WebSocket, WebSocketDisconnect


# @app.websocket("/ws/file-changes")
# async def websocket_file_changes(websocket: WebSocket):
#     """WebSocket推送文件变化"""
#     await websocket.accept()
#
#     # 定义WebSocket事件处理器
#     async def websocket_handler(event_data):
#         try:
#             await websocket.send_json(event_data)
#         except:
#             pass  # WebSocket可能已断开
#
#     # 注册所有类型的事件处理器 created modified deleted moved
#     file_monitor.register_handler("created", websocket_handler)
#     file_monitor.register_handler("modified", websocket_handler)
#     file_monitor.register_handler("deleted", websocket_handler)
#     file_monitor.register_handler("moved", websocket_handler)
#
#     try:
#         # 保持连接
#         while True:
#             # 接收客户端消息（用于控制）
#             data = await websocket.receive_text()
#             if data == "ping":
#                 await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
#     except WebSocketDisconnect:
#         # WebSocket断开连接
#         pass










