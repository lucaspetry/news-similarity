'''
Created on Oct 22, 2018

@authors: Vinicius Freitas
'''
import scrapy
import psycopg2
from scrapy.http import Request
from datetime import datetime
import re


class JORNAL_SC(scrapy.Spider):
    dbname = "news_articles"
    dbhost = "localhost"
    dbuser = "postgres"
    dbpass = "postgres"
    name = 'JORNAL DE SANTA CATARINA'
    start_urls = ['http://jornaldesantacatarina.clicrbs.com.br/sc/ultimas-noticias/']
    url_base = 'http://jornaldesantacatarina.clicrbs.com.br/sc/ultimas-noticias/'
    debug = True

    def __init__(self):
        print("init")
        self.conn = psycopg2.connect("dbname='" + self.dbname +
                                    "' user='" + self.dbuser +
                                    "' host='" + self.dbhost +
                                    "' password='" + self.dbpass + "'")

    def parse(self, response):
        pg = response.meta['page'] if 'page' in response.meta else 1
        if pg > 10:
            return
        news_list = response.xpath("//div[@class='conteudo-lista']")
        for news in news_list: # Iterate through each of the menus
            def parse_tags_and_date():
                sub_and_date_html = news.xpath("//p[@class='materia-cabecalho']")
                subject = sub_and_date_html.xpath("//span[contains(@class, 'editoria')]//text()").extract_first()
                date_txt = sub_and_date_html.xpath("//span[@class='data-publicacao']//text()").extract_first()
                tags = news.css("div .lista-tags").css("li").xpath("a/@title").extract()
                return (subject, date_txt, tags)

            (sub, date, tags) = parse_tags_and_date()
            date_time = datetime.strptime(date, "%d/%m/%Y | %Hh%M")
            title_link_html = news.css("h2")
            title = title_link_html.xpath("a/@title").extract_first()
            next_link = title_link_html.xpath("a/@href").extract_first()
            print("\n\n***\n\n")
            print(title)
            print(sub)
            print(date)
            print(next_link)
            print(tags)
            req = Request(next_link, callback=self.parse_news)
            req.meta['title'] = title
            req.meta['subject'] = sub
            req.meta['date'] = date_time
            req.meta['tags'] = tags
            yield req
            return
        next_page = self.url_base+"?pagina="+str(pg)
        print("Crawl to: "+next_page)
        req = Request(next_page, callback=self.parse)
        req.meta['page'] = pg+1
        yield req

    def parse_news(self, response):
        title = response.meta['title']
        subject = response.meta['subject']
        tags = response.meta['tags']
        date_time = response.meta['date']

        def parse_author():
            author = response.xpath("//div[@class='materia-assinatura']//text()").extract_first()
            return author

        def parse_text():
            text_body = response.xpath("//div[contains(@class, 'materia-corpo')]//p//text()").extract()
            text = ""
            for part in text_body:
                text += part + " "
            return text

        author = parse_author()
        text = parse_text()
        link = response.url
        
        query = "insert into news (title, subtitle, date_time, text, authors, portal, tags, subject, link) " + \
                "values ('" + title + "', '" + subtitle + "', '" + str(date_time) + "', '" + text + "', '" + author + "', '" + \
                portal + "', '" + str(tags).replace("'", '') + "', '" + subject + "', '" + link + "')"

        try:
            cur.execute(query)
            self.conn.commit()
        except Exception as e:
            print("\n\n\nQuery Error: " + str(e) + "\n\n\n\n")
            self.conn.rollback()
