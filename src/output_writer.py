import json
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
from product_schema import ScrapedResult
import logging

class OutputWriter:
    def __init__(self, json_path: str = "data/output.json", 
                 csv_path: str = "data/output.csv",
                 excel_path: str = "data/output.xlsx"):
        self.json_path = json_path
        self.csv_path = csv_path
        self.excel_path = excel_path
        
        # Ensure directories exist
        Path(self.json_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.csv_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.excel_path).parent.mkdir(parents=True, exist_ok=True)
    
    def write_results(self, results: List[ScrapedResult]):
        """Write results to all output formats"""
        self.write_json(results)
        self.write_csv_excel(results)
    
    def write_json(self, results: List[ScrapedResult]):
        """Write results to JSON file"""
        try:
            serializable_results = [result.dict() for result in results]
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False, default=str)
            logging.info(f"JSON output written to {self.json_path}")
        except Exception as e:
            logging.error(f"Error writing JSON: {e}")
    
    def write_csv_excel(self, results: List[ScrapedResult]):
        """Write results to CSV and Excel files"""
        try:
            flattened_data = self._flatten_results(results)
            
            df = pd.DataFrame(flattened_data)
            
            # Write CSV
            df.to_csv(self.csv_path, index=False, encoding='utf-8')
            logging.info(f"CSV output written to {self.csv_path}")
            
            # Write Excel
            df.to_excel(self.excel_path, index=False, engine='openpyxl')
            logging.info(f"Excel output written to {self.excel_path}")
            
        except Exception as e:
            logging.error(f"Error writing CSV/Excel: {e}")
    
    def _flatten_results(self, results: List[ScrapedResult]) -> List[Dict[str, Any]]:
        """Flatten the nested structure for CSV/Excel output"""
        flattened = []
        
        for result in results:
            base_data = {
                'store': result.store,
                'url': result.url,
                'name': result.product.name,
                'price': result.product.price,
                'discount_price': result.product.discount_price,
                'sku': result.product.sku,
                'brand': result.product.brand,
                'category': result.product.category,
                'product_url': result.product.product_url,
                'image_url': result.product.image_urls[0] if result.product.image_urls else '',
                'stock_status': result.product.stock_status,
                'rating': result.product.rating,
                'reviews': result.product.reviews,
                'seller': result.product.seller,
                'success': result.success,
                'error_message': result.error_message,
                'timestamp': result.timestamp
            }
            
            # If no scenarios, add base data
            if not result.scenarios:
                flattened.append(base_data)
            else:
                # Add each scenario as a separate row
                for scenario_name, scenario in result.scenarios.items():
                    if scenario.delivery_options:
                        for delivery_option in scenario.delivery_options:
                            row = base_data.copy()
                            row.update({
                                'scenario': scenario_name,
                                'delivery_company': delivery_option.company,
                                'delivery_type': delivery_option.type,
                                'delivery_price': delivery_option.price,
                                'eta': delivery_option.eta,
                                'screenshot': scenario.screenshot_path
                            })
                            flattened.append(row)
                    else:
                        # If no delivery options, still add scenario info
                        row = base_data.copy()
                        row.update({
                            'scenario': scenario_name,
                            'delivery_company': '',
                            'delivery_type': '',
                            'delivery_price': '',
                            'eta': '',
                            'screenshot': scenario.screenshot_path
                        })
                        flattened.append(row)
        
        return flattened