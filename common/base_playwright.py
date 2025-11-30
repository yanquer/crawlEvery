import abc
import logging
import os
from typing import Iterable

import scrapy
from scrapy import Request
from scrapy.http import Response

from .defines import CUSTOM_LOG
from .logger_ import LoggerEvery

_LOGGER = logging.getLogger(__name__)
LoggerEvery.add_rotating_log_handler(_LOGGER, CUSTOM_LOG, logging.DEBUG)


####
### base
####


class BasePlayWrightSpider(scrapy.Spider, abc.ABC):

    SAVE_DIR = "resources/gift"
    # 并发数
    CONCURRENT_REQUESTS = 25
    HEADLESS = False
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
            },
            PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT=playwright_default_navigation_timeout,

            ITEM_PIPELINES={
                'GiftInfo.pipelines.JsonWriterPipeline': 3,
                # 'GiftInfo.pipelines.ImageSavePipeline': None,
            },

            # page对象复用, 多page必须多线程
            CONCURRENT_REQUESTS=concurrent_requests,  # 增加并发数

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

