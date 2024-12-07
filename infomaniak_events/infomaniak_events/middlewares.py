from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

class SeleniumMiddleware:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

       
        self.service = Service('C:/Users/DAVIDO LAPTOP/Downloads/chromedriver-win32/chromedriver.exe')
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)

    def process_request(self, request, spider):
        self.driver.get(request.url)
        time.sleep(5)  
        body = self.driver.page_source

        
        request.meta["driver"] = self.driver

        return HtmlResponse(
            self.driver.current_url,
            body=body,
            encoding='utf-8',
            request=request
        )

    def __del__(self):
        self.driver.quit()
