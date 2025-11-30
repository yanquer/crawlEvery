# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


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
        # ensure_ascii=False , 中文正常解码
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
        self._file.write(line)
        return item

