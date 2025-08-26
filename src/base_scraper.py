from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from undetected_chromedriver import Chrome, ChromeOptions
import time
import random
import yaml
import logging
from typing import Optional, List, Dict, Any
from fake_useragent import UserAgent
from .product_schema import ProductData, ScrapedResult, StockStatus

class BaseScraper(ABC):
    def __init__(self, headless: bool = True, timeout: int = 30):
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.logger = logging.getLogger(__name__)
        self.ua = UserAgent()
        self.selectors = self.load_selectors()
        
    def load_selectors(self) -> Dict[str, Any]:
        try:
            with open('config/selectors.yaml', 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning("Selectors config file not found")
            return {}
    
    def setup_driver(self):
        options = ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'--user-agent={self.ua.random}')
        
        self.driver = Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def get_random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0) -> float:
        return random.uniform(min_delay, max_delay)
    
    def scroll_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(self.get_random_delay(0.5, 1.5))
    
    def human_like_scroll(self):
        scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_increment = random.randint(200, 500)
        
        for i in range(0, scroll_height, scroll_increment):
            self.driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(random.uniform(0.1, 0.3))
    
    def find_element_safe(self, by, value, timeout: Optional[float] = None):
        try:
            timeout = timeout or self.timeout
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            return None
    
    def find_elements_safe(self, by, value, timeout: Optional[float] = None):
        try:
            timeout = timeout or self.timeout
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return self.driver.find_elements(by, value)
        except TimeoutException:
            return []
    
    def extract_text(self, element) -> Optional[str]:
        if element:
            return element.text.strip()
        return None
    
    def extract_price(self, text: str) -> Optional[str]:
        if text:
            # Remove non-numeric characters except decimal point and currency symbols
            import re
            cleaned = re.sub(r'[^\d.,$€£¥₦]', '', text)
            return cleaned
        return None
    
    @abstractmethod
    def scrape_product(self, url: str) -> ScrapedResult:
        pass
    
    @abstractmethod
    def simulate_checkout(self, product_data: ProductData, quantity: int = 1) -> Dict[str, Any]:
        pass
    
    def close(self):
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()