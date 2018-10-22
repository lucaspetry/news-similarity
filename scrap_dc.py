'''
Created on Oct 22, 2018

@authors: Lucas May Petry
'''
import scrapy
import psycopg2
from scrapy.http import Request
from datetime import datetime
import re


class DC(scrapy.Spider):
    dbname = "news_articles"
    dbhost = "localhost"
    dbuser = "postgres"
    dbpass = "postgres"
    name = 'DIARIO CATARINENSE'
    start_urls = ['http://dc.clicrbs.com.br/sc/']
    url_base = 'http://dc.clicrbs.com.br/sc/'
    debug = True

    def __init__(self):
        self.conn = psycopg2.connect("dbname='" + self.dbname +
                                     "' user='" + self.dbuser +
                                     "' host='" + self.dbhost +
                                     "' password='" + self.dbpass + "'")

    def parse(self, response):
        for title in response.css('.nav-item-noticias .subnav .subnav-left ul li'):
            next_link = title.xpath('a/@href').extract_first()

            for page in range(1, 10):
                yield Request(next_link + "?pagina=" + str(page),
                              callback=self.parse_topics)

    def parse_topics(self, response):
        for news in response.css('.box-articles article h2'):
            news_link = news.xpath('a/@href').extract_first()
            yield Request(news_link, callback=self.parse_news)

    def parse_news(self, response):
        tag_re = re.compile(r"<[^>]+>")  # Regex to eliminate HTML tags

        def extract_date():
            date = response.css('.article-header .line-published-date-hour .published-date::text').extract_first()
            time = response.css('.article-header .line-published-date-hour .published-hour::text').extract_first()
            time = time.replace('h', ':').replace('min', '')
            date_time = datetime.strptime(date + ' ' + time, '%d/%m/%Y - %H:%M')
            return date_time

        subject = response.css('.article-header .cartola::text').extract_first()
        title = response.css('.article-header .article-title::text').extract_first().replace("'", "")
        subtitle = ''
        date_time = extract_date()
        author = response.css('.article-body .col-left .contributor a::text').extract_first()
        author = 'NULL' if not author else author
        text = response.css('.article-body .col-right div').extract_first().replace("'", "")
        text = tag_re.sub("", text)
        tags = str(response.css('.article-footer .list-tags li a::text').extract())
        link = response.url
        portal = 'DIARIO CATARINENSE'

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
        except Exception as e:
            print("\n\n\nQuery Error: " + str(e) + "\n\n\n\n")
            self.conn.rollback()
