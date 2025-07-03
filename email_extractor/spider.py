import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import logging

from .core.models import EmailResult
from .core.filters import DomainFilter
from .core.extractor import EmailExtractor
from .utils.anti_bot import AntiBot
from .search.global_search import GlobalSearchEngine
from .exporters.database import DatabaseManager

logger = logging.getLogger(__name__)

class EmailSpider:
    """Main email extraction spider"""
    
    def __init__(self, max_workers: int = 3):
        self.anti_bot = AntiBot()
        self.domain_filter = DomainFilter()
        self.email_extractor = EmailExtractor()
        self.search_engine = GlobalSearchEngine(self.anti_bot)
        self.db_manager = DatabaseManager()
        self.max_workers = max_workers
    
    def __del__(self):
        """Clean up resources"""
        if hasattr(self.search_engine, 'close_selenium'):
            self.search_engine.close_selenium()
        
    def crawl(self, keywords: List[str], country_codes: List[str], 
              search_config: Dict = None) -> List[EmailResult]:
        """Main crawling method"""
        
        if search_config is None:
            search_config = {
                'max_urls_per_keyword': 30,
                'operators': {
                    'exclude_words': ['wikipedia', 'youtube', 'facebook', 'twitter', 'linkedin'],
                    'include_words': ['contact', 'about', 'email', 'support', 'info', 'sales', 'service'],
                    'language': 'en'

                }
            }
        
        try:
        
            all_results = []

            for country_code in country_codes:
                logger.info(f"=== Starting extraction for country: {country_code} ===")
                country_results = []
            
                for keyword in keywords:
                    # for country_code in country_codes:
                    logger.info(f"Processing keyword '{keyword}' for country '{country_code}'")
                        
                    # Search for URLs
                    urls = self.search_engine.search_by_region(
                        keyword=keyword,
                        country_code=country_code,
                        max_results=search_config.get('max_urls_per_keyword', 30),
                        search_operators=search_config.get('operators', {})
                    )
                        
                    # Filter allowed URLs
                    allowed_urls = [url for url in urls if self.domain_filter.is_allowed_domain(url)]
                        
                    logger.info(f"Found {len(urls)} total URLs, {len(allowed_urls)} allowed after filtering")
                    logger.info(f"Found {len(urls)} URLs for '{keyword}' in {country_code}")
                        
                        
                    # Extract emails
                    results = self._extract_from_urls(allowed_urls, keyword, country_code)
                    country_results.extend(results)
                    # all_results.extend(results)
                        
                    # Save results
                    if results:
                        self.db_manager.save_emails(results)
                        logger.info(f"Saved {len(results)} email results")
                        
                    # Add delay between keywords for the same country
                    time.sleep(random.uniform(5, 10))
                    
                    all_results.extend(country_results)
                    logger.info(f"=== Completed {country_code}: Found {len(country_results)} total emails ===")
                
                    # Export country-specific results
                    country_filename = f"emails_{country_code.replace('.', '')}.csv"
                    self.db_manager.export_country_specific(country_filename, country_code)

                    # longer delay betweeen countries
                    if country_code != country_codes[-1]:
                        delay = random.uniform(30, 60)
                        logger.info(f"Waiting {delay:.2f} seconds before next country...")
                        time.sleep(delay)
            return all_results
        except Exception as e:
            logger.error(f"Error during crawling: {e}")
            raise e
    
        finally:
            if hasattr(self.search_engine, 'close_selenium'):
                self.search_engine.close_selenium()
                logger.info("Crawling completed. All resources cleaned up.")
    
    def _extract_from_urls(self, urls: List[str], keyword: str, country_code: str) -> List[EmailResult]:
        """Extract emails from URLs with threading"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self._process_url, url, keyword, country_code): url 
                for url in urls
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    url_results = future.result()
                    if url_results:
                        results.extend(url_results)
                        logger.info(f"Extracted {len(url_results)} emails from {url}")
                except Exception as e:
                    logger.error(f"Error processing {url}: {e}")
                    
        return results
    
    def _process_url(self, url: str, keyword: str, country_code: str) -> List[EmailResult]:
        """Process a single URL and extract emails"""
        try:
            response = self.anti_bot.safe_request(url)
            if not response:
                return []
                
            emails = self.email_extractor.extract_emails(response.text, url)
            
            results = []
            for email in emails:
                domain = email.split('@')[1]
                result = EmailResult(
                    email=email,
                    domain=domain,
                    source_url=url,
                    keyword=keyword,
                    country_code=country_code,
                    extracted_at=time.strftime('%Y-%m-%d %H:%M:%S')
                )
                results.append(result)
                
            return results
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            return []