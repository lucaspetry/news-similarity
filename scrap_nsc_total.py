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
    debug = True

    def __init__(self):
        self.conn = psycopg2.connect("dbname='" + self.dbname +
                        "' user='" + self.dbuser +
                        "' host='" + self.dbhost +
                        "' password='" + self.dbpass + "'")

    def parse(self, response):
        if debug:
            print("----- BEGIN PARSING -----")
        i = 0
        for title in response.xpath("//*[contains(@class, 'iJUApm')]//li"):
            next_link = title.xpath('a/@href').extract()
            print(next_link)
            if i > 0:
                yield Request(next_link[0], callback=self.parse_topics)
                if debug:
                    return # return statement meant for debugging
            i += 1

    def parse_topics(self,response): # Here we should first click on "Exibir Mais" a bunch of times
        if debug:
            print("----- ENTERING SUFFIX PAGE -----")
        news_suffix = response.css('h1::text').extract_first()
        for news in response.css('div .kACXYv article'):
            news_link = news.xpath('a/@href').extract_first()
            request = Request(news_link, callback=self.parse_news)
            request.meta['topic'] = news_suffix
            yield request
            if debug:
                return #return statement meant for debugging

    def parse_news(self, response): # WE HAVE TO CHECK DIFFERENT KINDS OF PAGES: WHEN REFERING TO DIARIO CATARINENSE, <p>'s have no class and are inside the entry-content <div> instead!!
        text_re = re.compile(r"<[^>]+>") # Regex to eliminate HTML tags
        if debug:
            print("----- ENTERING NEWS PAGE -----")

        def extract_date():
            date_re = re.compile(r"(Atualizada em: [0-9/]+ [0-9:]+)") # Regex to parse DateTime
            date_time = response.css('div .DateInfo ::text').extract_first().replace("min", '').replace("h", ':').replace("- ", '')
            date_time = date_re.sub("", date_time)
            date_time = datetime.strptime(date_time, '%d/%m/%Y %H:%M')
            return date_time

        def extract_sub_and_title():
            title = response.css('h1::text').extract_first() # Extract title from Header h1
            subtitle = "" # This website contains no subtitles
            return {title, subtitle}

        def extract_text():
            if debug:
            get_full_text = response.xpath("//*[contains(@class, 'StyledParagraph')]").extract() # Takes the HTML of the <p> element of class StyledParagraph. This is the class of all paragraphs in news article inside the HTML page.
            if debug:
                print(get_full_text)
            text = "" # Create the base appendable text
            for p in get_full_text:
                text_part = text_re.sub(p, "") # Eliminate all HTML tags from text
                if debug:
                    print(text_part)
                text += text_part
                text += " "
            if debug:
                print("--- FINAL NEWS TEXT EXTRACTED ---")
                print(text) # Show final text
            return text

        def extract_subject():
            return "Assunto"

        def extract_author():
            author_re = re.compile("Por") # Test if it eliminates names like 'Portugal' please
            author_full = response.xpath("//div[contains(@class, 'Author')]")
            if debug:
                print("Full author text: " + author_full)
            author = author_re.sub(author_full, "") # Eliminate 'Por' authorship declaration
            return author

        def commit_to_db():
            return "Nada"

        {title, subtitle} = extract_sub_and_title()
        author = extract_author()
        subject = extract_subject()
        text = extract_text()
        commit_to_db()
