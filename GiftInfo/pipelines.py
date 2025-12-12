# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import json
import logging
import os

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from GiftInfo.items import GiftInfoItem
from common.defines import ROOM_OUT_MSG_HEADER

_LOGGER = logging.getLogger(__name__)


class GiftinfoPipeline:
    def process_item(self, item, spider):
        return item


class JsonWriterPipeline:
    def open_spider(self, spider):
        # file_ = "resources/items_" + time.ctime() + ".jsonl"
        file_ = f"resources/details/item_{spider.name}.jsonl"
        if not os.path.exists(t := os.path.dirname(file_)):
            os.makedirs(t)
        self._file = open(file_, "a+")

    def close_spider(self, spider):
        self._file.close()

    _count = 0
    def process_item(self, item, spider):
        _LOGGER.debug(f"process_item: {item}")
        # ensure_ascii=False , 中文正常解码
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
        self._file.write(line)
        # 立即写入文件
        self._file.flush()
        return item


# class JsonWriterDayPipeline:
#     """ 按照天统计
#
#
#         2024-10-1: {
#             url: {
#                 幻梦爱做梦: {
#                     "买": {
#                         虎粮: 10,
#                         虎粮,up: 10,
#                     },
#                     "下单": {
#                         虎粮: 10,
#                         虎粮,up: 10,
#                     }
#                 }
#             }
#         }
#     """
#
#     _day_data = {}
#     _file_name = ''
#
#     def open_spider(self, spider):
#         self._day_data = {}
#
#         # file_ = "resources/items_" + time.ctime() + ".jsonl"
#         file_ = f"resources/details/item_{spider.name}_day.jsonl"
#         self._file_name = file_
#         if not os.path.exists(t := os.path.dirname(file_)):
#             os.makedirs(t)
#
#         if os.path.isfile(file_):
#             with open(file_, "r", encoding="utf-8") as f:
#                 for line in f:
#                     if line:
#                         self._day_data.update(json.loads(line))
#
#             # with open(file_, "w", encoding="utf-8") as f:
#             #     f.write("")
#
#         # self._file = open(file_, "w")
#         ...
#
#     def close_spider(self, spider):
#         # self._file.close()
#         ...
#
#     _count = 0
#     def process_item(self, item: GiftInfoItem, spider):
#         _LOGGER.debug(f"process_item: {item}")
#         date_now = datetime.datetime.now().strftime("%Y-%m-%d")
#
#         if date_now not in self._day_data:
#             self._day_data[date_now] = {}
#
#         if item.room not in self._day_data[date_now]:
#             self._day_data[date_now][item.room] = {}
#
#         day_url_dat = self._day_data[date_now][item.room]
#         if item.user_name not in day_url_dat:
#             day_url_dat[item.user_name] = {}
#
#         day_user_dat = day_url_dat[item.user_name]
#         if item.action not in day_user_dat:
#             day_user_dat[item.action] = {}
#
#         dat_action_dat = day_user_dat[item.action]
#         if item.up_name:
#             k1 = item.gift_name
#             k2 = (item.gift_name, item.up_name)
#
#             keys = (k1, k2)
#         else:
#             k1 = item.gift_name
#             keys = k1,
#
#         for k in keys:
#             if k not in dat_action_dat:
#                 dat_action_dat[k] = int(item.num)
#             else:
#                 lst = int(dat_action_dat[k] or 0)
#                 dat_action_dat[k] = int(item.num) + lst
#
#         # ensure_ascii=False , 中文正常解码
#         with open(self._file_name, "w", encoding="utf-8") as f:
#             for k, v in self._day_data.items():
#                 _LOGGER.debug(f"process_item: {k} {v}")
#                 line = json.dumps({k: v}, ensure_ascii=False) + "\n"
#                 f.write(line)
#         return item


class JsonWriterTimeRangePipeline:
    """ 按照轮次与直播间统计

        2024-10-1: {
            all_total: {
                带你环游: 1,
                心动鸭: 10,
            },
            url_total: {
                带你环游: 1,
                心动鸭: 10,
            },
            url: {
                幻梦爱做梦(粉丝): {
                    带你环游: 1,
                    心动鸭: 10,
                }
            }
        }

        每到下一轮次出发一次记录
    """

    _time_range_data = {}
    _file_name = ''

    def open_spider(self, spider):
        self._time_range_data = {}

        # file_ = "resources/items_" + time.ctime() + ".jsonl"
        file_ = f"resources/details/item_{spider.name}_time_range.jsonl"
        self._file_name = file_
        if not os.path.exists(t := os.path.dirname(file_)):
            os.makedirs(t)

    def close_spider(self, spider):
        # self._file.close()
        ...


    # 每次只记录当前轮次数据
    _current_range_data = {

    }
    _filter_gift_names = {
        '带你环游', '心动鸭'
    }
    _last_time_round: str = None
    _count = 0
    def process_item(self, item: GiftInfoItem, spider):
        _LOGGER.debug(f"process_item: {item}")

        if not item.gift_name in self._filter_gift_names:
            return item
        if not item.room:
            return item
        if not item.time_round:
            return item

        date_now = datetime.datetime.now().strftime("%Y-%m-%d")
        al_out = False
        if (self._last_time_round is not None) and (
                self._last_time_round != item.time_round
        ):
            # 记录当前的, 清空,
            # ensure_ascii=False , 中文正常解码
            with open(self._file_name, "a+", encoding="utf-8") as f:
                line = json.dumps({
                    f"{self._last_time_round}@@@{date_now}": self._current_range_data
                }, ensure_ascii=False) + "\n"
                f.write(line)
                print(f'{ROOM_OUT_MSG_HEADER}{line}')
                al_out = True
            self._current_range_data = {}
            self._last_time_round = item.time_round
        if self._last_time_round is None:
            self._last_time_round = item.time_round

        keys = (
            'all_total',
            f'{item.room}_total',
        )

        for k in keys:
            if k not in self._time_range_data:
                self._time_range_data[k] = {
                    gm: 0 for gm in self._filter_gift_names
                }

        if item.gift_name in self._filter_gift_names:

            cur_num_str: str = item.num
            if cur_num_str.isdigit():
                cur_num = int(cur_num_str)

                # all_total
                # 所有直播间统计
                self._time_range_data['all_total'][item.gift_name] += cur_num

                # f'{item.room}_total'
                # 每个直播间统计
                self._time_range_data[f'{item.room}_total'][item.gift_name] += cur_num

                # 每个直播间 分 粉丝统计
                if item.room not in self._time_range_data:
                    self._time_range_data[item.room] = {
                        # 分用户, 谁下单买的
                    }
                    room_url_dat = self._time_range_data[item.room]
                    if item.user_name not in room_url_dat:
                        room_url_dat[item.user_name] = {
                            gm: 0 for gm in self._filter_gift_names
                        }
                    room_url_dat[item.user_name][item.gift_name] += cur_num

        if self._last_time_round:
            if not al_out:
                line = json.dumps({
                    f"{self._last_time_round}@@@{date_now}": self._current_range_data
                }, ensure_ascii=False) + "\n"
                print(f'{ROOM_OUT_MSG_HEADER}{line}')

        return item
