import time
from dataclasses import dataclass
from typing import Optional
import logging

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

@dataclass
class Scraper:
    url: str
    endless_scroll: bool = False
    endless_scroll_time: int = 5
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
   
   
    def perform_scroll(self):
        if self.endless_scroll:
            current_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(self.endless_scroll_time)
                iter_height = self.driver.execute_script("return document.body.scrollHeight")
                if current_height == iter_height:
                    break
                current_height = iter_height
        return
   
    def get(self):
        driver = self.get_driver()
        driver.get(self.url)
        if self.endless_scroll:
            current_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(self.endless_scroll_time)
                iter_height = driver.execute_script("return document.body.scrollHeight")
                if current_height == iter_height:
                    break
                current_height = iter_height
        return driver.page_source