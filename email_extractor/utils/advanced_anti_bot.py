import requests
import time
import random
import logging
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .captcha_solver import CaptchaSolver
from .proxy_manager import ProxyManager

logger = logging.getLogger(__name__)

class AdvancedAntiBot:
    """Advanced anti-bot system with CAPTCHA solving and proxy rotation"""
    
    def __init__(self, captcha_api_key: str = None):
        self.captcha_solver = CaptchaSolver(captcha_api_key)
        self.proxy_manager = ProxyManager()
        self.session = requests.Session()
        self.driver = None
        
        # Load proxies
        self.proxy_manager.load_proxies()
        
        # Rotate to first proxy
        self._rotate_proxy()
    
    def _rotate_proxy(self) -> bool:
        """Rotate to new proxy"""
        proxy = self.proxy_manager.rotate_proxy()
        if proxy:
            self.session.proxies.update(proxy)
            logger.info(f"Rotated to proxy: {proxy['http']}")
            return True
        return False

    def safe_request_with_captcha(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make request with CAPTCHA solving and proxy rotation"""
        
        for attempt in range(max_retries):
            try:
                # Make request
                response = self.session.get(url, timeout=15)
                
                # Check for CAPTCHA
                if self._has_captcha(response):
                    logger.info(f"CAPTCHA detected on {url}")
                    solved_response = self._solve_captcha_challenge(url, response)
                    if solved_response:
                        return solved_response
                    else:
                        # CAPTCHA failed, rotate proxy and retry
                        if not self._rotate_proxy():
                            logger.error("No more proxies available")
                            return None
                        continue
                
                # Check for IP ban
                elif self._is_ip_banned(response):
                    logger.warning(f"IP banned detected, rotating proxy")
                    if not self._rotate_proxy():
                        logger.error("No more proxies available")
                        return None
                    continue
                
                # Success
                return response
            
            except requests.exceptions.ProxyError:
                logger.warning("Proxy failed, rotating...")
                self.proxy_manager.mark_proxy_failed(self.proxy_manager.current_proxy)
                if not self._rotate_proxy():
                    logger.error("No more proxies available")
                    return None
                    
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                time.sleep(random.uniform(2, 5))
        
        return None
    
    def _has_captcha(self, response: requests.Response) -> bool:
        """Detect if response contains CAPTCHA"""
        captcha_indicators = [
            'recaptcha', 'captcha', 'hcaptcha',
            'verify you are human', 'prove you are not a robot',
            'security check', 'unusual traffic'
        ]
        
        content_lower = response.text.lower()
        return any(indicator in content_lower for indicator in captcha_indicators)
    
    def _is_ip_banned(self, response: requests.Response) -> bool:
        """Detect IP ban"""
        ban_indicators = [
            'access denied', 'blocked', 'forbidden',
            'rate limit', 'too many requests',
            response.status_code in [403, 429, 503]
        ]
        
        content_lower = response.text.lower()
        return (response.status_code in [403, 429, 503] or 
                any(indicator in content_lower for indicator in ban_indicators if isinstance(indicator, str)))
    

    def _solve_captcha_challenge(self, url: str, response: requests.Response) -> Optional[requests.Response]:
        """Solve CAPTCHA challenge using Selenium + 2captcha"""
        try:
            # Setup Selenium with proxy
            self._setup_selenium_with_proxy()
            
            self.driver.get(url)
            time.sleep(3)
            
            # Find reCAPTCHA site key
            site_key = self._extract_recaptcha_site_key()
            if not site_key:
                logger.error("Could not find reCAPTCHA site key")
                return None
            
            # Solve CAPTCHA
            solution = self.captcha_solver.solve_recaptcha(site_key, url)
            if not solution:
                logger.error("CAPTCHA solving failed")
                return None
            
            # Inject solution
            self.driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{solution}";')
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"], button[type="submit"]')
            submit_button.click()
            
            time.sleep(5)
            
            # Get final page content
            final_response = requests.Response()
            final_response._content = self.driver.page_source.encode('utf-8')
            final_response.status_code = 200
            
            return final_response
            
        except Exception as e:
            logger.error(f"CAPTCHA challenge failed: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def _setup_selenium_with_proxy(self) -> None:
        """Setup Selenium WebDriver with current proxy"""
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Add proxy
        if self.proxy_manager.current_proxy:
            options.add_argument(f'--proxy-server=http://{self.proxy_manager.current_proxy}')
        
        self.driver = webdriver.Chrome(options=options)
    
    def _extract_recaptcha_site_key(self) -> Optional[str]:
        """Extract reCAPTCHA site key from page"""
        try:
            recaptcha_element = self.driver.find_element(By.CSS_SELECTOR, '[data-sitekey]')
            return recaptcha_element.get_attribute('data-sitekey')
        except:
            return None
    
    
    