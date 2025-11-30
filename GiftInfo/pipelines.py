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


class JsonWriterDayPipeline:
    """ 按照天统计


        2024-10-1: {
            url: {
                幻梦爱做梦: {
                    "买": {
                        虎粮: 10,
                        虎粮,up: 10,
                    },
                    "下单": {
                        虎粮: 10,
                        虎粮,up: 10,
                    }
                }
            }
        }
    """

    _day_data = {}
    _file_name = ''

    def open_spider(self, spider):
        self._day_data = {}

        # file_ = "resources/items_" + time.ctime() + ".jsonl"
        file_ = f"resources/details/item_{spider.name}_day.jsonl"
        self._file_name = file_
        if not os.path.exists(t := os.path.dirname(file_)):
            os.makedirs(t)

        if os.path.isfile(file_):
            with open(file_, "r", encoding="utf-8") as f:
                for line in f:
                    if line:
                        self._day_data.update(json.loads(line))

            # with open(file_, "w", encoding="utf-8") as f:
            #     f.write("")

        # self._file = open(file_, "w")
        ...

    def close_spider(self, spider):
        # self._file.close()
        ...

    _count = 0
    def process_item(self, item: GiftInfoItem, spider):
        _LOGGER.debug(f"process_item: {item}")
        date_now = datetime.datetime.now().strftime("%Y-%m-%d")

        if date_now not in self._day_data:
            self._day_data[date_now] = {}

        if item.room not in self._day_data[date_now]:
            self._day_data[date_now][item.room] = {}

        day_url_dat = self._day_data[date_now][item.room]
        if item.user_name not in day_url_dat:
            day_url_dat[item.user_name] = {}

        day_user_dat = day_url_dat[item.user_name]
        if item.action not in day_user_dat:
            day_user_dat[item.action] = {}

        dat_action_dat = day_user_dat[item.action]
        if item.up_name:
            k1 = item.gift_name
            k2 = (item.gift_name, item.up_name)

            keys = (k1, k2)
        else:
            k1 = item.gift_name
            keys = k1,

        for k in keys:
            if k not in dat_action_dat:
                dat_action_dat[k] = int(item.num)
            else:
                lst = int(dat_action_dat[k] or 0)
                dat_action_dat[k] = int(item.num) + lst

        # ensure_ascii=False , 中文正常解码
        with open(self._file_name, "w", encoding="utf-8") as f:
            for k, v in self._day_data.items():
                line = json.dumps({k: v}, ensure_ascii=False) + "\n"
                f.write(line)
        return item


