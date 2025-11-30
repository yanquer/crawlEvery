import logging
import os.path

from scrapy.utils.project import get_project_settings

from GiftInfo.spiders.huya import HuyaSpider


def run_with_crawl():
    from scrapy.crawler import CrawlerProcess

    def run():
        settings = get_project_settings()
        # settings["FEEDS"] = {
        #     'data/%(name)s_%(time)s.json': {
        #         'format': 'json',
        #         'encoding': 'utf8',
        #         'indent': 2,
        #         'store_empty': False,
        #         'overwrite': True
        #     },
        # }
        process = CrawlerProcess(settings)
        process.crawl(HuyaSpider)
        process.start()

    run()


def run_with_reactor():
    from scrapy.crawler import CrawlerRunner
    from scrapy.utils.log import configure_logging

    from scrapy.utils.reactor import install_reactor

    install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")

    from twisted.internet import reactor

    def run():

        settings = get_project_settings()

        # 直接运行控制台没有日志
        configure_logging(
            {
                'LOG_FORMAT': '%(message)s'
            }
        )

        runner = CrawlerRunner(
            settings
            # settings={
            #     "ITEM_PIPELINES": {JsonWriterPipeline: 3}
            # }
        )

        d = runner.crawl(HuyaSpider)
        # 如果有多个
        #   runner.crawl(HuyaSpider)
        #   d = runner.join()
        #   这样是顺序启动的

        d.addBoth(lambda _: reactor.stop())

        reactor.run()

    run()


if __name__ == '__main__':

    print(f'Running in directory: {os.getcwd()}')
    os.makedirs("log", exist_ok=True)
    # logging.basicConfig(level=logging.DEBUG, filename="log/spider.log", format="%(asctime)s - %(levelname)s - %(message)s")
    logging.basicConfig(level=logging.INFO, filename="log/spider.log", format="%(asctime)s - %(levelname)s - %(message)s")

    # run_with_reactor()

    from scrapy.utils.reactor import install_reactor
    install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

    run_with_crawl()
