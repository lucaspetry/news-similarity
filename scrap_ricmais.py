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
    name = 'RIC MAIS'
    start_urls = []
    url_base = 'https://ricmais.com.br'
    debug = True

    def __init__(self):
        self.conn = psycopg2.connect("dbname='" + self.dbname +
                                     "' user='" + self.dbuser +
                                     "' host='" + self.dbhost +
                                     "' password='" + self.dbpass + "'")

        for page in range(1, 10):
            self.start_urls.append('https://ricmais.com.br/sc/noticias/pagina/' + str(page))

    def parse(self, response):
        for news in response.css('.categoria .row h2'):
            news_link = self.url_base + news.xpath('a/@href').extract_first()
            yield Request(news_link, callback=self.parse_news)

    def parse_news(self, response):
        tag_re = re.compile(r"<[^>]+>")  # Regex to eliminate HTML tags

        def extract_date():
            date_time = response.css('.topo-materia .news-details-head-metadata::text').extract_first()
            date_time = date_time.replace('h', ':')
            date_time = datetime.strptime(date_time, '%d/%m/%Y | %H:%M - ')
            return date_time

        subject = response.css('.topo-materia .news-details-head-metadata a::text').extract_first()
        title = response.css('.topo-materia h2::text').extract_first()
        subtitle = ''
        date_time = extract_date()
        author = ''
        text = response.css('.news-text').extract_first().replace("'", "")
        text = tag_re.sub("", text)
        tags = str(response.css('.news-details-metadata .tags a::text').extract())
        link = response.url
        portal = 'RIC MAIS'

        cur = self.conn.cursor()

        cur.execute("select count(*) from news where title = $tag$" + title + "$tag$ AND subtitle = $tag$" + subtitle + "$tag$ AND portal = $tag$" + portal + "$tag$")
        if cur.fetchall()[0][0] > 0:
            return

        query = "insert into news (title, subtitle, date_time, text, authors, portal, tags, subject, link) " + \
                "values ($tag$" + title + "$tag$, $tag$" + subtitle + "$tag$, $tag$" + str(date_time) + "$tag$, $tag$" + text + "$tag$, $tag$" + author + "$tag$, $tag$" + \
                portal + "$tag$, $tag$" + str(tags).replace("'", '') + "$tag$, $tag$" + subject + "$tag$, $tag$" + link + "$tag$)"

        try:
            cur.execute(query)
            self.conn.commit()
        except Exception as e:
            print("\n\n\nQuery Error: " + str(e) + "\n\n\n\n")
            self.conn.rollback()
