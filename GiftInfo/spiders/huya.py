import asyncio
import logging

from scrapy import Selector
from scrapy.selector import SelectorList

from GiftInfo.items import GiftInfoItem
from common.base_playwright import BasePlayWrightSpider


_LOGGER = logging.getLogger(__name__)


# class HuyaSpider(scrapy.Spider):
class HuyaSpider(BasePlayWrightSpider):
    name = "huya"
    allowed_domains = ["www.huya.com"]
    start_urls = ["https://www.huya.com/"]

    CONCURRENT_REQUESTS = 1
    _REUSE_PAGE = True
    HEADLESS = False
    room_ids = [
        '13168',
    ]

    def start_requests(self):

        self.start_urls = [
            f'{self.start_urls[0]}{r}' for r in self.room_ids
        ]

        _LOGGER.info(f'will spider {self.start_urls}')

        # super().start_requests()

        for one in self.start_urls:
            yield self._request_url_as_playwright(one, callback=self.parse,)


    _already_find_msg_max_id = 0

    async def parse(self, response, **kwargs):
        page = response.meta['playwright_page']
        # url = response.url


        while 1:
            page_response_lastest = await self.refresh_playwright_response(response, 1000)
            await page.wait_for_timeout(1000)  # 等待 1 秒，确保内容加载

            chat_room_msgs: SelectorList = page_response_lastest.css('#chat-room__list')

            msg_divs: SelectorList = chat_room_msgs.css('div[data-cmid]')

            _LOGGER.info(f'本次发现 {len(msg_divs)} 消息')
            for one in msg_divs:
                one: Selector
                msg_front_id = one.attrib['data-cmid']

                if int(msg_front_id) <= self._already_find_msg_max_id:
                    continue
                self._already_find_msg_max_id = max(int(msg_front_id), self._already_find_msg_max_id)

                _LOGGER.info(f'开始解析 msg_front_id: {msg_front_id}')

                # 找送礼物消息
                if send_msg := one.css(f'div.tit-h-send'):
                    send_msg = send_msg[0]

                    msg_info = send_msg.css('.cont-item')

                    if msg_info and len(msg_info) >= 4:
                        span_name, _, span_gift, span_gift_num, *_ = msg_info

                        user_name = span_name.css('::text').get()
                        span_gift_desc = span_gift.css('img').attrib['alt']
                        gift_num = span_gift_num.css('::text').get()

                        _LOGGER.info(f'{user_name} 送 {gift_num} 个 {span_gift_desc} ')

                        yield GiftInfoItem(
                            user_name=user_name,
                            num=gift_num,
                            gift_name=span_gift_desc,
                            action="送",
                        )

                elif send_msg := one.css(f'div.msg-normal > span.msg.J_msg'):
                    msg_text = send_msg.css('::text').get()
                    if msg_text and "下单了" in msg_text:
                        msg_list = msg_text.split(' ')

                        user_name = msg_list[0]
                        up_name = msg_list[2]

                        gift_info = msg_list[4].split('×')
                        # print(gift_info)
                        up_namespan_gift_desc = gift_info[0]
                        gift_num = gift_info[1]

                        _LOGGER.info(f'{user_name} 下单 {gift_num} 个 {span_gift_desc} 给 {up_name}')

                        yield GiftInfoItem(
                            user_name=user_name,
                            num=gift_num,
                            gift_name=span_gift_desc,
                            up_name=up_name,
                            action="下单",
                        )

            # 一分钟刷新一次, 如果消息多, 需要更短间隔时间
            # await asyncio.sleep(1*60)
            await page.wait_for_timeout(1*10 * 1000)


