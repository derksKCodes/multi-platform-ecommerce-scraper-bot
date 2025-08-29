#!/usr/bin/env python3
"""
Main orchestrator for multi-platform e-commerce scraper
"""

import argparse
import logging
from typing import List
from scraper_factory import ScraperFactory
from output_writer import OutputWriter
from utils import setup_logging, read_urls_from_file, retry_on_failure
from product_schema import ScrapedResult
import yaml
import time

class ECommerceScraper:
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self.load_config(config_path)
        self.output_writer = OutputWriter(
            json_path=self.config['output']['json_path'],
            csv_path=self.config['output']['csv_path'],
            excel_path=self.config['output']['excel_path']
        )
        setup_logging()
    
    def load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logging.warning("Config file not found, using defaults")
            return {
                'scraper': {'headless': True, 'timeout': 30},
                'output': {
                    'json_path': 'data/output.json',
                    'csv_path': 'data/output.csv',
                    'excel_path': 'data/output.xlsx',
                    'screenshots_dir': 'data/screenshots'
                }
            }
    
    @retry_on_failure(max_retries=3, delay=2.0)
    def scrape_url(self, url: str) -> ScrapedResult:
        """Scrape a single URL"""
        scraper = ScraperFactory.create_scraper(
            url, 
            headless=self.config['scraper'].get('headless', True)
        )
        
        if not scraper:
            logging.warning(f"No scraper found for URL: {url}")
            return ScrapedResult(
                store="unknown",
                url=url,
                product={
                    "name": "",
                    "price": "",
                    "product_url": url,
                    "stock_status": "Out of Stock"
                },
                success=False,
                error_message="Unsupported platform"
            )
        
        try:
            with scraper:
                result = scraper.scrape_product(url)
                logging.info(f"Successfully scraped: {url}")
                return result
        except Exception as e:
            logging.error(f"Error scraping {url}: {e}")
            return ScrapedResult(
                store=scraper.platform,
                url=url,
                product={
                    "name": "",
                    "price": "",
                    "product_url": url,
                    "stock_status": "Out of Stock"
                },
                success=False,
                error_message=str(e)
            )
    
    def scrape_urls(self, urls: List[str]) -> List[ScrapedResult]:
        """Scrape multiple URLs"""
        results = []
        
        for i, url in enumerate(urls):
            logging.info(f"Scraping URL {i+1}/{len(urls)}: {url}")
            
            result = self.scrape_url(url)
            results.append(result)
            
            # Add delay between requests
            if i < len(urls) - 1:
                delay = self.config['scraper'].get('delay_between_requests', 2.0)
                time.sleep(delay)
        
        return results
    
    def run(self, urls: List[str]):
        """Main execution method"""
        logging.info(f"Starting scraping of {len(urls)} URLs")
        
        results = self.scrape_urls(urls)
        
        # Write results
        self.output_writer.write_results(results)
        
        # Print summary
        successful = sum(1 for r in results if r.success)
        logging.info(f"Scraping completed. Successful: {successful}/{len(urls)}")

def main():
    parser = argparse.ArgumentParser(description="Multi-platform E-commerce Scraper")
    parser.add_argument("--urls", nargs="+", help="List of URLs to scrape")
    parser.add_argument("--file", help="File containing URLs (one per line)")
    parser.add_argument("--config", default="config/settings.yaml", help="Config file path")
    
    args = parser.parse_args()
    
    # Get URLs from arguments or file
    urls = []
    if args.urls:
        urls = args.urls
    elif args.file:
        urls = read_urls_from_file(args.file)
    else:
        # Default to sample URLs if none provided
        urls = [
            "https://www.amazon.com/dp/B09XYZ123",
            "https://www.aliexpress.com/item/123456.html",
            "https://www.ebay.com/itm/1234567890"
        ]
    
    if not urls:
        print("No valid URLs provided. Use --urls or --file arguments.")
        return
    
    # Run scraper
    scraper = ECommerceScraper(config_path=args.config)
    scraper.run(urls)

if __name__ == "__main__":
    main()