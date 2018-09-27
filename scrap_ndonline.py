import scrapy
import psycopg2
from scrapy.http import Request

class NdOnlineSpider(scrapy.Spider):
    name = 'ndonline'

    start_urls = ['https://ndonline.com.br/florianopolis/noticias']

    url_base = "https://ndonline.com.br"

    def parse(self, response):

        for title in response.css('.side-noticias li'):
            next_link = self.url_base + title.xpath('a/@href').extract_first()

            for page in range(2, 3):
                yield Request(next_link + "?p=" + str(page), callback=self.parse_topics)

    def parse_topics(self,response):
    
        for news in response.css('.secoes-noticias .row'):
            topic = news.css('h3::text').extract_first()
            news_suffix = news.xpath('div/h4/a/@href').extract_first()

            if not news_suffix:
                continue

            news_link = self.url_base + news_suffix
            request = Request(news_link, callback=self.parse_news)
            request.meta['topic'] = topic
            yield request

    def parse_news(self,response):

        title = response.css('.materia-header h1::text').extract()[0]
        subtitle = response.css('.materia-header p::text').extract()[0]
        date_time = response.css('.materia-header .materia-autor time::text').extract()[0]
        text = response.css('.materia-conteudo-container div div').extract()[0]
        author = ""
        portal = "NDONLINE"
        tags = response.css('.materia-conteudo-container .tags a::text').extract()
        subject = response.meta['topic']
