'''
Created on Oct 17, 2018

@authors: Camila Leite, Vinicius Freitas
'''
import scrapy
import psycopg2
from scrapy.http import Request
from datetime import datetime
import re

class NSCTotal(scrapy.Spider):

    dbname = "news_articles"
    dbhost = "localhost"
    dbuser = "postgres"
    dbpass = "postgres"

    name = 'nsctotal'

    start_urls = ['https://www.nsctotal.com.br/florianopolis']

    url_base = "https://www.nsctotal.com.br"

    def __init__(self):
        self.conn = psycopg2.connect("dbname='" + self.dbname +
                        "' user='" + self.dbuser +
                        "' host='" + self.dbhost +
                        "' password='" + self.dbpass + "'")

    def parse(self, response):
        i = 0
        for title in response.xpath("//*[contains(@class, 'iJUApm')]//li"):
            next_link = title.xpath('a/@href').extract()
            if i > 0:
                yield Request(next_link[0], callback=self.parse_topics)
                return
            i += 1

    def parse_topics(self,response):
        news_suffix = response.css('h1::text').extract_first()
        for news in response.css('div .kACXYv article'):
            news_link = news.xpath('a/@href').extract_first()
            request = Request(news_link, callback=self.parse_news)
            request.meta['topic'] = news_suffix
            yield request
            return

    def parse_news(self, response):
        text_re = re.compile(r"<[^>]+>")
        date_re = re.compile(r"(Atualizada em: [0-9/]+ [0-9:]+)")
        title = response.css('h1::text').extract_first()
        subtitle = ""
        
        date_time = response.css('div .DateInfo ::text').extract_first().replace("min", '').replace("h", ':').replace("- ", '')
        date_time = date_re.sub("", date_time)
        date_time = datetime.strptime(date_time, '%d/%m/%Y %H:%M')

        get_full_text = response.xpath("//*[contains(@class, 'StyledParagraph')]").extract()
        print(get_full_text)
        text = ""
        for p in get_full_text:
            print(p)


