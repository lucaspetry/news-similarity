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
    debug = False

    name = 'globo'

    start_urls = ['https://g1.globo.com/sc/santa-catarina']
    stop = False

    def __init__(self):
        self.conn = psycopg2.connect("dbname='" + self.dbname +
                        "' user='" + self.dbuser +
                        "' host='" + self.dbhost +
                        "' password='" + self.dbpass + "'")

    def parse(self, response):
        if self.stop:
            return
        
        url_base = "https://g1.globo.com/sc/santa-catarina"
        pg = response.meta['page'] if 'page' in response.meta else 1
        if pg > 300:
            return
        for title in response.css('.feed-post-body a'):
            next_link = title.xpath('@href').extract_first()
            if not next_link:
                continue
            yield Request(next_link, callback=self.parse_news)
        next_link = url_base+"/index/feed/pagina-" + str(pg) + ".ghtml"
        req = Request(next_link, callback=self.parse)
        req.meta['page'] = pg+1
        yield req

    def parse_news(self, response):
        if self.stop:
            return

        debug = False
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
            get_full_text = response.xpath("//*[contains(@class, 'content-text__container')]").extract() # Takes the HTML of the <p> element of class StyledParagraph. This is the class of all paragraphs in news article inside the HTML page.
            text = "" # Create the base appendable text
            for p in get_full_text:
                text_part = text_re.sub("", p) # Eliminate all HTML tags from text
                text += text_part + " "
            if debug:
                print("--- FINAL NEWS TEXT EXTRACTED ---")
                print(text) # Show final text
            return text

        def extract_tags():
            get_full_tags = response.xpath("//*[@class='entities__list']")
            get_full_tags = get_full_tags.css('a ::text').extract()
            tags = str(get_full_tags).replace("'", "")
            if debug:
                print(tags)
            return tags

        def extract_subject():
            return "Santa Catarina"

        #G1 HAS NO AUTHORSHIP
        def extract_author():
            return ""

        def commit_to_db(date, title, subtitle, text, tag, subject, author, link, portal):
            cur = self.conn.cursor()
            cur.execute("select count(*) from news where title = $title$" + title + "$title$ AND subtitle = $subtitle$" + subtitle + "$subtitle$ AND portal = $portal$" + portal + "$portal$")

            if cur.fetchall()[0][0] > 0:
                return

            query = "insert into news (title, subtitle, date_time, text, authors, portal, tags, subject, link) " + \
                "values ($title$" + title + "$title$, $subtitle$" + subtitle + "$subtitle$, $date$" + str(date) + "$date$, $text$" + text + "$text$, $author$" + author + "$author$, $portal$" + \
                portal + "$portal$, $tag$" + tag + "$tag$, $subject$" + subject + "$subject$, $link$" + link + "$link$)" 

            try:
                cur.execute(query)
                self.conn.commit()
            except Exception as e:
                print("\n\n\n\n\n\n\n\n\nQuery Error: " + str(e) + "\n\n\n\n\n\n\n\n\n\n")
                self.conn.rollback()
                self.stop = True

        date = extract_date()
        title, subtitle = extract_sub_and_title()
        text = extract_text()
        tag = extract_tags()
        subject = extract_subject()
        author = extract_author()
        link = response.url
        portal = "Globo G1"
        commit_to_db(date, title, subtitle, text, tag, subject, author, link, portal)