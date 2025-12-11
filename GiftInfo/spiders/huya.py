import asyncio
import datetime
import logging

from playwright.async_api import ElementHandle, Page
from scrapy import Selector
from scrapy.http import HtmlResponse, Response
from scrapy.selector import SelectorList

from GiftInfo import CHECK_ROOMS
from GiftInfo.items import GiftInfoItem
from common.base_playwright import BasePlayWrightSpider
from common.js_helper import JS_MUTE

_LOGGER = logging.getLogger(__name__)


# class HuyaSpider(scrapy.Spider):
class HuyaSpider(BasePlayWrightSpider):
    name = "huya"
    allowed_domains = ["www.huya.com"]
    start_urls = ["https://www.huya.com/"]

    # room_ids = [
    #     '13168',
    #     'beisheng1117',
    # ]
    room_ids = CHECK_ROOMS

    CONCURRENT_REQUESTS = len(room_ids)
    _REUSE_PAGE = True
    # HEADLESS = False

    def start_requests(self):

        _LOGGER.info(f'需要检查的房间 {self.room_ids}')

        self.start_urls = [
            f'{self.start_urls[0]}{r}' for r in self.room_ids
        ]

        _LOGGER.info(f'will spider {self.start_urls}')

        # super().start_requests()

        for one in self.start_urls:
            yield self._request_url_as_playwright(one, callback=self.parse,)


    _already_find_msg_max_id = 0

    def _parse_msg(self,
                         url: str,
                         page_response_lastest: HtmlResponse,
                         ):
        chat_room_msgs: SelectorList = page_response_lastest.css('#chat-room__list')
        msg_divs: SelectorList = chat_room_msgs.css('div[data-cmid]')

        _LOGGER.info(f'本次发现 {len(msg_divs)} 消息')
        date_str = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
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
                        room=url,
                        time=date_str,
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
                        room=url,
                        time=date_str,
                    )

    async def _get_text(self, element: ElementHandle, css_selector: str):
        return await element.evaluate('''(element) => {
                                return element.innerText;
                            }''', css_selector)



    async def _parse_current_go_word(self,
                                     url: str,
                                     page_response_lastest: HtmlResponse,
                                     response: Response,
                                     ):
        """ 解析 带你环游游戏 """
        _LOGGER.info(f'准备自动化打开带你环游窗口')
        page = response.meta['playwright_page']

        # 判断一下是否打开 游戏窗口
        #   倒计时心形窗口
        go_word_wind_heart: ElementHandle = None
        heart_css = '.css-1dbjc4n.r-1awozwy.r-1777fci.r-u8s1d'
        # 权限请求那个 允许 按钮
        # per_sure_btn_css = '.modalBtn-09efa8bb.jqOk-68b2316b.modalBtnPrimary-0d919eb5'
        per_sure_btn_css = '.jqOk-68b2316b'

        heart_btn_css = '.more-attivity-panel #front-ojhmr5vg_web_video_com'

        # await asyncio.sleep(30)
        # while 1:
        #     _LOGGER.info(f'触发更多选项')
        #     await self._move_mouse_to_css_center(response=response, css_selector='.more-activity-icon')
        #     await asyncio.sleep(3)

        open_win = False
        while 1:
            if (not go_word_wind_heart) and (not open_win):
                ...
                # 尝试将心动环游点出来
                # await page.hover('.more-activity-icon')
                # await page.wait_for_timeout(0.1 * 1000)
                # await page.click('.more-activity-icon')
                if await self._move_mouse_to_css_center(response=response, css_selector='.more-activity-icon'):
                    # await asyncio.sleep(60)
                    _LOGGER.info(f'{url} 点击 带你环游')
                    await page.click(heart_btn_css)
                    await page.wait_for_timeout(0.5 * 1000)
                    # 可能会出现请求权限窗口, 检查一下然后允许
                    open_win = True

            if open_win:
                body_iframes: ElementHandle = await page.query_selector('body iframe')

                for iframe_ele in [body_iframes]:
                    if iframe_ele:
                        iframe_page = await iframe_ele.content_frame()

                        # 可能会出现请求权限窗口, 检查一下然后允许
                        # t = await page.query_selector_all(per_sure_btn_css)
                        for find_ele in await page.query_selector_all(per_sure_btn_css):
                            # t = await find_ele.text_content()
                            if await find_ele.text_content() == '允许':
                                await find_ele.click()

                        t = await iframe_page.query_selector_all('iframe')
                        if iframe_son_l1 := await iframe_page.query_selector('iframe'):
                            iframe_son_l1_iframe = await iframe_son_l1.content_frame()
                            # todo: iframe 获取的内容不对,
                            t0 = await iframe_son_l1_iframe.content()
                            for find_ele in await iframe_son_l1_iframe.query_selector_all(heart_css):
                                t = await find_ele.query_selector(heart_btn_css)
                                if await find_ele.query_selector(heart_btn_css):
                                    go_word_wind_heart = find_ele

            if (not go_word_wind_heart):
                _LOGGER.info(f'{url} 未检测到心动环游窗口打开, 请先在任一页面登录, 3s 后将刷新页面重试... ')
                await page.wait_for_timeout(1 * 3 * 1000)
            else:
                break

        #
        _LOGGER.info(f'成功找到带你环游窗口')
        text_div = await go_word_wind_heart.query_selector('.css-1dbjc4n.r-1awozwy')
        msg_1_div = await text_div.query_selector('.css-1dbjc4n.r-1awozwy')
        text = await text_div.text_content()

        print(text)

    async def _wait_for_login_by_text(self,
                                      response: Response,
                                      user_selector: str=None,
                                      user_success_text: str=None):
        page: Page = response.meta['playwright_page']
        url = response.url

        while 1:
            page_response_lastest = await self.refresh_playwright_response(response, 1000)
            right_nav = page_response_lastest.css("#J_duyaHeaderRight")
            if right_nav:
                if header_dy := right_nav.css(".HeaderDynamic--3HooPjEhfERVcNlLZt1RkY"):
                    class_name = header_dy.attrib['class']
                    if 'Logined' in class_name:
                        await self._save_user_cookies(response)
                        _LOGGER.info(f'{url} 登录成功')
                        return True

            _LOGGER.info(f'{url} 等待登录中...')
            await page.reload()
            # 等半分钟, 因为人工登录的时候要一会儿
            await page.wait_for_timeout(1 * 30 * 1000)

        return False

    async def parse(self, response, **kwargs):
        page = response.meta['playwright_page']
        url = response.url

        while 1:

            # todo: 放到 docker 里了 暂时取消主动登录
            # await self._wait_for_login_by_text(response=response,)

            page_response_lastest = await self.refresh_playwright_response(response, 1000)
            await page.wait_for_timeout(1000)  # 等待 1 秒，确保内容加载
            await page.evaluate(JS_MUTE)

            # todo: 放到 docker 里了 暂时取消打开环游界面
            # await self._parse_current_go_word(url=url,
            #                                   page_response_lastest=page_response_lastest,
            #                                   response=response)

            for msg_ret in self._parse_msg(url=url, page_response_lastest=page_response_lastest):
                yield msg_ret

            # 一分钟刷新一次, 如果消息多, 需要更短间隔时间
            # await asyncio.sleep(1*60)
            await page.wait_for_timeout(1*1 * 1000)


