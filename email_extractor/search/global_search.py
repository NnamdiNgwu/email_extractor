from .western import WesternSearchEngine
from .chinese import ChineseSearchEngine
from typing import List
import logging

logger = logging.getLogger(__name__)

class GlobalSearchEngine:
    """Global search engine with region-specific providers"""
    
    def __init__(self, anti_bot):
        self.anti_bot = anti_bot
        self.western_engine = WesternSearchEngine(anti_bot)
        self.chinese_engine = ChineseSearchEngine(anti_bot)
    
    def search_by_region(self, keyword: str, country_code: str, 
                        max_results: int = 10000,
                        search_operators: dict = None) -> List[str]:
        """Search using region-appropriate search engines"""
        
        if country_code == ".cn" or "china" in keyword.lower():
            # Use Chinese search engines for China
            providers = ['baidu', 'sogou', '360', 'bing_china']
            logger.info("Using Chinese search engines for China region")
            return self.chinese_engine.search(keyword, country_code, max_results, providers)
            
        elif country_code in [".ru", ".by", ".kz"]:
            # Use Yandex for Russian-speaking regions
            providers = ['yandex', 'google', 'bing']
            logger.info("Using Yandex for Russian-speaking regions")
            return self.western_engine.search(keyword, country_code, search_operators, max_results, providers)
            
        else:
            # Use Western search engines for other regions
            providers = ['google', 'bing', 'duckduckgo']
            logger.info("Using Western search engines")
            return self.western_engine.search(keyword, country_code, search_operators, max_results, providers)