from Bcolors import Bcolors as bc
from Product import Product
from bs4 import BeautifulSoup
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import random

# Search for various product categories on AliExpress
keywords = [
    'headphones',
    'laptops', 
    'garden supplies',
    'phone cases',
    'led lights',
    'kitchen gadgets',
    'fitness tracker',
    'bluetooth speaker',
    'gaming mouse',
    'home decor'
]

products = []

def export_data_to_csv():
    global products
    data = {"Keyword": [], "Title": [], "Rev_Rate": [], "Sold": [], "Shipping": [], "Price": [], "Image": []}
    for product in products:
        # Try to extract keyword from product title or set as unknown
        keyword_found = "Unknown"
        for kw in keywords:
            if any(word.lower() in product.title.lower() for word in kw.split()):
                keyword_found = kw
                break
        
        data["Keyword"].append(keyword_found)
        data["Title"].append(product.title)
        data["Rev_Rate"].append(product.rev_rate)
        data["Sold"].append(product.Sold)
        data["Shipping"].append(product.shipping)
        data["Price"].append(product.price)
        data["Image"].append(product.image_link if hasattr(product, 'image_link') else "N/A")
    df = pd.DataFrame(data)
    df.to_csv('aliexpress_products.csv', index=False)
    print(f"-> AliExpress Scrapper : Exported {len(products)} products to aliexpress_products.csv")


def get_url_page(url):
    options = Options()
    # Remove headless argument entirely to show the browser window
    # options.add_argument('--headless')  # Commented out to show browser
    
    # Enhanced anti-detection measures
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 2
    })
    
    # Use webdriver-manager to automatically download and manage Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Execute multiple anti-detection scripts
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
    driver.execute_script("Object.defineProperty(navigator, 'permissions', {get: () => undefined})")
    
    # Add random delay before accessing the URL
    sleep(2 + (random.random() * 1.5))  # Random delay between 2-3.5 seconds
    
    try:
        driver.get(url)
        sleep(5)  # Wait for page to load
    
        # Check if we hit a captcha or block page
        page_text = driver.page_source.lower()
        if any(blocked_term in page_text for blocked_term in ['captcha', 'robot', 'verification', 'blocked', 'suspicious']):
            print("-> AliExpress Scrapper : Detected anti-bot protection. Trying alternative approach...")
            # Try refreshing the page
            driver.refresh()
            sleep(3)
            
    except Exception as e:
        print(f"-> AliExpress Scrapper : Error loading page: {e}")
        driver.quit()
        return None

    print("-> AliExpress Scrapper : Scrolling …")
    
    # More human-like scrolling behavior
    scroll_step = random.randint(250, 400)  # Variable scroll distance
    max_scrolls = 80  # Reduced number of scrolls
    
    for i in range(max_scrolls):
        # Variable scroll step to mimic human behavior
        current_scroll = scroll_step + random.randint(-50, 50)
        driver.execute_script(f"window.scrollBy(0, {current_scroll});")
        
        # Variable delay to mimic human behavior
        delay = random.uniform(0.5, 1.2)
        sleep(delay)
        
        # Check if we have enough content every 10 scrolls
        if i % 10 == 0:
            try:
                # Count product elements to see if we have enough
                product_count = driver.execute_script("""
                    const selectors = [
                        'div[data-pl="search-item"]',
                        'div.manhattan--container--1lP57Ag',
                        'div[class*="product-item"]',
                        'a[href*="/item/"]'
                    ];
                    let maxCount = 0;
                    selectors.forEach(selector => {
                        const elements = document.querySelectorAll(selector);
                        maxCount = Math.max(maxCount, elements.length);
                    });
                    return maxCount;
                """)
                print(f"-> AliExpress Scrapper : Found {product_count} products so far...")
                
                # If we have enough products, we can stop early
                if product_count >= 30:
                    print("-> AliExpress Scrapper : Found sufficient products, stopping scroll.")
                    break
                    
            except Exception as e:
                print(f"-> AliExpress Scrapper : Error checking product count: {e}")

        # break if we're already at the bottom
        try:
            at_bottom = driver.execute_script(
                "return window.innerHeight + window.pageYOffset >= document.body.scrollHeight - 100;"
            )
            if at_bottom:
                print("-> AliExpress Scrapper : Reached bottom, stopping scroll.")
                break
        except Exception as e:
            print(f"-> AliExpress Scrapper : Error checking scroll position: {e}")
            break

    html = driver.page_source
    driver.quit()
    return html


def scrap_products(soup_object):
    global products
    print(f"-> AliExpress Scrapper : Looking for products...")
    
    # Keep track of existing product titles to prevent duplicates
    existing_titles = {product.title.lower().strip() for product in products}
    duplicates_found = 0
    new_products_added = 0
    
    # Debug: Save HTML to file for inspection
    with open('page_source.html', 'w', encoding='utf-8') as f:
        f.write(str(soup_object))
    print(f"-> AliExpress Scrapper : Saved page source to page_source.html")
    
    # Use the specific selector for AliExpress card wrappers
    products_elements = soup_object.select('div.card-out-wrapper')
    print(f"-> AliExpress Scrapper : Found {len(products_elements)} products using card-out-wrapper selector")
    
    if len(products_elements) == 0:
        print("-> AliExpress Scrapper : No products found with card-out-wrapper. Trying search-item-card-wrapper...")
        products_elements = soup_object.select('div.search-item-card-wrapper-gallery')
        print(f"-> AliExpress Scrapper : Found {len(products_elements)} products using search-item-card-wrapper-gallery selector")
    
    if len(products_elements) == 0:
        print("-> AliExpress Scrapper : No products found with any selector. Trying fallback approach...")
        # Fallback: look for any div with a link containing '/item/'
        all_links = soup_object.find_all('a', href=True)
        product_links = [link for link in all_links if '/item/' in link.get('href', '')]
        products_elements = [link.find_parent('div') for link in product_links[:20] if link.find_parent('div')]
        print(f"-> AliExpress Scrapper : Found {len(products_elements)} products using fallback method")

    for i, product_element in enumerate(products_elements[:30]):  # Limit to 30 products
        if not product_element:
            continue
            
        try:
            # Extract title - look for h3 elements or title attributes
            title_text = extract_product_title(product_element)
            
            # Extract price - look for price containers
            price_text = extract_product_price(product_element)
            
            # Extract rating
            rating_text = extract_product_rating(product_element)
            
            # Extract shipping info
            shipping_text = extract_product_shipping(product_element)
            
            # Extract orders/sold info
            orders_text = extract_product_orders(product_element)

            image_links=extract_image_links(product_element)

            # Clean and validate extracted data - keep full title without truncation
            title_text = clean_text(title_text) if title_text else f"Product {i+1}"
            price_text = clean_text(price_text) if price_text else "N/A"
            rating_text = clean_text(rating_text) if rating_text else "N/A"
            shipping_text = clean_text(shipping_text) if shipping_text else "N/A"
            orders_text = clean_text(orders_text) if orders_text else "N/A"
            image_links_text = f'[{", ".join(image_links)}]' if image_links else "N/A"

            # Check for duplicates and only add products with meaningful, unique data
            title_normalized = title_text.lower().strip()
            if title_text and title_text != f"Product {i+1}" and not is_duplicate_title(title_text, existing_titles):
                product_object = Product(title_text, rating_text, orders_text, shipping_text, price_text, image_links_text)
                product_object.description()
                products.append(product_object)
                existing_titles.add(title_normalized)  # Add to set to prevent future duplicates
                new_products_added += 1
                print(f"-> Extracted: {title_text[:80]}... - {price_text}")
            elif is_duplicate_title(title_text, existing_titles):
                duplicates_found += 1
                print(f"-> Skipped duplicate: {title_text[:50]}...")
                
        except Exception as e:
            print(f"-> Error extracting product {i}: {e}")
            continue
            
    print(f"-> AliExpress Scrapper : Added {new_products_added} new products, skipped {duplicates_found} duplicates")
    print(f"-> AliExpress Scrapper : Total unique products now: {len(products)}")


def extract_product_title(element):
    """Extract product title from h3 tag or title attribute"""
    # First try to find h3 element (most common)
    h3_element = element.select_one('h3')
    if h3_element:
        return h3_element.get_text(strip=True)
    
    # Try title attribute from div or a elements
    title_element = element.select_one('div[title]')
    if title_element:
        return title_element.get('title')
    
    title_element = element.select_one('a[title]')
    if title_element:
        return title_element.get('title')
    
    # Fallback to img alt text
    img_element = element.select_one('img[alt]')
    if img_element:
        alt_text = img_element.get('alt')
        if alt_text and len(alt_text) > 10:  # Only use meaningful alt text
            return alt_text
    
    return None


def extract_product_price(element):
    """Extract product price - look for spans with specific styling"""
    # Look for the main price (current price) with large font
    price_spans = element.select('span[style*="font-size:20px"]')
    if price_spans:
        # Combine all spans to form the price
        price_parts = []
        for span in price_spans:
            text = span.get_text(strip=True)
            if text:
                price_parts.append(text)
        if price_parts:
            return ''.join(price_parts)
    
    # Look for price in common AliExpress price containers
    price_containers = element.select('div[class*="price"], span[class*="price"]')
    for container in price_containers:
        text = container.get_text(strip=True)
        if '$' in text:
            import re
            price_match = re.search(r'\$[\d.,]+', text)
            if price_match:
                return price_match.group()
    
    # Fallback: look for any element containing a dollar sign
    all_text_elements = element.find_all(string=True)
    for text in all_text_elements:
        text = text.strip()
        if '$' in text and any(char.isdigit() for char in text):
            # Clean up the price text
            import re
            price_match = re.search(r'\$[\d.,]+', text)
            if price_match:
                return price_match.group()
    
    return None


def extract_product_rating(element):
    """Extract product rating"""
    # Look for rating text in specific spans (AliExpress usually has this pattern)
    # The rating is often near star images in a span
    rating_spans = element.select('span')
    for span in rating_spans:
        text = span.get_text(strip=True)
        if text and text.replace('.', '').replace(',', '').isdigit():
            try:
                rating_val = float(text)
                if 1.0 <= rating_val <= 5.0:
                    return f"{rating_val}★"
            except ValueError:
                continue
    
    # Look for patterns like "4.3" followed by star images
    all_text_elements = element.find_all(string=True)
    for text in all_text_elements:
        text = text.strip()
        if text and len(text) <= 5:  # Rating should be short
            try:
                rating_val = float(text)
                if 1.0 <= rating_val <= 5.0:
                    # Check if there are star images nearby
                    parent = text.parent if hasattr(text, 'parent') else None
                    if parent:
                        nearby_stars = parent.find_parent().select('img[src*="star"]') if parent.find_parent() else []
                        if nearby_stars:
                            return f"{rating_val}★"
            except (ValueError, AttributeError):
                continue
    
    # Count star images as fallback
    star_images = element.select('img[src*="star"]')
    if star_images:
        return f"{len(star_images)}/5★"
    
    return None


def extract_product_shipping(element):
    """Extract shipping information"""
    # Look for "Free shipping" text
    all_text_elements = element.find_all(string=True)
    for text in all_text_elements:
        text_lower = text.strip().lower()
        if 'free shipping' in text_lower:
            return "Free shipping"
        elif 'shipping' in text_lower:
            return text.strip()
    
    # Look for spans with shipping-related titles
    shipping_spans = element.select('span[title*="shipping" i]')
    if shipping_spans:
        return shipping_spans[0].get('title')
    
    return None


def extract_product_orders(element):
    """Extract number of orders/sold"""
    # Look for "sold" text
    all_text_elements = element.find_all(string=True)
    for text in all_text_elements:
        text_stripped = text.strip()
        if 'sold' in text_stripped.lower():
            return text_stripped
    
    # Look for order-related patterns
    import re
    for text in all_text_elements:
        text_stripped = text.strip()
        # Match patterns like "500+ sold", "1,234 orders", etc.
        if re.search(r'\d+.*(?:sold|orders?)', text_stripped, re.IGNORECASE):
            return text_stripped
    
    return None


def extract_image_links(element):
    """
    Extract all product image URLs from a container div with style="transform: translateX(0%);"
    """
    image_links = []
    image_wrappers = element.find_all("div", style="transform: translateX(0%);")

    for wrapper in image_wrappers:
        img_tags = wrapper.find_all("img", class_="mn_bc")
        for img in img_tags:
            src = img.get("src")
            if src:
                # Ensure it's a full URL
                if src.startswith("//"):
                    src = "https:" + src
                elif src.startswith("/"):
                    src = f"https://www.aliexpress.com{src}"
                image_links.append(src)
    
    return image_links



def extract_text_with_selectors(element, selectors, attribute=None):
    """Try multiple selectors to extract text from an element"""
    for selector in selectors:
        try:
            found_element = element.select_one(selector)
            if found_element:
                if attribute:
                    text = found_element.get(attribute)
                    if text:
                        return text
                text = found_element.get_text(strip=True)
                if text:
                    return text
        except Exception:
            continue
    return None


def clean_text(text):
    """Clean and normalize extracted text while preserving full content"""
    if not text:
        return ""
    # Remove extra whitespace and newlines but keep full content
    if isinstance(text, list):
        text = ' '.join(str(item) for item in text)
    else:
        text = str(text)
    
    # Clean up whitespace but preserve full title
    text = ' '.join(text.split())  # Removes extra spaces and newlines
    return text


def is_duplicate_title(new_title, existing_titles, similarity_threshold=0.9):
    """
    Check if a title is a duplicate based on similarity
    Uses simple string matching and length comparison
    """
    new_title_clean = new_title.lower().strip()
    
    # Exact match check
    if new_title_clean in existing_titles:
        return True
    
    # Check for very similar titles (accounting for minor variations)
    for existing_title in existing_titles:
        # If titles are very similar in length and content
        if len(new_title_clean) > 10 and len(existing_title) > 10:
            # Simple similarity check - count matching words
            new_words = set(new_title_clean.split())
            existing_words = set(existing_title.split())
            
            if len(new_words) > 0 and len(existing_words) > 0:
                common_words = new_words.intersection(existing_words)
                similarity = len(common_words) / max(len(new_words), len(existing_words))
                
                if similarity >= similarity_threshold:
                    return True
    
    return False


def main():
    print(f"-> AliExpress Scrapper : {bc.OKGREEN}Start{bc.DEFAULT}")
    global products
    products = []  # Reset products list
    
    for keyword in keywords:
        print(f"-> AliExpress Scrapper : {bc.OKBLUE}Scraping keyword: {keyword}{bc.DEFAULT}")
        
        # Scrape first 5 pages for each keyword to get variety without being too intensive
        for page_num in range(1, 6):
            print(f"-> AliExpress Scrapper : Scraping {keyword} - page {page_num}...")
            
            url = f"https://www.aliexpress.com/w/wholesale-{keyword.replace(' ', '%20')}.html?page={page_num}&g=y"
            
            html_page = get_url_page(url)
            if html_page:
                soup_object = BeautifulSoup(html_page, 'html.parser')
                scrap_products(soup_object)
                
                # Add a small delay between pages to be respectful
                sleep(2)
            else:
                print(f"-> AliExpress Scrapper : Failed to load {keyword} page {page_num}")
        
        # Add delay between different keywords
        print(f"-> AliExpress Scrapper : Completed {keyword}. Total products so far: {len(products)}")
        sleep(5)
    
    # Export all results after scraping all keywords
    if products:
        export_data_to_csv()
        print(f"-> AliExpress Scrapper : {bc.OKGREEN}Completed successfully!{bc.DEFAULT}")
        print(f"-> Total products: {len(products)}")

        # Show sample of what we collected
        print(f"\n-> Sample products:")
        for i, product in enumerate(products[:5], 1):
            print(f"   {i}. {product.title[:50]}... - {product.price}")
    else:
        print(f"-> AliExpress Scrapper : {bc.WARNING}No products were scraped{bc.DEFAULT}")

if __name__ == "__main__":
    main()