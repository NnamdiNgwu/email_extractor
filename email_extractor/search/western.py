from .base import BaseSearchEngine
from .selenium_search import SeleniumGoogleSearch
from bs4 import BeautifulSoup
from urllib.parse import quote
import urllib.parse
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class WesternSearchEngine(BaseSearchEngine):
    """Western search engines with hybrid approach"""
    
    def __init__(self, anti_bot):
        super().__init__(anti_bot)
        self.selenium_search = None
        self.search_providers = {
            'google': self._search_google_selenium,
            'bing': self._search_bing,
            'duckduckgo': self._search_duckduckgo
        }
    
    def _get_selenium_search(self):
        """Lazy initialization of Selenium search"""
        if not self.selenium_search:
            self.selenium_search = SeleniumGoogleSearch()
        return self.selenium_search
    
    def search(self, keyword: str, country_code: str, 
               search_operators: Dict = None, 
               max_results: int = 10000,
               providers: List[str] = None) -> List[str]:
        """Enhanced search with Selenium for Google"""
        
        if providers is None:
            providers = ['google', 'duckduckgo', 'bing']  # Google first
            
        all_urls = []
        
        for provider in providers:
            if provider in self.search_providers:
                logger.info(f"Searching with {provider}...")
                try:
                    urls = self.search_providers[provider](
                        keyword, country_code, search_operators or {}, max_results
                    )
                    all_urls.extend(urls)
                    logger.info(f"Found {len(urls)} URLs from {provider}")
                    
                    # If we get good results from Google, might skip others
                    if provider == 'google' and len(urls) >= 10000:
                        logger.info("Got sufficient results from Google, stopping search")
                        break
                        
                except Exception as e:
                    logger.error(f"Search failed for {provider}: {e}")
                    
        # Remove duplicates
        unique_urls = list(dict.fromkeys(all_urls))  # Preserves order
        return unique_urls[:max_results]
    
    def _search_google_selenium(self, keyword: str, country_code: str, 
                              operators: Dict, max_results: int) -> List[str]:
        """Google search using Selenium"""
        try:
            selenium_search = self._get_selenium_search()
            return selenium_search.search_google(keyword, country_code, max_results)
        except Exception as e:
            logger.error(f"Selenium Google search failed: {e}")
            return []
    
    def _search_duckduckgo(self, keyword: str, country_code: str, 
                          operators: Dict, max_results: int) -> List[str]:
        """DuckDuckGo search (fallback)"""
        urls = []
        
        try:
            # Build query
            query = keyword
            if country_code != ".com":
                query += f" site:{country_code}"
                
            search_url = f"https://duckduckgo.com/html/?q={quote(query)}"
            logger.info(f"DuckDuckGo search: {search_url}")
            
            response = self.anti_bot.safe_request(search_url)
            if not response:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # DuckDuckGo result links
            result_links = soup.select('a.result__a')
            
            for link in result_links:
                href = link.get('href', '')
                if href.startswith('http') and self._is_valid_url(href, country_code):
                    urls.append(href)
                    
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            
        return urls[:max_results]
    
    def _search_bing(self, keyword: str, country_code: str, 
                     operators: Dict, max_results: int) -> List[str]:
        """Bing search (fallback)"""
        urls = []
        
        try:
            query = keyword
            if country_code != ".com":
                query += f" site:{country_code}"
                
            search_url = f"https://www.bing.com/search?q={quote(query)}"
            
            response = self.anti_bot.safe_request(search_url)
            if not response:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Bing result selectors
            for selector in ['h2 a[href]', '.b_title a[href]']:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href', '')
                    if href.startswith('http') and self._is_valid_url(href, country_code):
                        urls.append(href)
                        
        except Exception as e:
            logger.error(f"Bing search error: {e}")
            
        return urls[:max_results]
    
    def close_selenium(self):
        """Clean up Selenium resources"""
        if self.selenium_search:
            self.selenium_search.close()
            self.selenium_search = None