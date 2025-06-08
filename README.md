# AliExpress Product Scraper

A Python-based web scraper designed to extract product information from AliExpress search results. This tool automatically scrapes product details including titles, prices, ratings, shipping information, and sales data, then exports the results to a CSV file.

## 🚀 Features

- **Automated Web Scraping**: Uses Selenium WebDriver with anti-detection measures
- **Comprehensive Data Extraction**: Captures product titles, prices, ratings, shipping info, and sales numbers
- **Smart HTML Parsing**: Robust extraction logic that adapts to AliExpress's dynamic class names
- **CSV Export**: Automatically exports scraped data to `aliexpress_products.csv`
- **Fallback Mechanisms**: Includes sample data generation when scraping fails
- **Human-like Behavior**: Implements random delays and scrolling patterns to avoid detection

## 📊 Extracted Data Fields

The scraper captures the following information for each product:

- **Title**: Product name and description
- **Price**: Current selling price (in USD)
- **Rating**: Customer review rating (with star symbols)
- **Sold**: Number of items sold (e.g., "500+ sold", "1,000+ sold")
- **Shipping**: Shipping information (e.g., "Free shipping")

## 🛠️ Installation

### Prerequisites

- Python 3.9 or higher
- Chrome browser installed
- Git (for cloning the repository)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/harveylijh/aliexpress-pages-scrapper.git
   cd aliexpress-pages-scrapper
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv scraper
   source scraper/bin/activate  # On macOS/Linux
   # or
   scraper\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Usage

### Basic Usage

Run the scraper with default settings (searches for "electronics"):

```bash
python main.py
```

### What Happens When You Run It

1. **Browser Launch**: Opens Chrome browser with anti-detection settings
2. **Page Navigation**: Navigates to AliExpress electronics search page
3. **Intelligent Scrolling**: Scrolls through results to load more products
4. **Data Extraction**: Parses HTML and extracts product information
5. **CSV Export**: Saves results to `aliexpress_products.csv`
6. **Console Output**: Displays progress and extracted product details

### Sample Output

```
-> AliExpress Scrapper : Start
-> AliExpress Scrapper : Scrolling …
-> AliExpress Scrapper : Found 64 products so far...
-> AliExpress Scrapper : Found sufficient products, stopping scroll.
-> AliExpress Scrapper : Looking for products...
-> AliExpress Scrapper : Found 60 products using card-out-wrapper selector
-> Extracted: Portable Translation Pen 2.99inch Screen Scanning ... - $30.06
-> Extracted: Smart Ring R08 Womens Men Electronic Smartring 5AT... - $21.23
-> AliExpress Scrapper : Successfully extracted 30 products
-> AliExpress Scrapper : Completed successfully!
-> Total products: 30
```

## 📁 Project Structure

```
aliexpress-pages-scrapper/
├── main.py                    # Main scraper application
├── Product.py                 # Product data class
├── Bcolors.py                # Terminal color formatting
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── aliexpress_products.csv  # Output CSV file (generated)
├── page_source.html         # Debug HTML file (generated)
└── scraper/                 # Virtual environment folder
```

## 🔧 Configuration

### Modifying Search Terms

To scrape different products, modify the URL in `main.py`:

```python
# Change this line to search for different products
url = "https://www.aliexpress.com/wholesale?SearchText=electronics"
# Example: url = "https://www.aliexpress.com/wholesale?SearchText=smartphones"
```

### Adjusting Product Limit

To change the number of products scraped, modify the limit in the extraction loop:

```python
for i, product_element in enumerate(products_elements[:30]):  # Change 30 to desired number
```

## 🛡️ Anti-Detection Features

The scraper includes several anti-detection mechanisms:

- **User Agent Spoofing**: Mimics real browser headers
- **Random Delays**: Variable timing between actions
- **Human-like Scrolling**: Natural scrolling patterns
- **Browser Property Masking**: Hides automation indicators
- **Request Throttling**: Controlled request rate

## 📋 Dependencies

### Core Libraries

- **selenium**: Web browser automation
- **beautifulsoup4**: HTML parsing and extraction
- **pandas**: Data manipulation and CSV export
- **requests**: HTTP requests handling

### Support Libraries

- **webdriver-manager**: Automatic Chrome driver management
- **numpy**: Numerical operations for pandas
- **fake-useragent**: User agent generation

## 🐛 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**:
   - The script automatically downloads the Chrome driver
   - Ensure Chrome browser is installed and up to date

2. **Anti-Bot Detection**:
   - If blocked, try running the script again after a few minutes
   - The script includes automatic retry mechanisms

3. **No Products Found**:
   - Check your internet connection
   - Verify the AliExpress URL is accessible
   - The script will generate sample data as fallback

4. **Permission Errors**:
   - Run with appropriate permissions
   - Ensure write access to the project directory

### Debug Mode

The scraper automatically saves the page source to `page_source.html` for debugging. You can inspect this file to understand the current page structure.

## 📊 Sample Output

The generated CSV file contains data like:

| Title | Rev_Rate | Sold | Shipping | Price |
|-------|----------|------|----------|-------|
| Portable Translation Pen 2.99inch Screen... | N/A | 1 sold | Free shipping | $30.06 |
| Smart Ring R08 Womens Men Electronic... | 5.0★ | 8 sold | N/A | $21.23 |
| Military Digital Watch for Men Outdoor... | 4.0★ | 500+ sold | Free shipping | $4.35 |

## ⚖️ Legal and Ethical Considerations

- **Respect robots.txt**: Always check and respect website policies
- **Rate Limiting**: The scraper includes delays to avoid overwhelming servers
- **Personal Use**: Intended for educational and personal research purposes
- **Data Usage**: Be mindful of how you use the scraped data
- **Terms of Service**: Ensure compliance with AliExpress Terms of Service

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request

## 📄 License

This project is for educational purposes. Please respect AliExpress's terms of service and use responsibly.

## 🔄 Version History

- **v1.0**: Initial release with basic scraping functionality
- **v1.1**: Added anti-detection measures and improved extraction logic
- **v1.2**: Enhanced HTML parsing for better data accuracy
- **v1.3**: Added robust error handling and fallback mechanisms

## 📧 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the generated `page_source.html` for debugging
3. Open an issue on the GitHub repository


**Disclaimer**: This tool is for educational and research purposes only. Users are responsible for ensuring their use complies with applicable laws and website terms of service.
