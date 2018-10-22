'''
Created on Sep 26, 2018

@authors: Camila Leite, Lucas May
'''
import scrapy
import psycopg2
from scrapy.http import Request
from datetime import datetime
import re

class NdOnlineSpider(scrapy.Spider):

    dbname = "news_articles"
    dbhost = "localhost"
    dbuser = "postgres"
    dbpass = "postgres"

    name = 'ndonline'

    start_urls = ['https://ndonline.com.br/florianopolis/noticias']

    url_base = "https://ndonline.com.br"

    def __init__(self):
        self.conn = psycopg2.connect("dbname='" + self.dbname +
                        "' user='" + self.dbuser +
                        "' host='" + self.dbhost +
                        "' password='" + self.dbpass + "'")

    def parse(self, response):
        for title in response.css('.side-noticias li'):
            next_link = self.url_base + title.xpath('a/@href').extract_first()

            for page in range(2, 50):
                yield Request(next_link + "?p=" + str(page), callback=self.parse_topics)

    def parse_topics(self, response):
        for news in response.css('.secoes-noticias .row'):
            topic = news.css('h3::text').extract_first()
            news_suffix = news.xpath('div/h4/a/@href').extract_first()

            if not news_suffix:
                continue

            news_link = self.url_base + news_suffix
            request = Request(news_link, callback=self.parse_news)
            request.meta['topic'] = topic
            yield request

    def parse_news(self, response):
        
        tag_re = re.compile(r"<[^>]+>")

        title = response.css('.materia-header h1::text').extract()[0].replace("'", "")

        subtitle = response.css('.materia-header p::text').extract()[0].replace("'", "")

        date_time = response.css('.materia-header .materia-autor time::text').extract()[0].replace("h", ':')
        date_time = datetime.strptime(date_time, '%d/%m/%Y %H:%M')

        text = response.css('.materia-conteudo-container div div').extract()[0].replace("'", "")
        text = tag_re.sub("", text)

        author = ""

        portal = "NDONLINE"

        tags = response.css('.materia-conteudo-container .tags a::text').extract()

        subject = response.meta['topic']

        link = response.url

        cur = self.conn.cursor()
         
        cur.execute("select count(*) from news where title = '" + title + "' AND subtitle = '" + subtitle + "' AND portal = '" + portal + "'")
        if cur.fetchall()[0][0] > 0:
            return

        query = "insert into news (title, subtitle, date_time, text, authors, portal, tags, subject, link) " + \
                "values ('" + title + "', '" + subtitle + "', '" + str(date_time) + "', '" + text + "', '" + author + "', '" + \
                portal + "', '" + str(tags).replace("'", '') + "', '" + subject + "', '" + link + "')" 

        try:
            cur.execute(query)
            self.conn.commit()
        except e:
            print("\n\n\nQuery Error: " + str(e) + "\n\n\n\n")
            self.conn.rollback()

