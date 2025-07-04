from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException, InvalidSessionIdException
import time
import random
import logging
from urllib.parse import urlparse
from typing import List, Dict

logger = logging.getLogger(__name__)

class SeleniumGoogleSearch:
    """Advanced Google search using Selenium for JavaScript execution"""
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
        self.failed_searches = 0  # Track failed searches to adjust session limits
        self.search_count = 0
        self.max_searches_per_session = 50  # Limit to avoid detection
        self.last_restart_time = time.time()  # Track last restart time
    
    def _should_restart_session(self):
        """Smart logic to determine if session should restart"""
        current_time = time.time()
        time_since_restart = current_time - self.last_restart_time
        
        # Restart conditions:
        # 1. Search count limit reached
        # 2. Too many failures recently
        # 3. Session running for more than 1 hour
        return (
            self.search_count >= self.max_searches_per_session or
            self.failed_searches >= 5 or
            time_since_restart > 3600  # 1 hour
        )
    
    def _adjust_session_limit(self):
        """Adjust based on success rate"""
        if self.failed_searches > 3:
            self.max_searches_per_session = max(10, self.max_searches_per_session - 5)
            logger.info(f"🔽 Reduced session limit to {self.max_searches_per_session}")
        elif self.failed_searches == 0:
            self.max_searches_per_session = min(50, self.max_searches_per_session + 5)
            logger.info(f"🔼 Increased session limit to {self.max_searches_per_session}")
        
    
    def generate_high_entropy_search(self, keyword: str, country_code: str):
        """Generate high-entropy search URLs"""
        
        # Randomize num parameter (Google accepts 10-100)
        num_options = [10, 20, 30, 50, 100]
        num = random.choice(num_options)
        
        # Randomize search operators
        exclude_combinations = [
            ["-wikipedia", "-youtube"],
            ["-wikipedia", "-facebook"],
            ["-youtube", "-twitter"],
            ["-wikipedia"],
            []  # No exclusions sometimes
        ]
        excludes = " ".join(random.choice(exclude_combinations))
        
        # Randomize quote usage (sometimes use quotes, sometimes don't)
        if random.random() > 0.5:
            query = f'"{keyword}" site:{country_code} {excludes}'
        else:
            query = f'{keyword} site:{country_code} {excludes}'
        
        # Add random additional parameters (Google ignores unknown ones)
        random_params = {
            'hl': random.choice(['en', 'en-US', 'en-GB']),
            'gl': random.choice(['US', 'UK', 'CA']),
            'source': random.choice(['hp', 'lnt']),
        }
        
        return query, num, random_params
        
    
    def get_high_entropy_user_agent(self):
        """Generate higher entropy user agents"""
        
        # More diverse browsers and versions
        browsers = [
            "Chrome/120.0.0.0", "Chrome/119.0.0.0", "Chrome/118.0.0.0",
            "Firefox/120.0", "Firefox/119.0", 
            "Safari/537.36", "Edge/120.0.0.0"
        ]
        
        os_systems = [
            "Macintosh; Intel Mac OS X 10_15_7",
            "Windows NT 10.0; Win64; x64", 
            "X11; Linux x86_64",
            "Macintosh; Intel Mac OS X 10_14_6",
            "Windows NT 11.0; Win64; x64"
        ]
        
        # More combinations = higher entropy
        browser = random.choice(browsers)
        os_system = random.choice(os_systems)
        
        return f"Mozilla/5.0 ({os_system}) AppleWebKit/537.36 (KHTML, like Gecko) {browser} Safari/537.36"
    
    def intelligent_delay(self):
        """Human-like delay patterns with higher entropy"""
        
        # Variable delay patterns
        delay_patterns = [
            lambda: random.uniform(2, 4),      # Quick browsing
            lambda: random.uniform(4, 8),      # Normal browsing  
            lambda: random.uniform(8, 15),     # Slow reading
            lambda: random.uniform(15, 30),    # Long pause
        ]
        # Weight toward normal patterns
        pattern_weights = [0.3, 0.4, 0.2, 0.1]
        pattern = random.choices(delay_patterns, weights=pattern_weights)[0]
        
        delay = pattern()
        
        # Add micro-variations (human finger timing)
        delay += random.uniform(-0.5, 0.5)
        
        return max(1.0, delay)  # Minimum 1 second
    
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
        # high entropy user agent function
        high_entropy_user_agent = self.get_high_entropy_user_agent()
        options.add_argument(f'--user-agent={high_entropy_user_agent}')
        
        # User agent rotation
        # user_agents = [
        #     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        #     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        # ]
        
        # options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        try:
            if self.driver:
                self.driver.quit()
            # Initialize the Chrome driver with options
            self.driver = webdriver.Chrome(options=options)
            # Execute script to remove webdriver property
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
                Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})});
            """)
            # self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {'userAgent': random.choice(user_agents)})
            self.search_count = 0
            self.failed_searches = 0  # Reset failed searches
            self.last_restart_time = time.time()  # Reset last restart time
            # self.max_searches_per_session = 50
            logger.info("Selenium driver initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Selenium driver: %s", e)
            raise
    
    def _ensure_valid_session(self):
        """Ensure we have a valid Selenium session"""
        try:
            # Test if session is still valid
            if self.driver:
                self.driver.current_url
            else:
                logger.warning("Driver not initialized, setting up...")
                self.setup_driver()
                return
            
            # Restart driver if too many searches
            # if self.search_count >= self.max_searches_per_session:
            if self._should_restart_session():
                logger.info("🔄 Restarting driver after searches=%d, failures=%d", 
                            self.search_count, self.failed_searches)
                self.setup_driver()
                
        except (InvalidSessionIdException, WebDriverException):
            logger.warning("🔄 Session invalid, restarting driver...")
            self.setup_driver()
    
    def search_google(self, keyword: str, country_code: str, max_results: int = 100) -> List[str]:
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
                    self.failed_searches = 0  # Reset on success
                    self.search_count += 1
                    self._adjust_session_limit()  # Adjust based on success rate
                    logger.info("Search successful: %d URLs found" , len(urls))
                    return urls
                
            except (InvalidSessionIdException, WebDriverException) as e:
                self.failed_searches += 1
                self._adjust_session_limit()  # Adjust session limit on failure
                logger.warning("Session Attempt %d failed: %s", attempt + 1, e)
                if attempt < max_retries -1:
                    self.setup_driver()  # Restart driver on failure
                    time.sleep(random.uniform(3, 6))  # Wait before retrying
                else:
                    logger.error("All %d attempts failed", max_retries)

            except Exception as e:
                logger.error("Unexpected error in search: %s", e)
                break
        
        return urls
    
    def _ensure_driver_ready(self):
        """Ensure driver is initialized and ready to use"""
        if not self.driver:
            logger.warning("Driver not found, initializing...")
            self.setup_driver()
        
        # Test if driver is responsive
        try:
            self.driver.current_url
        except (AttributeError, WebDriverException):
            logger.warning("Driver not responsive, reinitializing...")
            self.setup_driver()
    
    def _perform_search(self, keyword: str, country_code: str, max_results: int) -> List[str]:
        """Perform the actual Google search"""
        try:
            self._ensure_driver_ready()
           
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
            
            # high entopy function
            query, num, random_params = self.generate_high_entropy_search(keyword, country_code)
            base_url =  google_domains.get(country_code, "https://www.google.com")

            # Build search URL with high entropy parameters
            search_url = f"{base_url}/search?q={query}&num={num}"
            # Add random parameters to the URL
            param_strings = "&".join([f"{k}={v}" for k, v in random_params.items()])
            search_url += f"&{param_strings}" 

            logger.info("High entropy Selenium search URL: %s", search_url)

            # base_url = google_domains.get(country_code, "https://www.google.com")
                
            # Build search query
            # if country_code == ".com":
            #     query = f'"{keyword}" site:.com -wikipedia -youtube'
            # else:
            #     query = f'"{keyword}" site:*{country_code} -wikipedia -youtube'
                
            # search_url = f"{base_url}/search?q={query}&num={max_results}"
                
            # logger.info("Selenium search: %s", search_url)
            
            # Ensure driver is ready
            # self._ensure_driver_ready()
            # Navigate to Google
            self.driver.set_page_load_timeout(30)  # Set a timeout for page load
            self.driver.get(search_url)

            # smart delay
            delay = self.intelligent_delay()
            time.sleep(delay)
                
            # # Human-like delay
            # time.sleep(random.uniform(3, 6))
                
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
        except Exception as e:
            logger.error("Selenium Google search failed: %s", e)
        
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
                logger.info("Selector '%s' found %d elements", selector, len(elements))
                    
                for element in elements:
                    try:
                        href = element.get_attribute('href')
                        if href and self._is_valid_result_url(href, country_code):
                            urls.append(href)
                    except Exception as e:
                        logger.debug("Error extracting href: %s", e)
                
                if urls: # If we found any URLs, we can stop checking other selectors
                    break

            except Exception as e:
                logger.debug("Selector %s failed: %s", selector, e)
            
        # Remove duplicates
        return list(dict.fromkeys(urls)) # Preserve order while removing duplicates
        # logger.info("Total unique URLs found: {len(unique_urls)}")
    
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
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
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