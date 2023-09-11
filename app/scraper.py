from typing import Optional

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

def get_user_agent():
    try:
        return UserAgent(verify_ssl=False).random
    except Exception as e:
        # Log the error or return a default user-agent
        return "Mozilla/5.0"

class Scraper:
    driver: Optional[WebDriver] = None
    
    @classmethod
    def _initialize_driver(cls):
        try:
            if cls.driver is None:
                user_agent = get_user_agent()
                options = Options()
                options.add_argument("--no-sandbox")
                options.add_argument("--headless")
                options.add_argument(f"user-agent={user_agent}")
                options.binary_location = '/usr/bin/google-chrome'
                cls.driver = webdriver.Chrome(options=options)
        except Exception as e:
            # Replace with logging in a real-world application
            print(f"An exception occurred while initializing the WebDriver: {e}")

    
    @classmethod
    def get_driver(cls):
        cls._initialize_driver()
        return cls.driver

    @classmethod
    def close_driver(cls):
        if cls.driver is not None:
            cls.driver.quit()
            cls.driver = None
   