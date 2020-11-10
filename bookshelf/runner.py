from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from bookshelf import settings
from bookshelf.spiders.book24 import BookSpider
from bookshelf.spiders.labyrinth import LabyrinthSpider

if __name__ =='__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings = crawler_settings)
    process.crawl(BookSpider)
    process.crawl(LabyrinthSpider)

    process.start()