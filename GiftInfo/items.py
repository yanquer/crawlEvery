# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GiftInfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # pass

    user_name = scrapy.Field()
    up_name = scrapy.Field()

    # 送 / 下单
    action = scrapy.Field()

    # 数量
    num = scrapy.Field()

    # 礼物
    gift_name = scrapy.Field()
    # 直播间
    room = scrapy.Field()
    time = scrapy.Field()

    # 时间戳轮次, 这里是不是要注意一下时区问题?
    #   服务器是成都的, 不用弄时区
    # time_round = scrapy.Field()
    time_second_to_end = scrapy.Field()

    def __getattr__(self, name):
        if name in self.fields:
            try:
                return self[name]
            except KeyError:
                return None
        return super().__getattr__(name)


