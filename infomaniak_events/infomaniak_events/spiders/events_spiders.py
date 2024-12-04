from scrapy import Spider
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


class DynamicEventsSpider(Spider):
    name = "events"
    start_urls = ["https://infomaniak.events/en-ch"]

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        self.driver = webdriver.Chrome(options=chrome_options)

    def parse(self, response):
        self.driver.get(response.url)
        html = self.driver.page_source
        response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

        categories = response.css('div.categories h4.category a::attr(href)').getall()
        for category_link in categories:
            yield response.follow(category_link, callback=self.parse_category)

    def parse_category(self, response):
        self.driver.get(response.url)
        html = self.driver.page_source
        response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

        events = response.css('.event-card')
        for event in events:
            titre = event.css('h3.event-title::text').get()
            date_affichée = event.css('.description p span::text').get()
            date_debut = event.css('meta[itemprop="startDate"]::attr(content)').get()
            date_fin = event.css('meta[itemprop="endDate"]::attr(content)').get()
            description = event.css('meta[itemprop="description"]::attr(content)').get()
            lieu = event.css('span[itemprop="address"]::text').get()
            image_url = event.css('meta[itemprop="thumbnailUrl"]::attr(content)').get()
            event_link = event.css('a[itemprop="url"]::attr(href)').get()

            if event_link:
                yield response.follow(event_link, callback=self.parse_event_details, meta={
                    'titre': titre,
                    'date_affichée': date_affichée,
                    'date_debut': date_debut,
                    'date_fin': date_fin,
                    'description': description,
                    'lieu': lieu,
                    'image_url': image_url,
                    'event_link': event_link,
                })

    def parse_event_details(self, response):
        meta_data = response.meta

        categorie = response.css('ol.flex-center li.breadcrumb-item:nth-child(3) span[itemprop="name"]::text').get()

        elements = response.css("div.text-2.tariff-container p::text, div.text-2.tariff-container span::text, div p::text, div span::text").getall()
        prix = next((p.strip() for p in elements if 'CHF' in p), None)

        yield {
            'titre': meta_data['titre'],
            'date_affichée': meta_data['date_affichée'],
            'date_debut': meta_data['date_debut'],
            'date_fin': meta_data['date_fin'],
            'description': meta_data['description'],
            'lieu': meta_data['lieu'],
            'image_url': meta_data['image_url'],
            'event_link': meta_data['event_link'],
            'categorie': categorie,
            'prix': prix,
        }

    def closed(self, reason):
        self.driver.quit()
