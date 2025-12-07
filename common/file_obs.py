# coding: utf-8


"""
    监听文件变化
"""
import logging
from typing import Callable, Tuple

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os


_LOGGER = logging.getLogger(__name__)



class FileChangeHandler(FileSystemEventHandler):
    """文件变化处理器"""

    def on_any_event(self, event):
        """任何事件发生时触发"""
        _LOGGER.debug(f"事件类型: {event.event_type}")
        _LOGGER.debug(f"事件路径: {event.src_path}")
        _LOGGER.debug(f"是否为目录: {event.is_directory}")
        _LOGGER.debug("-" * 50)

    def on_created(self, event):
        """文件/目录创建时触发"""
        if event.is_directory:
            _LOGGER.debug(f"📁 目录创建: {event.src_path}")
        else:
            _LOGGER.debug(f"📄 文件创建: {event.src_path}")
            # 可以在这里处理新文件
            if event.src_path.endswith('.txt'):
                self._process_new_file(event.src_path)

    def on_deleted(self, event):
        """文件/目录删除时触发"""
        if event.is_directory:
            _LOGGER.debug(f"🗑️  目录删除: {event.src_path}")
        else:
            _LOGGER.debug(f"🗑️  文件删除: {event.src_path}")

    def on_modified(self, event):
        """文件/目录修改时触发"""
        if event.is_directory:
            _LOGGER.debug(f"📁 目录修改: {event.src_path}")
        else:
            _LOGGER.debug(f"📄 文件修改: {event.src_path}")
            # 避免重复触发（如保存文件时可能多次触发）
            if hasattr(self, '_last_modified') and time.time() - self._last_modified < 0.5:
                return
            self._last_modified = time.time()

            # 处理文件内容变化
            if event.src_path.endswith(('.txt', '.py', '.json')):
                self._process_file_change(event.src_path)

    def on_moved(self, event):
        """文件/目录移动或重命名时触发"""
        _LOGGER.debug(f"📦 移动/重命名: {event.src_path} -> {event.dest_path}")

    def _process_new_file(self, filepath):
        """处理新文件"""
        try:
            file_size = os.path.getsize(filepath)
            _LOGGER.debug(f"📊 新文件大小: {file_size} bytes")
        except Exception as e:
            _LOGGER.debug(f"❌ 处理新文件时出错: {e}")

    def _process_file_change(self, filepath):
        """处理文件变化"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                _LOGGER.debug(f"📝 文件内容行数: {len(lines)}")
        except Exception as e:
            _LOGGER.debug(f"❌ 读取文件时出错: {e}")


def monitor_file(path_to_watch: str, ext_do: Callable[[str], None]) -> Tuple[FileChangeHandler, Callable[[], None]]:

    """ 监听文件变化事件, 返回停止函数 """

    event_handler = FileChangeHandler()
    observer = Observer()

    # 开始监控
    observer.schedule(event_handler, path_to_watch, recursive=False)
    observer.start()

    return event_handler, lambda: observer.stop()


def monitor_directory(path_to_watch=".", recursive=True):
    """监控目录变化"""
    event_handler = FileChangeHandler()
    observer = Observer()

    # 开始监控
    observer.schedule(event_handler, path_to_watch, recursive=recursive)
    observer.start()

    _LOGGER.debug(f"👀 开始监控目录: {os.path.abspath(path_to_watch)}")
    _LOGGER.debug(f"📁 递归监控: {recursive}")
    _LOGGER.debug("按 Ctrl+C 停止监控")
    _LOGGER.debug("=" * 50)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        _LOGGER.debug("\n🛑 停止监控")

    observer.join()


# 使用示例
if __name__ == "__main__":
    # 监控当前目录
    monitor_directory()

    FileChangeHandler()

    # 监控特定目录（递归）
    # monitor_directory("/path/to/watch", recursive=True)

    # 监控特定目录（非递归）
    # monitor_directory("/path/to/watch", recursive=False)




