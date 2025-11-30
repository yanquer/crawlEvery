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

