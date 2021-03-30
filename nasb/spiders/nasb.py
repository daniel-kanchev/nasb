import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from nasb.items import Article


class nasbSpider(scrapy.Spider):
    name = 'nasb'
    start_urls = ['https://www.nasb.com/blog/']

    def parse(self, response):
        if response.url.endswith('blog'):
            featured = response.xpath('//a[@class="d-block d-md-flex w-100 no-arrow"]/@href').get()
            yield response.follow(featured, self.parse_article)

        links = response.xpath('//div[@class="col-12 col-md-4 my-4"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@id="Main_PageContent_C002_masterBlogPostsFrontend_ctl00_ctl00_pager_ctl00_ctl00_cmdNext"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//strong/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="sfpostDetails sfdetails"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
