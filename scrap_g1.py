'''
Created on 22, Oct, 2018

@authors: Camila Leite, Vinicius Freitas, Lucas May
'''
import scrapy
import psycopg2
from scrapy.http import Request
from datetime import datetime
import re

class GloboSpider(scrapy.Spider):

    dbname = "news_articles"
    dbhost = "localhost"
    dbuser = "postgres"
    dbpass = "postgres"
    debug = True

    name = 'globo'

    start_urls = ['https://g1.globo.com/sc/santa-catarina']

    url_base = "https://g1.globo.com/sc/santa-catarina"

    def __init__(self):
        self.conn = psycopg2.connect("dbname='" + self.dbname +
                        "' user='" + self.dbuser +
                        "' host='" + self.dbhost +
                        "' password='" + self.dbpass + "'")

    def parse(self, response):
        for title in response.css('.feed-post-body a'):
            next_link = title.xpath('@href').extract_first()
            yield Request(next_link, callback=self.parse_news)

    def parse_news(self, response):

        debug = True
        text_re = re.compile(r"<[^>]+>") # Regex to eliminate HTML tags
        if debug:
            print("----- ENTERING NEWS PAGE -----")

        def extract_date():
            date_time = response.css('time::text').extract_first().replace("h", ':')
            date_time = date_time[1:-1]
            if debug:
                print(date_time)
            date_time = datetime.strptime(date_time, '%d/%m/%Y %H:%M')
            return date_time

        def extract_sub_and_title():
            title = response.xpath("//*[contains(@class, 'content-head__title')]").extract_first()
            title = text_re.sub("", title)
            subtitle = response.css('h2::text').extract_first() # This website contains no subtitles
            if debug:
                print(title)
                print(subtitle)
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

        date = extract_date()
        title, subtitle = extract_sub_and_title();
        print("Fechou")
