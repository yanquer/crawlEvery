import asyncio
import datetime
import logging
import os
from typing import List, Optional

from playwright.async_api import ElementHandle, Page
from scrapy import Selector
from scrapy.http import HtmlResponse, Response
from scrapy.selector import SelectorList

from GiftInfo import CHECK_ROOMS
from GiftInfo.items import GiftInfoItem
from common.base_playwright import BasePlayWrightSpider
from common.defines import IS_DEBUG_MODE
from common.js_helper import JS_MUTE
from common.utils import get_rooms

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
    room_ids = CHECK_ROOMS if not IS_DEBUG_MODE else ([] + get_rooms())

    CONCURRENT_REQUESTS = len(room_ids)
    _REUSE_PAGE = True

    _sep = asyncio.Semaphore(CONCURRENT_REQUESTS)

    # HEADLESS = False

    def start_requests(self):

        _LOGGER.info(f'需要检查的房间 {self.room_ids}')

        self.start_urls = [
            f'{self.start_urls[0]}{r}' for r in self.room_ids
        ]

        _LOGGER.info(f'will spider {self.start_urls}')

        # super().start_requests()

        for one in self.start_urls:
            yield self._request_url_as_playwright(one, callback=self.parse, )

    _already_find_msg_max_id = 0

    def _parse_msg(self,
                   url: str,
                   page_response_lastest: HtmlResponse,
                   ):
        chat_room_msgs: SelectorList = page_response_lastest.css('#chat-room__list')
        msg_divs: SelectorList = chat_room_msgs.css('div[data-cmid]')

        room_id = os.path.basename(url)

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

                    # yield GiftInfoItem(
                    #     user_name=user_name,
                    #     num=gift_num,
                    #     gift_name=span_gift_desc,
                    #     action="送",
                    #     room=url,
                    #     time=date_str,
                    # )
                    yield None

            elif send_msg := one.css(f'div.msg-normal > span.msg.J_msg'):
                msg_text = send_msg.css('::text').get()
                _LOGGER.info(f'{room_id} msg_text: {msg_text} ')
                if msg_text and "下单了" in msg_text:
                    msg_list = msg_text.split(' ')

                    user_name = msg_list[0]
                    up_name = msg_list[2]

                    gift_info = msg_list[4].split('×')
                    # print(gift_info)
                    # up_namespan_gift_desc = gift_info[0]
                    gift_name = gift_info[0]
                    gift_num = gift_info[1]

                    _LOGGER.info(f'{user_name} 下单 {gift_num} 个 {gift_info} 给 {up_name}')

                    # 暂时只看订单消息
                    yield GiftInfoItem(
                        user_name=user_name,
                        num=gift_num,
                        gift_name=gift_name,
                        up_name=up_name,
                        action="下单",
                        room=url,
                        time=date_str,
                    )

    async def _get_text(self, element: ElementHandle, css_selector: str):
        return await element.evaluate('''(element) => {
                                return element.innerText;
                            }''', css_selector)

    @staticmethod
    def get_time_seconds_by_str(time_str: str) -> int:
        """
            将 01:50 => 110 秒
        """
        if ":" in time_str:
            m, s, *_ = time_str.split(":")
            m: str
            s: str
            if m.isdigit() and s.isdigit():
                return int(m) * 60 + int(s)
        elif time_str.isdigit():
            return int(time_str)
        return 0

    # 记录最近一次的时间戳轮次
    #   与倒计时时间
    _last_round: str = None
    _last_time: int = None

    async def _parse_current_go_word(self,
                                     url: str,
                                     page_response_lastest: HtmlResponse,
                                     response: Response,
                                     ) -> Optional[str]:
        """ 解析 带你环游游戏,
            返回是否在轮次

            如果在轮次, 以时间命名轮次,
            如果不在轮次, 返回 None
        """
        room_ = os.path.basename(url)
        _LOGGER.info(f'{room_} 准备自动化打开带你环游窗口')
        page: Page = response.meta['playwright_page']

        # 判断一下是否打开 游戏窗口
        #   倒计时心形窗口
        #   倒计时元素
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
        # 服务器上带宽低, 等长点时间
        await page.wait_for_timeout(2 * 1000)
        text = ""

        idx_ = 0
        while 1:
            idx_ += 1
            # todo: 后续优化下判断, 不重复打开
            if (not go_word_wind_heart) and (not open_win):
                ...
                # 尝试将心动环游点出来
                # await page.hover('.more-activity-icon')
                # await page.wait_for_timeout(0.1 * 1000)
                # await page.click('.more-activity-icon')
                # 先移动到其他位置, 不然不一定会触发
                await self._move_mouse_to_css_center(response=response, css_selector='body')
                # 看看更多加载出来没有, 没有就刷新页面
                more_ac_btn = await page.query_selector('.more-activity-icon')
                if not more_ac_btn:
                    _LOGGER.info(f'{room_} 未检测到更多按钮, 刷新页面')
                    await self.reload(page=page)
                    await page.wait_for_timeout(idx_ * 5 * 1000)
                if await self._move_mouse_to_css_center(response=response, css_selector='.more-activity-icon'):
                    # await asyncio.sleep(60)
                    _LOGGER.info(f'{room_} 点击 带你环游')
                    await page.wait_for_timeout(1 * 1000)
                    await page.click(heart_btn_css)
                    await page.wait_for_timeout(0.5 * 1000)
                    # 可能会出现请求权限窗口, 检查一下然后允许
                    open_win = True

            if open_win:
                body_iframes: List[ElementHandle] = await page.query_selector_all('body iframe')

                # 找到目标frame
                target_iframe: ElementHandle = None
                # 还是得遍历找, 不然后面会返回代理界面
                # todo: 是不是要从后往前找
                for i, one in enumerate(body_iframes):
                    one_page_content = await one.content_frame()
                    if one_page_content.url == 'https://y2261a742d6a43b3-ojhmr5vg.ext.huya.com/ext-web-sub-frame/0.2.8/index.html':
                        target_iframe = one
                        _LOGGER.debug(f'{url} 在第 {i} 个 frame 找到目标 frame')
                        break

                # 一般在最后一个
                if target_iframe:
                    iframe_page_content = await target_iframe.content_frame()
                    t1 = await iframe_page_content.content()

                    # 可能会出现请求权限窗口, 检查一下然后允许
                    # t = await page.query_selector_all(per_sure_btn_css)
                    for find_ele in await page.query_selector_all(per_sure_btn_css):
                        # t = await find_ele.text_content()
                        if await find_ele.text_content() == '允许':
                            await find_ele.click()
                            await iframe_page_content.wait_for_timeout(0.5 * 1000)

                    # 心动环游在 这个 iframe 的 子 iframe
                    al_iframe = await iframe_page_content.query_selector_all('iframe')

                    for iframe_son_l1 in al_iframe:
                        iframe_son_l1_iframe = await iframe_son_l1.content_frame()
                        t2 = await iframe_son_l1_iframe.content()

                        # 优化一下直接找文本
                        # for find_ele in await iframe_son_l1_iframe.query_selector_all(heart_css):
                        #     go_word_wind_heart = find_ele
                        #     break
                        find_text_element = await iframe_son_l1_iframe.query_selector_all('.css-901oao')
                        for one in find_text_element[:3]:
                            if one:
                                text += (await one.text_content() or "").strip()

                        if text:
                            break

            if (not text):
                _LOGGER.info(f'{url} 未检测到心动环游窗口打开, 请先在任一页面登录, 3s 后将刷新页面重试... ')
                await page.wait_for_timeout(1 * 3 * 1000)
            else:
                break

        _LOGGER.info(f'{room_} 成功找到带你环游窗口倒计时消息 {text}')
        # text_div = await go_word_wind_heart.query_selector('.css-1dbjc4n.r-1awozwy')
        # css-1dbjc4n r-1awozwy
        # msg_1_div = await text_div.query_selector('.css-1dbjc4n.r-1awozwy')
        # text: str = await text_div.text_content()

        if text.endswith('后出发'):
            time_str = text.replace('后出发', '')
            time_int = self.get_time_seconds_by_str(time_str)

            if self._last_round is None:
                self._last_round = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self._last_time = time_int
            else:
                # 如果有轮次, 判断下是否是新的一轮
                if time_int <= self._last_time:
                    ...
                else:
                    # 新一轮
                    self._last_round = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self._last_time = time_int
                return self._last_round
        return None

    async def _wait_for_login_by_text(self,
                                      response: Response,
                                      user_selector: str = None,
                                      user_success_text: str = None):
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
            await self.reload(page=page)
            # 等半分钟, 因为人工登录的时候要一会儿
            await page.wait_for_timeout(1 * 30 * 1000)

        return False

    async def parse(self, response, **kwargs):

        # 并发支持
        async with self._sep:

            page: Page = response.meta['playwright_page']
            url = response.url

            # 如果找不到房间号
            if 'error?errorType=ROOM_NOT_FOUND' in url:
                _LOGGER.warning(f'找不到房间 {url}')
                await page.close()
                return

            _LOGGER.debug(f'等待页面 {url} 加载完成')
            await page.wait_for_load_state('domcontentloaded', timeout=0)
            _LOGGER.debug(f'页面 {url} 加载完成')

            while 1:

                # 把视频页面关掉, 看看能不能降低一点流量与占用
                await page.evaluate("document.querySelectorAll('#videoContainer > .player-wrap').forEach(e => e.remove())")

                # todo: 放到 docker 里了 暂时取消主动登录
                #   如果需要登陆, 改成手动登了, 提交代码上去
                # await self._wait_for_login_by_text(response=response,)

                page_response_lastest = await self.refresh_playwright_response(response, 1000)
                await page.wait_for_timeout(1000)  # 等待 1 秒，确保内容加载
                await self.exec_js(page=page, js_str=JS_MUTE)

                # 时间轮次
                current_time_round = await self._parse_current_go_word(url=url,
                                                                       page_response_lastest=page_response_lastest,
                                                                       response=response)

                for msg_ret in self._parse_msg(url=url, page_response_lastest=page_response_lastest):
                    msg_ret: Optional[GiftInfoItem]
                    if msg_ret:
                        msg_ret['time_round'] = current_time_round
                        yield msg_ret

                # 一分钟刷新一次, 如果消息多, 需要更短间隔时间
                # await asyncio.sleep(1*60)
                # 提高准确性, 半秒钟刷新一次
                await page.wait_for_timeout(0.5 * 1 * 1000)
