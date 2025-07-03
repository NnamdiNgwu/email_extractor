import requests
import time
import random
import threading
from fake_useragent import UserAgent
from typing import Dict
import logging

try:
    from .advanced_anti_bot import AdvancedAntiBot
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False
    logging.warning("Advanced anti-bot features not available. Install: pip install selenium")

logger = logging.getLogger(__name__)

class AntiBot:
    """Handle anti-bot protection and human-like behavior"""
    
    def __init__(self, use_advanced: bool = False, captcha_api_key: str = None):
        self.use_advanced = use_advanced and ADVANCED_FEATURES
        
        if self.use_advanced:
            self.advanced_bot = AdvancedAntiBot(captcha_api_key)
            logger.info("Advanced anti-bot system enabled (CAPTCHA + Proxy rotation)")
        else:
            logger.info("Basic anti-bot system enabled (no CAPTCHA or proxy rotation)")
        # Initialize user agent and session
            self.ua = UserAgent()
            self.session = requests.Session()
            self.request_count = 0
            self.lock = threading.Lock()
            self.country_sessions = {}
    
    def get_session_for_country(self, country_code: str):
        """Get or create a session for specific country"""
        if country_code not in self.country_sessions:
            session = requests.Session()
            
            # Initialize session by visiting the appropriate Google homepage
            homepage_map = {
                ".com": "https://www.google.com",
                ".uk": "https://www.google.co.uk",
                ".cn": "https://www.google.cn",
                ".de": "https://www.google.de", 
                ".fr": "https://www.google.fr",
                ".au": "https://www.google.com.au",
                ".ca": "https://www.google.ca",
                ".in": "https://www.google.co.in",
                ".jp": "https://www.google.co.jp",
                ".br": "https://www.google.com.br",
                ".ru": "https://www.google.ru",
                ".it": "https://www.google.it",
                ".es": "https://www.google.es",
                ".mx": "https://www.google.com.mx",
                ".nl": "https://www.google.nl",
                ".se": "https://www.google.se",
                ".pl": "https://www.google.pl",
                ".tr": "https://www.google.com.tr",
                ".us": "https://www.google.com.us"
            }
            homepage = homepage_map.get(country_code, "https://www.google.com")
            
            try:
                # Visit homepage first to establish session
                logger.info(f"Initializing session for {country_code} via {homepage}")
                session.get(homepage, headers=self.get_headers(country_code), timeout=10)
                time.sleep(random.uniform(1, 3))
                self.country_sessions[country_code] = session
                logger.info(f"Session initialized for {country_code}")
            except Exception as e:
                logger.error(f"Failed to initialize session for {country_code}: {e}")
                self.country_sessions[country_code] = session  # Use it anyway
                
        return self.country_sessions[country_code]
        
    def get_headers(self, country_code: str = None) -> Dict[str, str]:
        """Generate realistic headers with country-specific settings"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        # Country-specific language headers
        language_map = {
            ".com": 'en-US,en;q=0.9',
            ".uk": 'en-GB,en;q=0.9',
            ".de": 'de-DE,de;q=0.9,en;q=0.8',
            ".fr": 'fr-FR,fr;q=0.9,en;q=0.8',
            ".au": 'en-AU,en;q=0.9'
        }
        headers['Accept-Language'] = language_map.get(country_code, 'en-US,en;q=0.9')
            
        return headers
    
    def human_delay(self):
        """Simulate human-like delays"""
        with self.lock:
            self.request_count += 1
            
        # Progressive delay based on request count
        base_delay = random.uniform(2, 5)
        if self.request_count > 10:
            base_delay *= 1.2
        if self.request_count > 30:
            base_delay *= 1.5
        if self.request_count > 50:
            base_delay *= 2
            
        logger.debug(f"Delaying {base_delay:.1f}s (request #{self.request_count})")
        time.sleep(base_delay)
    
    def detect_anti_bot_measures(self, response: requests.Response) -> bool:
        """Detect if we've been flagged as a bot"""
        if not response:
            return True
            
        content = response.text.lower()
        
        # Comprehensive bot detection indicators
        bot_indicators = [
            'captcha', 'recaptcha', 'blocked', 'access denied',
            'rate limit', 'too many requests', 'suspicious activity',
            'cloudflare', 'protection mode', 'security check',
            'please enable javascript', 'bot detected', 'unusual traffic',
            'klicke hier, wenn du nach einigen sekunden',  # German
            'veuillez patienter', 'attendre quelques secondes',  # French
            'javascript is disabled', 'enable cookies',
            'verify you are human', 'prove you are not a robot'
        ]
        
        for indicator in bot_indicators:
            if indicator in content:
                logger.warning(f"Bot detection indicator found: '{indicator}'")
                return True
                
        # Check problematic status codes
        if response.status_code in [403, 429, 503, 402, 406]:
            logger.warning(f"Suspicious status code: {response.status_code}")
            return True
            
        # Check for redirect loops or minimal content
        if len(content) < 1000 and response.status_code == 200:
            logger.warning("Suspiciously small response content")
            return True
            
        return False
    
    def safe_request(self, url: str, country_code: str = None, timeout: int = 15) -> requests.Response:
        """Make a safe request with comprehensive anti-bot measures"""
        self.human_delay()
        
        try:
            # Get appropriate session and headers
            if country_code:
                session = self.get_session_for_country(country_code)
                headers = self.get_headers(country_code)
                
                # Add realistic referer based on search engine
                if 'google' in url:
                    referer_map = {
                        ".com": 'https://www.google.com/',
                        ".uk": 'https://www.google.co.uk/',
                        ".de": 'https://www.google.de/',
                        ".fr": 'https://www.google.fr/',
                        ".au": 'https://www.google.com.au/',
                        ".ca": 'https://www.google.ca/',
                        ".in": 'https://www.google.co.in/',
                        ".jp": 'https://www.google.co.jp/',
                        ".br": 'https://www.google.com.br/',
                        ".ru": 'https://www.google.ru/',
                        ".it": 'https://www.google.it/',
                        ".es": 'https://www.google.es/',
                        ".mx": 'https://www.google.com.mx/',
                        ".nl": 'https://www.google.nl/',
                        ".se": 'https://www.google.se/',
                        ".pl": 'https://www.google.pl/',
                        ".tr": 'https://www.google.com.tr/',
                        ".us": 'https://www.google.com.us/'
                    }
                    headers['Referer'] = referer_map.get(country_code, 'https://www.google.com/')
                    
            else:
                session = self.session
                headers = self.get_headers()
            
            logger.info(f"Making request to {url} [{country_code or 'default'}]")
            
            # Make the request using the appropriate session
            response = session.get(
                url, 
                headers=headers, 
                timeout=timeout, 
                allow_redirects=True,
                verify=True  # Enable SSL verification
            )
            
            # Check for bot detection
            if self.detect_anti_bot_measures(response):
                logger.warning(f"Bot detection triggered for {url}")
                # Exponential backoff
                backoff_time = random.uniform(45, 90)
                logger.info(f"Backing off for {backoff_time:.1f} seconds...")
                time.sleep(backoff_time)
                return None
                
            logger.info(f"✓ Successfully fetched {url} [{response.status_code}]")
            return response
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            return None
    
    def reset_sessions(self):
        """Reset all sessions to clear cookies/state"""
        logger.info("Resetting all sessions...")
        self.country_sessions.clear()
        self.session = requests.Session()
        self.request_count = 0