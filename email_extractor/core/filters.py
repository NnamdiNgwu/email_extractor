import logging
from urllib.parse import urlparse
from typing import Set

logger = logging.getLogger(__name__)

class DomainFilter:
    """Filter out government, military, and educational domains"""
    
    def __init__(self):
        self.excluded_domains = {
            # US domains
            '.gov', '.mil', '.edu',
            # UK domains
            '.gov.uk', '.mod.uk', '.ac.uk',
            # German domains
            '.bund.de', '.bundeswehr.de', '.uni-',
            # French domains
            '.gouv.fr', '.defense.gouv.fr', '.univ-',
            # Canadian domains
            '.gc.ca', '.forces.gc.ca',
            # Australian domains
            '.gov.au', '.defence.gov.au', '.edu.au',
            # Chinese domains
            '.gov.cn', '.mil.cn', '.edu.cn',
        }
        
        self.excluded_keywords = {
            'government', 'military', 'defense', 'defence', 'army', 'navy', 
            'airforce', 'police', 'sheriff', 'courthouse', 'municipality', 
            'city-hall', 'federal', 'state-gov', 'county-gov', 'university',
            'college', 'school', 'academic'
        }
    
    def is_allowed_domain(self, url: str) -> bool:
        """Check if domain is allowed for email extraction"""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Check for excluded domain patterns
            for excluded in self.excluded_domains:
                if excluded in domain:
                    logger.info(f"Excluded domain: {domain} (pattern: {excluded})")
                    return False
                    
            # Check for excluded keywords in domain
            for keyword in self.excluded_keywords:
                if keyword in domain:
                    logger.info(f"Excluded domain: {domain} (keyword: {keyword})")
                    return False
                    
            return True
        except Exception as e:
            logger.error(f"Error checking domain {url}: {e}")
            return False