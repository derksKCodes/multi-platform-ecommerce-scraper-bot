from base_scraper import BaseScraper
from product_schema import ProductData, ScrapedResult, StockStatus, DeliveryOption, CheckoutScenario
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from typing import Dict, Any, List, Optional
import re

class AmazonScraper(BaseScraper):
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.platform = "amazon"
    
    def scrape_product(self, url: str) -> ScrapedResult:
        try:
            self.driver.get(url)
            time.sleep(self.get_random_delay())
            
            # Human-like behavior
            self.human_like_scroll()
            
            product_data = self._extract_product_data()
            
            return ScrapedResult(
                store="amazon.com",
                url=url,
                product=product_data,
                scenarios=self._simulate_checkout_scenarios(product_data)
            )
            
        except Exception as e:
            logging.error(f"Error scraping Amazon product: {e}")
            return ScrapedResult(
                store="amazon.com",
                url=url,
                product=ProductData(
                    name="",
                    price="",
                    product_url=url,
                    stock_status=StockStatus.OUT_OF_STOCK
                ),
                success=False,
                error_message=str(e)
            )
    
    def _extract_product_data(self) -> ProductData:
        selectors = self.selectors.get('amazon', {})
        
        name = self._extract_with_selectors(selectors.get('product_name', []))
        price = self._extract_with_selectors(selectors.get('price', []))
        discount_price = self._extract_with_selectors(selectors.get('discount_price', []))
        brand = self._extract_with_selectors(selectors.get('brand', []))
        category = self._extract_category()
        sku = self._extract_sku()
        image_urls = self._extract_images()
        stock_status = self._extract_stock_status()
        rating = self._extract_rating()
        reviews = self._extract_reviews()
        seller = self._extract_seller()
        
        return ProductData(
            name=name or "Unknown",
            price=price or "0",
            discount_price=discount_price,
            sku=sku,
            brand=brand,
            category=category,
            product_url=self.driver.current_url,
            image_urls=image_urls,
            stock_status=stock_status,
            rating=rating,
            reviews=reviews,
            seller=seller
        )
    
    def _extract_with_selectors(self, selector_list: List[str]) -> Optional[str]:
        for selector in selector_list:
            try:
                element = self.find_element_safe(By.CSS_SELECTOR, selector, 5)
                if element:
                    return self.extract_text(element)
            except:
                continue
        return None
    
    def _extract_category(self) -> Optional[str]:
        try:
            breadcrumb_elements = self.driver.find_elements(
                By.CSS_SELECTOR, ".a-breadcrumb li:not(.a-breadcrumb-divider) a"
            )
            categories = [elem.text.strip() for elem in breadcrumb_elements if elem.text.strip()]
            return " > ".join(categories) if categories else None
        except:
            return None
    
    def _extract_sku(self) -> Optional[str]:
        # Try to extract SKU from various locations
        try:
            # Check product details table
            details = self.driver.find_elements(By.CSS_SELECTOR, ".prodDetTable tr")
            for row in details:
                if "ASIN" in row.text or "SKU" in row.text or "Model" in row.text:
                    return row.text.split(":")[-1].strip()
        except:
            pass
        
        # Try to extract from URL
        url = self.driver.current_url
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
        if asin_match:
            return asin_match.group(1)
        
        return None
    
    def _extract_images(self) -> List[str]:
        images = []
        try:
            img_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "img[data-old-hires], #landingImage, .a-dynamic-image"
            )
            for img in img_elements:
                src = img.get_attribute('src') or img.get_attribute('data-src')
                if src and 'http' in src:
                    images.append(src)
        except:
            pass
        return images
    
    def _extract_stock_status(self) -> StockStatus:
        try:
            stock_elem = self.find_element_safe(
                By.CSS_SELECTOR, "#availability .a-size-medium, #availability span"
            )
            if stock_elem:
                text = stock_elem.text.lower()
                if 'in stock' in text:
                    return StockStatus.IN_STOCK
                elif 'out of stock' in text:
                    return StockStatus.OUT_OF_STOCK
                elif 'limited' in text:
                    return StockStatus.LIMITED_STOCK
        except:
            pass
        return StockStatus.OUT_OF_STOCK
    
    def _extract_rating(self) -> Optional[str]:
        try:
            rating_elem = self.find_element_safe(
                By.CSS_SELECTOR, ".a-icon-alt, [data-hook='rating-out-of-text']"
            )
            if rating_elem:
                text = rating_elem.get_attribute('textContent') or rating_elem.text
                match = re.search(r'(\d+\.\d+)', text)
                return match.group(1) if match else None
        except:
            return None
    
    def _extract_reviews(self) -> Optional[str]:
        try:
            reviews_elem = self.find_element_safe(
                By.CSS_SELECTOR, "#acrCustomerReviewText, [data-hook='total-review-count']"
            )
            if reviews_elem:
                text = reviews_elem.text
                numbers = re.findall(r'\d+', text.replace(',', ''))
                return numbers[0] if numbers else None
        except:
            return None
    
    def _extract_seller(self) -> Optional[str]:
        try:
            seller_elem = self.find_element_safe(
                By.CSS_SELECTOR, "#merchant-info, .a-link-normal.contributorNameID"
            )
            return self.extract_text(seller_elem) if seller_elem else None
        except:
            return None
    
    def _simulate_checkout_scenarios(self, product_data: ProductData) -> Dict[str, CheckoutScenario]:
        scenarios = {}
        
        try:
            # Scenario 1: Single item (below free shipping threshold)
            scenarios['below_threshold'] = self._checkout_scenario(quantity=1)
            
            # Scenario 2: Multiple items (above free shipping threshold)
            scenarios['above_threshold'] = self._checkout_scenario(quantity=5)
            
        except Exception as e:
            self.logger.error(f"Error during checkout simulation: {e}")
        
        return scenarios
    
    def _checkout_scenario(self, quantity: int = 1) -> CheckoutScenario:
        try:
            # Add to cart
            add_to_cart_btn = self.find_element_safe(By.ID, "add-to-cart-button")
            if add_to_cart_btn:
                add_to_cart_btn.click()
                time.sleep(self.get_random_delay())
            
            # Go to cart
            self.driver.get("https://www.amazon.com/gp/cart/view.html")
            time.sleep(self.get_random_delay())
            
            # Update quantity if needed
            if quantity > 1:
                quantity_dropdown = self.find_element_safe(By.NAME, "quantity")
                if quantity_dropdown:
                    quantity_dropdown.send_keys(str(quantity))
                    time.sleep(self.get_random_delay())
            
            # Proceed to checkout
            checkout_btn = self.find_element_safe(By.NAME, "proceedToRetailCheckout")
            if checkout_btn:
                checkout_btn.click()
                time.sleep(self.get_random_delay())
            
            # Extract delivery options
            delivery_options = self._extract_delivery_options()
            
            # Take screenshot
            screenshot_path = f"data/screenshots/amazon_{quantity}_items_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            
            return CheckoutScenario(
                scenario_name=f"{quantity}_item{'s' if quantity > 1 else ''}",
                delivery_options=delivery_options,
                screenshot_path=screenshot_path
            )
            
        except Exception as e:
            self.logger.error(f"Error in checkout scenario: {e}")
            return CheckoutScenario(
                scenario_name=f"{quantity}_items",
                delivery_options=[],
                error_message=str(e)
            )
    
    def _extract_delivery_options(self) -> List[DeliveryOption]:
        options = []
        try:
            # Look for delivery option elements
            delivery_elems = self.driver.find_elements(
                By.CSS_SELECTOR, ".a-radio-label, .ship-option"
            )
            
            for elem in delivery_elems:
                text = elem.text
                if any(keyword in text.lower() for keyword in ['delivery', 'shipping', 'ship']):
                    # Parse delivery option
                    company = "Amazon"
                    delivery_type = "Standard"
                    price = "0.00"
                    eta = "3-5 days"
                    
                    # Extract price
                    price_match = re.search(r'\$(\d+\.\d+)', text)
                    if price_match:
                        price = price_match.group(0)
                    
                    # Extract ETA
                    eta_match = re.search(r'(\d+[-–]\d+\s*(days|business days))', text, re.IGNORECASE)
                    if eta_match:
                        eta = eta_match.group(1)
                    
                    options.append(DeliveryOption(
                        company=company,
                        type=delivery_type,
                        price=price,
                        eta=eta
                    ))
        except Exception as e:
            self.logger.error(f"Error extracting delivery options: {e}")
        
        return options
    
    def simulate_checkout(self, product_data: ProductData, quantity: int = 1) -> Dict[str, Any]:
        """
        Implements the abstract method required by BaseScraper.
        Wraps the existing checkout scenario logic.
        """
        try:
            # Use the same flow as _checkout_scenario
            scenario = self._checkout_scenario(quantity=quantity)
            return {
                "scenario_name": scenario.scenario_name,
                "delivery_options": [opt.__dict__ for opt in scenario.delivery_options],
                "screenshot_path": scenario.screenshot_path,
                "error_message": scenario.error_message,
            }
        except Exception as e:
            self.logger.error(f"simulate_checkout failed: {e}")
            return {
                "scenario_name": f"{quantity}_items",
                "delivery_options": [],
                "error_message": str(e),
            }
