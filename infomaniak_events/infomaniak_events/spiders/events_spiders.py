from scrapy import Spider, signals
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
            self.logger.error(f"Erreur lors du clic sur 'see all' : {e}")

        
        html = self.driver.page_source
        response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

        # Extraire les événements
        events = response.css('.event-card')
        for event in events:
            yield {
                'titre': event.css('h3.event-title::text').get(),
                'date_affichée': event.css('.description p span::text').get(),
                'date_debut': event.css('meta[itemprop="startDate"]::attr(content)').get(),
                'date_fin': event.css('meta[itemprop="endDate"]::attr(content)').get(),
                'description': event.css('meta[itemprop="description"]::attr(content)').get(),
                'lieu': event.css('span[itemprop="address"]::text').get(),
                'image_url': event.css('meta[itemprop="thumbnailUrl"]::attr(content)').get(),
                'event_link': event.css('a[itemprop="url"]::attr(href)').get(),
               
            }

    def closed(self, reason):
        self.driver.quit()
