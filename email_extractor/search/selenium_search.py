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
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')  # Run in headless mode for better performance
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # Faster loading
        # options.add_argument('--disable-javascript')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Realistic window size
        options.add_argument('--window-size=1366,768')
        
        # User agent rotation
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            # Execute script to remove webdriver property
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
                Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})});
            """)
            # self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {'userAgent': random.choice(user_agents)})
            self.search_count = 0
            logger.info("Selenium driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium driver: {e}")
            raise
    
    def _ensure_valid_session(self):
        """Ensure we have a valid Selenium session"""
        try:
            # Test if session is still valid
            self.driver.current_url
            
            # Restart driver if too many searches
            if self.search_count >= self.max_searches_per_session:
                logger.info(f"🔄 Restarting driver after {self.search_count} searches")
                self.setup_driver()
                
        except (InvalidSessionIdException, WebDriverException):
            logger.warning("🔄 Session invalid, restarting driver...")
            self.setup_driver()
    
    def search_google(self, keyword: str, country_code: str, max_results: int = 10000) -> List[str]:
        """Search Google with JavaScript execution"""

        # Ensure we have a valid session before starting a search
        self._ensure_valid_session()
        urls = []
        max_retries = 3

        for attempt in range(max_retries):
            try:
                # Perform the search
                urls = self._perform_search(keyword, country_code, max_results)
                if urls:
                    self.search_count += 1
                    logger.info(f"Search successful: {len(urls)} URLs found")
                    return urls
            except (InvalidSessionIdException, WebDriverException) as e:
                logger.warning(f"Session Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries -1:
                    self.setup_driver()  # Restart driver on failure
                    time.sleep(random.uniform(3, 6))  # Wait before retrying
                else:
                    logger.error(f"All {max_retries} attempts failed")
            except Exception as e:
                logger.error(f" Unexpected error in searchn {e}")
                break
        
        return urls
    
    def _perform_search(self, keyword: str, country_code: str, max_results: int) -> List[str]:
        """Perform the actual Google search"""
        # Build country-specific Google URL
        google_domains = {
                ".com": "https://www.google.com",
                ".uk": "https://www.google.co.uk",
                ".de": "https://www.google.de",
                ".fr": "https://www.google.fr",
                ".au": "https://www.google.com.au",
                ".ca": "https://www.google.ca",
                ".in": "https://www.google.co.in",
                ".jp": "https://www.google.co.jp",
                ".br": "https://www.google.com.br",
                ".it": "https://www.google.it",
                ".es": "https://www.google.es",
                ".ru": "https://www.google.ru",
                ".nl": "https://www.google.nl",
                ".pl": "https://www.google.pl",
                ".se": "https://www.google.se",
                ".no": "https://www.google.no",
                ".fi": "https://www.google.fi",
                ".dk": "https://www.google.dk",
                ".tr": "https://www.google.com.tr",
                ".mx": "https://www.google.com.mx",
                ".ar": "https://www.google.com.ar",
                ".ch": "https://www.google.ch",
                ".be": "https://www.google.be",
                ".at": "https://www.google.at",
                ".cz": "https://www.google.cz",
                ".hu": "https://www.google.hu",
                ".gr": "https://www.google.gr",
                ".cn": "https://www.google.cn",
                ".kr": "https://www.google.co.kr",
        }
            
        base_url = google_domains.get(country_code, "https://www.google.com")
            
        # Build search query
        if country_code == ".com":
            query = f'"{keyword}" site:.com -wikipedia -youtube'
        else:
            query = f'"{keyword}" site:*{country_code} -wikipedia -youtube'
            
            search_url = f"{base_url}/search?q={query}&num={max_results}"
            
            logger.info(f"Selenium search: {search_url}")
            
            # Navigate to Google
            self.driver.set_page_load_timeout(30)  # Set a timeout for page load
            self.driver.get(search_url)
            
            # Human-like delay
            time.sleep(random.uniform(3, 6))
            
            # Handle potential cookie/consent dialogs
            self._handle_consent_dialog()
            
            # Wait for results to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.g")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.tF2Cxc")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".yuRUbf"))
                    )
                )
            except TimeoutException:
                logger.warning("Search results didn't load within timeout")
                return []
            
            # Extract URLs
            return self._extract_urls(country_code)
        
    def _extract_urls(self, country_code: str) -> List[str]:
        """Extract URLs from the search results"""
        urls = []

        # Extract URLs using multiple selectors
        selectors = [ 
            "div.yuRUbf a[href]",# Modern Google
            "div.g a[href]", 
            "div.tF2Cxc a[href]", 
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
                
                if urls: # If we found any URLs, we can stop checking other selectors
                    break

            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
            
        # Remove duplicates
        unique_urls = list(dict.fromkeys(urls)) # Preserve order while removing duplicates
        logger.info(f"Total unique URLs found: {len(unique_urls)}")
        
        return unique_urls
        # except Exception as e:
        #     logger.error(f"Selenium Google search failed: {e}")
            
        # return urls[:max_results]
    
    def _handle_consent_dialog(self):
        """Handle Google's consent/cookie dialogs"""
        try:
            # Common consent button selectors
            consent_selectors = [
                "#L2AGLb",  # Google's "Accept all" button
                "button[aria-label*='Accept']",
                "button:contains('Accept')",
                "button[id*='accept']",
                "button[id*='consent']", 
                "div[role='button']:contains('Accept')",
                "button:contains('I agree')"
            ]
            
            for selector in consent_selectors:
                try:
                    element = WebDriverWait(self.driver, 3).until(
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
        if not url or not url.startswith('http'):
            return False
        # Exclude Google's own URLs
        excluded = ['google.com', 'youtube.com', 'wikipedia.org', 'facebook.com', 'twitter.com']
        if any(domain in url for domain in excluded):
            return False
            
        # Check country code
        if country_code == ".com":
            return ".com" in url
        else:
            return country_code in url
    
    def close(self):
        """Clean up driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Selenium driver closed successfully")
            except Exception as e:
                logger.error(f"Error closing Selenium driver: {e}")
            finally:
                self.driver = None
    
    def __del__(self):
        self.close()