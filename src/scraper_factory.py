from amazon_scraper import AmazonScraper
# from aliexpress_scraper import AliExpressScraper
# from ebay_scraper import EbayScraper
# from etsy_scraper import EtsyScraper
# from jumia_scraper import JumiaScraper
# from kilimall_scraper import KilimallScraper
# from jiji_scraper import JijiScraper
from base_scraper import BaseScraper
from typing import Optional
import re

class ScraperFactory:
    @staticmethod
    def create_scraper(url: str, headless: bool = True) -> Optional[BaseScraper]:
        """
        Factory method to create appropriate scraper based on URL
        """
        domain = ScraperFactory._extract_domain(url)
        
        scraper_map = {
            'amazon': AmazonScraper,
            # 'aliexpress': AliExpressScraper,
            # 'ebay': EbayScraper,
            # 'etsy': EtsyScraper,
            # 'jumia': JumiaScraper,
            # 'kilimall': KilimallScraper,
            # 'jiji': JijiScraper
        }
        
        for platform, scraper_class in scraper_map.items():
            if platform in domain:
                return scraper_class(headless=headless)
        
        return None
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL"""
        import re
        domain_pattern = r'https?://(?:www\.)?([^/]+)'
        match = re.search(domain_pattern, url)
        return match.group(1).lower() if match else ''