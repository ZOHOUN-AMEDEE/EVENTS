from scrapy import Spider
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
import uuid  

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
            event_id = str(uuid.uuid4())  
            titre = event.css('h3.event-title::text').get()
            date_affichée = event.css('.description p span::text').get()
            date_debut = event.css('meta[itemprop="startDate"]::attr(content)').get()
            date_fin = event.css('meta[itemprop="endDate"]::attr(content)').get()
            description = event.css('meta[itemprop="description"]::attr(content)').get()
            lieu = event.css('span[itemprop="address"]::text').get()
            image_url = event.css('meta[itemprop="thumbnailUrl"]::attr(content)').get()
            event_link = event.css('a[itemprop="url"]::attr(href)').get()

            if event_link:
                meta = {
                    
                    'titre': titre,
                    'date_affichée': date_affichée,
                    'date_debut': date_debut,
                    'date_fin': date_fin,
                    'description': description,
                    'lieu': lieu,
                    'image_url': image_url,
                    'event_link': event_link,
                }
                yield response.follow(event_link, callback=self.parse_event_details, meta=meta)

    def parse_event_details(self, response):
        meta_data = response.meta

        
        categorie = response.css(
            'ol.flex-center li.breadcrumb-item:nth-child(3) span[itemprop="name"]::text'
        ).get()
        meta_data['categorie'] = categorie  
        tariffs_url = self.extract_tariffs_url(response.url)
        if tariffs_url:
            yield response.follow(tariffs_url, callback=self.parse_tariffs, meta=meta_data)
        else:
            
            yield {
                'event_id': meta_data['event_id'],
                'prix': None,
                'titre': meta_data['titre'],
                'date_affichée': meta_data['date_affichée'],
                'date_debut': meta_data['date_debut'],
                'date_fin': meta_data['date_fin'],
                'description': meta_data['description'],
                'lieu': meta_data['lieu'],
                'image_url': meta_data['image_url'],
                'event_link': meta_data['event_link'],
                'categorie': meta_data['categorie'],
            }

    def extract_tariffs_url(self, event_url):
        self.driver.get(event_url)
        time.sleep(3)  
        logs = self.driver.get_log("performance")

        for log_entry in logs:
            try:
                log = json.loads(log_entry["message"])["message"]
                if log.get("method") == "Network.requestWillBeSent":
                    request = log.get("params", {}).get("request", {})
                    url = request.get("url", "")
                    if "tariffs" in url:
                        self.logger.info(f"Tariffs URL found: {url}")
                        return url
            except Exception as e:
                self.logger.error(f"Error parsing log entry: {e}")
        return None

    def parse_tariffs(self, response):
        meta_data = response.meta

        json_text = response.css("pre::text").get()
        if json_text:
            data = json.loads(json_text)
            tariffs = data.get("tariffs", [])
            prices = [sub_tariff.get("price") for tariff in tariffs for sub_tariff in tariff.get("tariffs", [])]

            
            yield {
                
                'prix': prices,
                'categorie': meta_data.get('categorie'),
                'titre': meta_data['titre'],
                'date_affichée': meta_data['date_affichée'],
                'date_debut': meta_data['date_debut'],
                'date_fin': meta_data['date_fin'],
                'description': meta_data['description'],
                'lieu': meta_data['lieu'],
                'image_url': meta_data['image_url'],
                'event_link': meta_data['event_link'],
               
            }
