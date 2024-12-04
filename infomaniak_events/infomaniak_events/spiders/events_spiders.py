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

        
        try:
            voir_tout_buttons = self.driver.find_elements(By.CSS_SELECTOR, '.title-section a.more')
            for button in voir_tout_buttons:
                button.click()
                time.sleep(4)  
        except Exception as e:
            self.logger.error(f"Erreur lors du clic sur 'see all': {e}")

       
        html = self.driver.page_source
        response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

        # Extraire les événements
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

            # Suivre le lien pour les détails supplémentaires
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

        price_text = response.css('td.availability p.price::text').get() or response.css('div.tariff-container p.text-right::text').get()
        prix = price_text.strip() if price_text != "N/A" else "N/A"

        
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
