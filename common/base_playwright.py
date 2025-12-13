import abc
import json
import logging
import os
from typing import Iterable

import scrapy
from scrapy import Request
from scrapy.http import Response
from scrapy_playwright.page import PageMethod

from .defines import CUSTOM_LOG, IS_DEBUG_MODE
from .logger_ import LoggerEvery

_LOGGER = logging.getLogger(__name__)
LoggerEvery.add_rotating_log_handler(_LOGGER, CUSTOM_LOG, logging.DEBUG)


####
### base
####

class BasePlaywrightHelper(object):
    """ 主要定义一些辅助方法 """

    async def _move_mouse_to_css_center(self, response: Response, css_selector: str):
        """ 将鼠标移动要元素正中心

            css_selector:
                比如 .user-info
        """
        page = response.meta['playwright_page']

        # 1. 获取目标元素
        element = await page.query_selector(css_selector)

        if element:
            # 2. 获取元素的位置和尺寸
            bounding_box = await element.bounding_box()

            if bounding_box:
                # 3. 计算元素正中心坐标
                center_x = bounding_box['x'] + bounding_box['width'] / 2
                center_y = bounding_box['y'] + bounding_box['height'] / 2

                # 4. 先将鼠标移动到 (0, 0) 位置
                await page.mouse.move(0, 0)
                await page.wait_for_timeout(200)

                # 5. 从 (0, 0) 移动到元素中心
                await page.mouse.move(center_x, center_y)

                # 6. 等待并验证
                await page.wait_for_timeout(500)

                # 获取当前鼠标位置
                # current_pos = await page.mouse.position

                # 触发鼠标事件（可选）
                # await page.dispatch_event(css_selector, 'mouseover')
                # await page.dispatch_event(css_selector, 'mousemove')

                # yield {
                #     'element_found': True,
                #     'element_position': bounding_box,
                #     'calculated_center': {'x': center_x, 'y': center_y},
                #     'mouse_position_after': current_pos,
                #     'distance_from_center': {
                #         'x_diff': abs(current_pos['x'] - center_x),
                #         'y_diff': abs(current_pos['y'] - center_y)
                #     }
                # }
                await page.wait_for_timeout(100)
                return True
            else:
                # yield {'element_found': True, 'error': '无法获取元素位置信息'}
                return False
        else:
            # yield {'element_found': False, 'error': '元素未找到'}
            ...

        return False

    async def _wait_for_login_by_text(self, response: Response, user_selector: str, user_success_text: str=None):
        """ 等待页面登录完成

            通过用户元素的text文本判断, 比如用户名
            没有找到就刷新, 然后循环

            user_selector: 用户元素css选择器
            user_success_text: 登录成功后具有文本
                给定值时判断, 值是否是某个值
                None, 判断用户元素文本值非空
        """

    cache_dir = os.path.join('data', 'cookies',)
    cookies_file = os.path.join(cache_dir, 'user_cookies.json')
    context_file = os.path.join(cache_dir, 'user_context.json')
    os.makedirs(cache_dir, exist_ok=True)
    # context_file = 'user_context.dat'
    async def _save_user_cookies(self, response: Response,):
        os.makedirs(self.cache_dir, exist_ok=True)

        page = response.meta['playwright_page']

        # 保存 cookies
        cookies = await page.context.cookies()
        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f, indent=2)

        # 保存 storage state (包含 cookies, localStorage, sessionStorage)
        storage_state = await page.context.storage_state(path=self.context_file)

        _LOGGER.info(f"登录状态已保存到 {self.context_file}")
        return True

    async def _load_user_cookies(self, response: Response):
        os.makedirs(self.cache_dir, exist_ok=True)
        page = response.meta['playwright_page']

        # if os.path.exists(self.context_file):
        #     # 使用保存的状态
        #     yield scrapy.Request(
        #         url='https://example.com/dashboard',
        #         meta={
        #             'playwright': True,
        #             'playwright_include_page': True,
        #             'playwright_context_kwargs': {
        #                 'storage_state': self.context_file,  # 加载保存的状态
        #             },
        #         },
        #         callback=self.parse_logged_in
        #     )








class BasePlayWrightSpider(scrapy.Spider, BasePlaywrightHelper, abc.ABC):

    SAVE_DIR = "resources/gift"
    # 并发数
    CONCURRENT_REQUESTS = 25
    HEADLESS = not IS_DEBUG_MODE
    PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 10 * 60 * 1000,  # 10 min

    @staticmethod
    def get_scrapy_playwright_setting(
            save_dir=SAVE_DIR,
            headless=HEADLESS,
            concurrent_requests=CONCURRENT_REQUESTS,
            playwright_default_navigation_timeout=PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT,
    ):
        os.makedirs(save_dir, exist_ok=True)
        return dict(
            IMAGES_STORE=save_dir,
            ROBOTSTXT_OBEY=False,
            DOWNLOAD_HANDLERS={
                "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            },
            TWISTED_REACTOR="twisted.internet.asyncioreactor.AsyncioSelectorReactor",
            PLAYWRIGHT_LAUNCH_OPTIONS={
                "headless": headless,
                # "headless": False,
                "timeout": 3 * 60 * 1000,  # 3 min

                # Chrome/Chromium 静音参数
                # 'args': [
                #     '--mute-audio',
                # ],
            },
            PLAYWRIGHT_CONTEXT_KWARGS={
                'ignore_https_errors': True,
            },
            PLAYWRIGHT_PAGE_METHODS={
                # 静音
                PageMethod('wait_for_load_state', 'domcontentloaded'),
                PageMethod('evaluate', '() => { document.volume = 0; }'),
                # PageMethod('evaluate', """() => {
                #
                #     setTimeout(() => {
                #         document.querySelectorAll('video, audio').forEach(media => {
                #             # document.querySelectorAll('video, audio')[0].muted = true
                #             media.muted = true;
                #             media.volume = 0;
                #         })
                #     }, 5 * 1000)
                #
                #
                # }"""),

                # 为什么无效 ?
                PageMethod('evaluate', """() => {

                            setTimeout(() => {
                                console.log('静音...')
                                document.querySelectorAll('video, audio').forEach(videoEle => {
                                    // 静音
                                    //  muted 有时候会导致暂停, ?
                                    videoEle.muted = true
                                    videoEle.volume = 0
                                })

                            }, 10 * 1000)


                        }"""),
            },
            PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT=playwright_default_navigation_timeout,

            ITEM_PIPELINES={
                'GiftInfo.pipelines.JsonWriterPipeline': 3,
                'GiftInfo.pipelines.JsonWriterTimeRangePipeline': 4,
                # 'GiftInfo.pipelines.ImageSavePipeline': None,
            },

            # page对象复用, 多page必须多线程
            CONCURRENT_REQUESTS=concurrent_requests,  # 增加并发数

            # PLAYWRIGHT_BROWSER_TYPE="chromium",  # 指定使用 chromium
            # PLAYWRIGHT_BROWSER_TYPE="firefox",  # 指定使用 Firefox
            PLAYWRIGHT_BROWSER_TYPE="webkit",  # 指定使用 webkit
        )

    custom_settings = get_scrapy_playwright_setting()

    _spider_must_attr = ("name", "allowed_domains", "start_urls", "_REUSE_PAGE")

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for attr in cls._spider_must_attr:
            if attr not in cls.__dict__:
                raise TypeError(f"Class {cls.__name__} must define '{attr}'")

    # 是否复用 playwright 的页面, 注意遵循下面要求, 否则会卡死
    #   False 不复用
    #   True  全局复用一个, 仅适用 start_requests 返回一个 yield
    #   1     全局复用一个, 仅适用 start_requests 返回一个 yield
    #   2     全局复用多个, 需保证 start_requests 返回 yield 的数量比并发数 CONCURRENT_REQUESTS 小
    _REUSE_PAGE: bool = False

    def start_requests(self) -> Iterable[Request]:
        for one in self.start_urls:
            yield self._request_url_as_playwright(one, callback=self.parse,)

    async def error_handler(self, failure, from_where: int=1):
        from_where = "error_handler_from_start_requests"
        if from_where == 1:
            from_where = "error_handler_from_start_requests"
        else:
            from_where = "error_handler_from_parse"
            # _LOGGER.debug(f"{from_where}: is reuse {self._REUSE_PAGE}, close page...")
            page = failure.request.meta.get("playwright_page")
            if page:
                _LOGGER.debug(f"{from_where}: is reuse {self._REUSE_PAGE}, close page...")
                await page.close()

        _LOGGER.debug(f"{from_where}: {failure}...")
        page = failure.request.meta.get("playwright_page")
        if self._REUSE_PAGE is False:
            _LOGGER.debug(f"{from_where}: close page...")
            if page:
                await page.close()
        elif self._REUSE_PAGE in (True, 1):
            _LOGGER.debug(f"{from_where}: is reuse 1, ignore page...")
        elif self._REUSE_PAGE == 2:
            _LOGGER.debug(f"{from_where}: is reuse 2, ignore page...")
        else:
            msg = f"{from_where} - error _reuse_page val: {self._REUSE_PAGE}"
            _LOGGER.error(msg)
            raise RuntimeError(msg)

    async def error_handler_from_start_requests(self, failure):
        return await self.error_handler(failure, from_where=1)

    async def error_handler_from_parse(self, failure):
        return await self.error_handler(failure, from_where=2)

    async def handle_page_when_every_page_end(self, page, is_last_page=False, from_where=1):
        _LOGGER.debug(f"handle_page_when_every_page_end: page_id {id(page) if page else None}; is_last_page {is_last_page}")
        if is_last_page:
            if page:
                await page.close()
            return
        if self._REUSE_PAGE is False:
            _LOGGER.debug(f"handle_page_when_every_page_end-{from_where}: close page...")
            if page:
                await page.close()
        elif self._REUSE_PAGE in (True, 1):
            _LOGGER.debug(f"handle_page_when_every_page_end-{from_where}: is reuse 1, ignore page...")
        elif self._REUSE_PAGE == 2:
            _LOGGER.debug(f"handle_page_when_every_page_end-{from_where}: is reuse 2, ignore page...")
        else:
            msg = f"handle_page_when_every_page_end-{from_where} - error _reuse_page val: {self._REUSE_PAGE}"
            _LOGGER.error(msg)
            raise RuntimeError(msg)

    def _request_url_as_playwright(self, url, callback=None, current_page=None, ext_kwargs: dict=None, from_where=1):
        if from_where == 1:
            ...
        else:
            if not current_page:
                _LOGGER.warning(f"_request_url_as_playwright: current_page is {current_page} but from_where is {from_where}")

        callback_kwargs = ext_kwargs or {}
        callback_kwargs.update({
            'url': url,
        })
        return Request(
            url=url,
            callback=callback,
            meta={
                # 启用 Playwright
                'playwright': True,
                # 将页面对象传递给回调函数
                'playwright_include_page': True,
                "playwright_page": None if self._REUSE_PAGE == False else current_page,
                # "playwright_context": "new",  # 创建新的浏览器上下文
                "playwright_page_goto_kwargs": {
                    # 增加导航超时时间
                    "timeout": 60 * 60 * 1000,  # 30 min
                },
                'playwright_context_kwargs': {
                    # 加载保存的状态
                    'storage_state': self.context_file if os.path.exists(self.context_file) else None,
                },
            },
            cb_kwargs=callback_kwargs,
            errback=self.error_handler_from_start_requests if from_where==1 else self.error_handler_from_parse,
        )

    @abc.abstractmethod
    async def parse(self, response: Response, **kwargs):
        page = response.meta['playwright_page']

    @staticmethod
    async def refresh_playwright_response(response: Response, wait_ms: int = None):
        """
        刷新为 playwright 最新的内容
        :param response: Response
        :param wait_ms: 等待网页加载多长时间
        :return: Response
        """
        page = response.meta['playwright_page']
        if wait_ms:
            await page.wait_for_timeout(wait_ms)
        html = await page.content()
        response = scrapy.http.HtmlResponse(url=page.url, body=html.encode(), encoding='utf-8')
        return response



