import requests
import random
import time
import logging
from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class ProxyManager:
    """Manage proxy rotation and IP switching """
    def __init__(self):
        self.working_proxies = []
        self.failed_proxies = []
        self.current_proxy = None
        self.proxy_usage_count = {}
    
    def load_proxies(self, proxy_sources: List[str] = None) -> None:
        """Load proxies from varoius sources """
        if proxy_sources is None:
            proxy_sources = [
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt"
            ]
        
        all_proxies = []

        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                proxies = response.text.strip().split('\n')
                all_proxies.extend([proxy.strip() for proxy in proxies if ':' in proxy])
                logger.info(f"Loaded {len(proxies)} proxies from {source}")
            except requests.RequestException as e:
                logger.error(f"Failed to load proxies from {source}: {e}")

        # Test proxies in parallel
        self._test_proxies(all_proxies)
        logger.info(f"Found {len(self.working_proxies)} working proxies out of {len(all_proxies)} tested")

    def _test_proxies(self, proxies: List[str], max_workers: int = 50) -> None:
        """Test proxies in parallel"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._test_proxy, proxy): proxy for proxy in proxies[:200]
            }

            for future in as_completed(futures):
                proxy = futures[future]
                try:
                    if future.result(timeout=10):
                        self.working_proxies.append(proxy)
                        self.proxy_usage_count[proxy] = 0
                    else:
                        self.failed_proxies.append(proxy)
                except Exception as e:
                    logger.error(f"Error testing proxy {proxy}: {e}")
    
    def _test_proxy(self, proxy: str) -> bool:
        """Test if a proxy is working"""
        try:
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }

            response = requests.get(
                "https://httpbin.org/ip",
                proxies=proxy_dict,
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
        
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get next available proxy"""
        if not self.working_proxies:
            logger.error("No working proxies available")
            return None
        
        # Remove overused proxies
        self.working_proxies = [p for p in self.working_proxies 
                              if self.proxy_usage_count.get(p, 0) < 10]
        
        if not self.working_proxies:
            logger.warning("All proxies exhausted, reloading...")
            self.load_proxies()
            return self.get_proxy()
        
        # Select random proxy
        proxy = random.choice(self.working_proxies)
        self.current_proxy = proxy
        self.proxy_usage_count[proxy] += 1
        
        return {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
    
    def mark_proxy_failed(self, proxy: str) -> None:
        """Mark proxy as failed"""
        if proxy in self.working_proxies:
            self.working_proxies.remove(proxy)
            self.failed_proxies.add(proxy)
            logger.info(f"Marked proxy as failed: {proxy}")
    
    def rotate_proxy(self) -> Optional[Dict[str, str]]:
        """Force proxy rotation"""
        if self.current_proxy:
            logger.info(f"Rotating from proxy: {self.current_proxy}")
        
        return self.get_proxy()