from abc import ABC, abstractmethod
from typing import List, Dict
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class BaseSearchEngine(ABC):
    """Base class for search engines"""
    
    def __init__(self, anti_bot):
        self.anti_bot = anti_bot
        
    @abstractmethod
    def search(self, keyword: str, country_code: str, max_results: int = 10000) -> List[str]:
        """Search for URLs"""
        pass

    def _is_valid_url(self, url: str, country_code: str) -> bool:
        """Validate URL and check if it matches country code"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check if domain ends with country code
            if country_code.startswith('.'):
                return domain.endswith(country_code)
            else:
                return country_code in domain
                
        except Exception as e:
            logger.debug(f"URL validation error for {url}: {e}")
            return False
        
    # def _is_valid_url(self, url: str, country_code: str) -> bool:
    #     """Validate URL and check if it matches country code"""
    #     try:
    #         from urllib.parse import urlparse
    #         parsed = urlparse(url)
    #         domain = parsed.netloc.lower()
            
    #         # Check if domain ends with country code
    #         if country_code.startswith('.'):
    #             return domain.endswith(country_code)
    #         else:
    #             return country_code in domain
                
    #     except:
    #         return False