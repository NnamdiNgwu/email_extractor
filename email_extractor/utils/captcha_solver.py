
import requests
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CaptchaSolver:
    """Handle CAPTCHA solving using 2captcha service"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "YOUR_2CAPTCHA_API_KEY"  # Get from 2captcha.com
        self.base_url = "http://2captcha.com"
        
    def solve_recaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA v2/v3"""
        try:
            # Submit CAPTCHA
            submit_url = f"{self.base_url}/in.php"
            submit_data = {
                'key': self.api_key,
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'pageurl': page_url,
                'json': 1
            }
            
            response = requests.post(submit_url, data=submit_data, timeout=30)
            result = response.json()
            
            if result['status'] != 1:
                logger.error(f"CAPTCHA submit failed: {result.get('error_text')}")
                return None
                
            captcha_id = result['request']
            logger.info(f"CAPTCHA submitted, ID: {captcha_id}")
            
            # Poll for solution
            return self._poll_solution(captcha_id)
            
        except Exception as e:
            logger.error(f"CAPTCHA solving error: {e}")
            return None
    
    def _poll_solution(self, captcha_id: str, max_wait: int = 120) -> Optional[str]:
        """Poll for CAPTCHA solution"""
        get_url = f"{self.base_url}/res.php"
        
        for _ in range(max_wait // 5):
            try:
                response = requests.get(get_url, params={
                    'key': self.api_key,
                    'action': 'get',
                    'id': captcha_id,
                    'json': 1
                }, timeout=10)
                
                result = response.json()
                
                if result['status'] == 1:
                    logger.info("CAPTCHA solved successfully")
                    return result['request']
                elif result['error_text'] == 'CAPCHA_NOT_READY':
                    time.sleep(5)
                    continue
                else:
                    logger.error(f"CAPTCHA solve failed: {result.get('error_text')}")
                    return None
                    
            except Exception as e:
                logger.error(f"Error polling CAPTCHA solution: {e}")
                time.sleep(5)
                
        logger.error("CAPTCHA solving timeout")
        return None
