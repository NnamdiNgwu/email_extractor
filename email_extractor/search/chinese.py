from .base import BaseSearchEngine
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse
from typing import List
import logging

logger = logging.getLogger(__name__)

class ChineseSearchEngine(BaseSearchEngine):
    """Chinese search engines (Baidu, Sogou, 360, Bing China)"""
    
    def __init__(self, anti_bot):
        super().__init__(anti_bot)
        self.search_providers = {
            'baidu': self._search_baidu,
            'sogou': self._search_sogou,
            '360': self._search_360,
            'bing_china': self._search_bing_china
        }
        
    def search(self, keyword: str, country_code: str = ".cn", 
               max_results: int = 50,
               providers: List[str] = None) -> List[str]:
        """Search using Chinese search engines"""
        
        if providers is None:
            providers = ['baidu', 'sogou', '360']
            
        all_urls = []
        
        for provider in providers:
            if provider in self.search_providers:
                logger.info(f"Searching with Chinese engine: {provider}...")
                try:
                    urls = self.search_providers[provider](keyword, country_code, max_results)
                    all_urls.extend(urls)
                    logger.info(f"Found {len(urls)} URLs from {provider}")
                except Exception as e:
                    logger.error(f"Chinese search failed for {provider}: {e}")
                    
        # Remove duplicates
        unique_urls = list(set(all_urls))
        return unique_urls[:max_results]
    
    def _search_baidu(self, keyword: str, country_code: str, max_results: int) -> List[str]:
        """Baidu search implementation"""
        urls = []
        
        query = f"{keyword} site:{country_code}"
        
        for pn in range(0, min(max_results, 100), 10):
            search_url = f"https://www.baidu.com/s?wd={quote(query)}&pn={pn}"
            
            response = self.anti_bot.safe_request(search_url)
            if not response:
                continue
                
            page_urls = self._parse_baidu_results(response.text, country_code)
            urls.extend(page_urls)
            
            if len(urls) >= max_results:
                break
                
        return urls[:max_results]
    
    def _search_sogou(self, keyword: str, country_code: str, max_results: int) -> List[str]:
        """Sogou search implementation"""
        urls = []
        
        query = f"{keyword} site:{country_code}"
        
        for page in range(1, min(max_results//10 + 1, 10)):
            search_url = f"https://www.sogou.com/web?query={quote(query)}&page={page}"
            
            response = self.anti_bot.safe_request(search_url)
            if not response:
                continue
                
            page_urls = self._parse_sogou_results(response.text, country_code)
            urls.extend(page_urls)
            
            if len(urls) >= max_results:
                break
                
        return urls[:max_results]
    
    def _search_360(self, keyword: str, country_code: str, max_results: int) -> List[str]:
        """360 Search implementation"""
        urls = []
        
        query = f"{keyword} site:{country_code}"
        
        for pn in range(1, min(max_results//10 + 1, 10)):
            search_url = f"https://www.so.com/s?q={quote(query)}&pn={pn}"
            
            response = self.anti_bot.safe_request(search_url)
            if not response:
                continue
                
            page_urls = self._parse_360_results(response.text, country_code)
            urls.extend(page_urls)
            
            if len(urls) >= max_results:
                break
                
        return urls[:max_results]
    
    def _search_bing_china(self, keyword: str, country_code: str, max_results: int) -> List[str]:
        """Bing China search implementation"""
        urls = []
        
        query = f"{keyword} site:{country_code}"
        
        for first in range(1, min(max_results, 100), 10):
            search_url = f"https://cn.bing.com/search?q={quote(query)}&first={first}"
            
            response = self.anti_bot.safe_request(search_url)
            if not response:
                continue
                
            page_urls = self._parse_bing_china_results(response.text, country_code)
            urls.extend(page_urls)
            
            if len(urls) >= max_results:
                break
                
        return urls[:max_results]
    
    def _parse_baidu_results(self, html: str, country_code: str) -> List[str]:
        """Parse Baidu search results"""
        urls = []
        soup = BeautifulSoup(html, 'html.parser')
        
        selectors = ['h3.t a', 'a[data-click]', '.result h3 a']
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                
                if 'baidu.com/link?' in href:
                    try:
                        response = self.anti_bot.safe_request(href)
                        if response and response.url != href:
                            actual_url = response.url
                            if self._is_valid_chinese_url(actual_url, country_code):
                                urls.append(actual_url)
                    except:
                        continue
                elif href.startswith('http') and self._is_valid_chinese_url(href, country_code):
                    urls.append(href)
                    
        return urls
    
    def _parse_sogou_results(self, html: str, country_code: str) -> List[str]:
        """Parse Sogou search results"""
        urls = []
        soup = BeautifulSoup(html, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http') and self._is_valid_chinese_url(href, country_code):
                urls.append(href)
                
        return urls
    
    def _parse_360_results(self, html: str, country_code: str) -> List[str]:
        """Parse 360 Search results"""
        urls = []
        soup = BeautifulSoup(html, 'html.parser')
        
        for link in soup.find_all('a', class_='res-title'):
            href = link.get('href', '')
            if href.startswith('http') and self._is_valid_chinese_url(href, country_code):
                urls.append(href)
                
        return urls
    
    def _parse_bing_china_results(self, html: str, country_code: str) -> List[str]:
        """Parse Bing China search results"""
        urls = []
        soup = BeautifulSoup(html, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http') and self._is_valid_chinese_url(href, country_code):
                urls.append(href)
                
        return urls
    
    def _is_valid_chinese_url(self, url: str, country_code: str) -> bool:
        """Validate Chinese URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if country_code == ".cn":
                return domain.endswith('.cn') or any(
                    chinese_tld in domain for chinese_tld in ['.com.cn', '.net.cn', '.org.cn']
                )
            
            return country_code in domain
            
        except:
            return False