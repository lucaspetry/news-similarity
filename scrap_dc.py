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
    dbhost = "150.162.58.58"
    dbuser = "postgres"
    dbpass = "Trajetorias123"
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
        skip = ['Eleições 2018', 'Últimas']

        for title in response.css('.nav-item-noticias .subnav .subnav-left ul li'):
            next_link = title.xpath('a/@href').extract_first()
            subject = title.css("a::text").extract_first()

            if subject in skip:
                continue

            for page in range(1, 150):
                req = Request(next_link + "?pagina=" + str(page),
                              callback=self.parse_topics)
                req.meta['subject'] = subject
                yield req

    def parse_topics(self, response):
        for news in response.css('.box-articles article h2'):
            news_link = news.xpath('a/@href').extract_first()
            req = Request(news_link, callback=self.parse_news)
            req.meta['subject'] = response.meta['subject']
            yield req

    def parse_news(self, response):
        tag_re = re.compile(r"<[^>]+>")  # Regex to eliminate HTML tags

        def extract_date():
            date = response.css('.article-header .line-published-date-hour .published-date::text').extract_first()
            time = response.css('.article-header .line-published-date-hour .published-hour::text').extract_first()
            time = time.replace('h', ':').replace('min', '')
            date_time = datetime.strptime(date + ' ' + time, '%d/%m/%Y - %H:%M')
            return date_time

        subject = response.meta['subject']
        title = response.css('.article-header .article-title::text').extract_first().replace("'", "")
        subtitle = ''
        date_time = extract_date()
        author = response.css('.article-body .col-left .contributor a::text').extract_first()
        author = 'NULL' if not author else author
        text = response.css('.article-body .col-right .entry-content').extract_first().replace("'", "")
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
