# Multi-Platform E-commerce Scraper

An intelligent, scalable web automation tool for extracting product information and delivery details from major e-commerce platforms worldwide. Built with Python and designed to handle dynamic content, anti-bot measures, and deliver structured data in multiple formats.

🌟 Features
- **Multi-Platform Support**: Amazon, AliExpress, eBay, Etsy, Jumia, Kilimall, Jiji, and more
- **Product Data Extraction**: Comprehensive product information including prices, stock status, ratings, and more
- **Checkout Simulation**: Automated basket addition and delivery option extraction
- **Anti-Bot Protection**: Proxy rotation, user-agent randomization, and human-like behavior simulation
- **Multiple Output Formats**: JSON, CSV, and Excel exports with consistent schema
- **Dockerized Deployment**: Easy containerization for scalable deployment

📋 Supported Data Fields
For each product, the scraper extracts:
- Product Name & Brand
- Current Price & Discount Price
- SKU/Product ID
- Category Information
- Product & Image URLs
- Stock Status & Seller Information
- Ratings & Review Counts
- Shipping/Delivery Options (via checkout simulation)

🛠️ Installation
**Prerequisites**
- Python 3.10+
- Google Chrome browser
- Docker (optional, for containerized deployment)

**Local Installation**
Clone the repository:
```bash
git clone <repository-url>
cd multi-platform-scraper
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Install Playwright browsers:
```bash
playwright install chromium
```

**Docker Installation**
```bash
docker build -t ecommerce-scraper .
```

📖 Usage
**Basic Usage**
```bash
# Run with specific URLs
python src/main.py --urls "https://www.amazon.com/dp/B08N5WRWNW" "https://www.ebay.com/itm/284003579041"

# Run with URL file
python src/main.py --file data/input_urls.csv

# Run with custom config
python src/main.py --urls "https://www.amazon.com/dp/B08N5WRWNW" --config config/custom_settings.yaml
```
**Docker Usage**
```bash
# Build and run
docker build -t ecommerce-scraper .
docker run -v $(pwd)/data:/app/data ecommerce-scraper

# Or with specific URLs
docker run -v $(pwd)/data:/app/data ecommerce-scraper python src/main.py --urls "https://www.amazon.com/dp/B08N5WRWNW"
```

**Input Format**
Create a CSV file with URLs (one per line):
```csv
url
https://www.amazon.com/dp/B08N5WRWNW
https://www.aliexpress.com/item/1005002956352981.html
https://www.ebay.com/itm/284003579041
```

⚙️ Configuration
The scraper can be configured using YAML files in the `config/` directory:

**settings.yaml**
```yaml
scraper:
  headless: true           # Run browser in headless mode
  timeout: 30              # Timeout for page operations
  max_retries: 3           # Maximum retry attempts
  delay_between_requests: 1.5  # Delay between requests

proxies:
  enabled: false           # Enable proxy rotation
  list: []                 # List of proxy servers

output:
  json_path: "data/output.json"
  csv_path: "data/output.csv"
  excel_path: "data/output.xlsx"
  screenshots_dir: "data/screenshots"
```

**selectors.yaml**
Contains CSS selectors for each platform to handle different website structures.

📊 Output Formats
**JSON Output**
```json
{
  "store": "amazon.com",
  "url": "https://www.amazon.com/dp/B09XYZ123",
  "product": {
    "name": "Samsung Galaxy A54",
    "price": "$299.99",
    "discount_price": "$249.99",
    "sku": "B09XYZ123",
    "brand": "Samsung",
    "category": "Electronics > Mobile Phones",
    "product_url": "https://www.amazon.com/dp/B09XYZ123",
    "image_url": "https://m.media-amazon.com/images/I/xyz.jpg",
    "stock_status": "In Stock",
    "rating": "4.6",
    "reviews": "12,430",
    "seller": "Samsung Official Store"
  },
  "scenarios": {
    "below_threshold": {
      "delivery_options": [
        {"company": "Amazon Logistics", "type": "Standard Shipping", "price": "$5.99", "eta": "3-5 days"}
      ],
      "screenshot": "screenshots/amazon_below.png"
    }
  }
}
```

**CSV/Excel Output**
Flattened structure with all product and delivery information in tabular format.

🏗️ Project Structure
```
multi-platform-scraper/
├── config/                 # Configuration files
│   ├── settings.yaml      # Main configuration
│   └── selectors.yaml     # Platform-specific selectors
├── data/                  # Data directory
│   ├── input_urls.csv     # Input URLs
│   ├── output.json        # JSON output
│   ├── output.csv         # CSV output
│   ├── output.xlsx        # Excel output
│   └── screenshots/       # Checkout screenshots
├── src/                   # Source code
│   ├── main.py            # Main orchestrator
│   ├── scraper_factory.py # Platform dispatcher
│   ├── base_scraper.py    # Shared scraping logic
│   ├── amazon_scraper.py  # Amazon-specific scraper
│   ├── aliexpress_scraper.py # AliExpress scraper
│   ├── ebay_scraper.py    # eBay scraper
│   ├── etsy_scraper.py    # Etsy scraper
│   ├── jumia_scraper.py   # Jumia scraper
│   ├── kilimall_scraper.py # Kilimall scraper
│   ├── jiji_scraper.py    # Jiji scraper
│   ├── product_schema.py  # Pydantic data models
│   ├── output_writer.py   # Output formatting
│   └── utils.py           # Utility functions
├── tests/                 # Test cases
├── Dockerfile            # Container configuration
└── requirements.txt      # Python dependencies
```

🔧 Advanced Configuration
**Proxy Setup**
Enable proxy rotation in `config/settings.yaml`:
```yaml
proxies:
  enabled: true
  list:
    - "http://proxy1:port"
    - "http://proxy2:port"
  rotation_interval: 10
```

**Custom Selectors**
Add platform-specific selectors in `config/selectors.yaml`:
```yaml
new_platform:
  product_name: [".product-title"]
  price: [".price-selector"]
  # ... other selectors
```

🚀 Performance Tips
- Use Headless Mode: Enable `headless: true` for faster execution
- Adjust Timeouts: Modify timeouts based on target website responsiveness
- Proxy Rotation: Use proxies to avoid IP blocking for large-scale scraping
- Request Throttling: Adjust `delay_between_requests` to avoid overwhelming targets

⚠️ Legal Considerations
- Respect `robots.txt` directives
- Check website Terms of Service before scraping
- Use scraping responsibly and ethically
- Consider using official APIs when available

🐛 Troubleshooting
**Common Issues**
- Element Not Found: Update selectors in `config/selectors.yaml`
- Blocked Requests: Enable proxies or increase delays between requests
- CAPTCHA Challenges: Implement CAPTCHA solving services or increase human-like behavior

**Debug Mode**
Run with headless mode disabled to see browser interactions:
```yaml
# config/settings.yaml
scraper:
  headless: false
```

📈 Scaling for Production
For large-scale deployment:
- Implement distributed task queues (Celery, Redis Queue)
- Use cloud-based browser automation services
- Set up monitoring and alerting for failed scrapes
- Implement data validation and quality checks

🤝 Contributing
- Fork the repository
- Create a feature branch
- Add tests for new functionality
- Submit a pull request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🆓 Free Tool Notice
This is a free, open-source tool. For commercial use or high-volume scraping, please ensure compliance with target websites' terms of service and consider using official APIs where available.

**Disclaimer:** This tool is for educational and research purposes. Users are responsible for ensuring their scraping activities comply with applicable laws and website terms of service.
