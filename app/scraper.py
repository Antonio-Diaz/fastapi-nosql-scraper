import time
from dataclasses import dataclass
from typing import Optional
import logging
from slugify import slugify
from requests_html import HTML
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

@dataclass
class Scraper:
    url: str
    endless_scroll: bool = False
    endless_scroll_time: int = 5
    html_obj: HTML = None
    _driver: Optional[WebDriver] = None
    CHROME_BINARY_LOCATION = '/usr/share/man/man1/google-chrome.1.gz'
    CHROME_OPTIONS = ["--no-sandbox", "--headless"]

    @staticmethod
    def _initialize_driver():
        if Scraper._driver is None:
            try:
                user_agent = UserAgent().random
                options = Options()
                options.add_argument(f"user-agent={user_agent}")
                options.binary_location = Scraper.CHROME_BINARY_LOCATION
                for opt in Scraper.CHROME_OPTIONS:
                    options.add_argument(opt)
                Scraper._driver = webdriver.Chrome(options=options)
            except Exception as e:
                logging.error(f"An exception occurred while initializing the WebDriver: {e}")

    @staticmethod
    def get_driver():
        Scraper._initialize_driver()
        return Scraper._driver

    @staticmethod
    def close_driver():
        if Scraper._driver is not None:
            Scraper._driver.quit()
            Scraper._driver = None
   
   
    def perform_scroll(self, driver):
        current_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(self.endless_scroll_time)
            iter_height = driver.execute_script("return document.body.scrollHeight")
            if current_height == iter_height:
                break
            current_height = iter_height
        return
   
    def get(self):
        driver = self.get_driver()
        driver.get(self.url)
        if self.endless_scroll:
            self.perform_scroll(driver=driver)
        else:
            time.sleep(10)
        return driver.page_source
    
    
    def get_html_obj(self):
        try:
            if self.html_obj is None:
                html_str = self.get()
                self.html_obj = HTML(html=html_str)
            return self.html_obj
        except Exception as e:
            logging.error(f"An exception occurred while getting HTML object: {e}")
            return None

    
    def extract_element_text(self, element_id):
        html_obj = self.get_html_obj()
        el = html_obj.find(element_id, first=True)
        if not el:
            return ''
        return el.text
        
    def extract_tables(self):
        html_obj = self.get_html_obj()
        return html_obj.find("table")
    
    def extarct_tables_dataset(self, tables):
        dataset = {}
        for table in tables:
            for tbody in table.element.getchildren():
                for tr in tbody.getchildren():
                    row = []
                    for col in tr.getchildren():
                        try:
                            content = col.text_content()
                        except:
                            pass
                        if content != "":
                            _content = content.strip()
                            row.append(_content)
                    if len(row) != 2:
                        continue
                    key = row[0]
                    value = row[1]
                    key = slugify(key)
                    if key in dataset:
                        continue
                    else:
                        dataset[key] = value
        return dataset
    
    def scrape(self):
        price_str = self.extract_element_text(element_id='.a-offscreen')
        title_str = self.extract_element_text(element_id='#productTitle')
        tables = self.extract_tables()
        dataset = self.extarct_tables_dataset(tables)
        return {
            'price_str': price_str,
            'title_str': title_str,
            **dataset
        }
