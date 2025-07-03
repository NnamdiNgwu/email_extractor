from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import random
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class SeleniumGoogleSearch:
    """Advanced Google search using Selenium for JavaScript execution"""
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with anti-detection measures"""
        options = Options()
        
        # Anti-detection measures
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Realistic window size
        options.add_argument('--window-size=1366,768')
        
        # User agent rotation
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Selenium driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium driver: {e}")
            raise
    
    def search_google(self, keyword: str, country_code: str, max_results: int = 10) -> List[str]:
        """Search Google with JavaScript execution"""
        urls = []
        
        try:
            # Build country-specific Google URL
            google_domains = {
                ".com": "https://www.google.com",
                ".uk": "https://www.google.co.uk",
                ".de": "https://www.google.de",
                ".fr": "https://www.google.fr",
                ".au": "https://www.google.com.au"
            }
            
            base_url = google_domains.get(country_code, "https://www.google.com")
            
            # Build search query
            if country_code == ".com":
                query = f"{keyword} site:.com"
            else:
                query = f"{keyword} site:*{country_code}"
            
            search_url = f"{base_url}/search?q={query}&num={max_results}"
            
            logger.info(f"Selenium search: {search_url}")
            
            # Navigate to Google
            self.driver.get(search_url)
            
            # Human-like delay
            time.sleep(random.uniform(2, 4))
            
            # Handle potential cookie/consent dialogs
            self._handle_consent_dialog()
            
            # Wait for results to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.g, div.tF2Cxc"))
                )
            except TimeoutException:
                logger.warning("Search results didn't load within timeout")
                return []
            
            # Extract URLs using multiple selectors
            selectors = [
                "div.g a[href]",
                "div.tF2Cxc a[href]", 
                ".yuRUbf a[href]",
                "h3 a[href]",
                "div.r a[href]"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"Selector '{selector}' found {len(elements)} elements")
                    
                    for element in elements:
                        try:
                            href = element.get_attribute('href')
                            if href and href.startswith('http') and self._is_valid_result_url(href, country_code):
                                urls.append(href)
                                logger.info(f"Found URL: {href}")
                        except Exception as e:
                            logger.debug(f"Error extracting href: {e}")
                            
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
            
            # Remove duplicates
            urls = list(set(urls))
            logger.info(f"Total unique URLs found: {len(urls)}")
            
        except Exception as e:
            logger.error(f"Selenium Google search failed: {e}")
            
        return urls[:max_results]
    
    def _handle_consent_dialog(self):
        """Handle Google's consent/cookie dialogs"""
        try:
            # Common consent button selectors
            consent_selectors = [
                "button[id*='accept']",
                "button[id*='consent']", 
                "div[role='button']:contains('Accept')",
                "#L2AGLb",  # Google's "Accept all" button
                "button:contains('I agree')"
            ]
            
            for selector in consent_selectors:
                try:
                    element = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    element.click()
                    logger.info(f"Clicked consent dialog with selector: {selector}")
                    time.sleep(1)
                    break
                except TimeoutException:
                    continue
                    
        except Exception as e:
            logger.debug(f"No consent dialog found or error handling it: {e}")
    
    def _is_valid_result_url(self, url: str, country_code: str) -> bool:
        """Check if URL is a valid search result"""
        # Exclude Google's own URLs
        if any(domain in url for domain in ['google.com', 'youtube.com', 'wikipedia.org']):
            return False
            
        # Check country code
        if country_code == ".com":
            return ".com" in url
        else:
            return country_code in url
    
    def close(self):
        """Clean up driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium driver closed")
    
    def __del__(self):
        self.close()