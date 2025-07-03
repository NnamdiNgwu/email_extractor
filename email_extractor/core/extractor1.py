import re
from typing import Set
import logging

logger = logging.getLogger(__name__)

class EmailExtractor:
    """Extract emails from web content"""
    
    def __init__(self):
        # Comprehensive email regex pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Patterns to exclude (common false positives)
        self.exclude_patterns = [
            r'.*@example\.(com|org|net)',
            r'.*@test\.(com|org|net)',
            r'.*@domain\.(com|org|net)',
            r'.*@email\.(com|org|net)',
            r'.*@yourcompany\.(com|org|net)',
            r'.*@website\.(com|org|net)',
        ]
    
    def extract_emails(self, content: str, source_url: str) -> Set[str]:
        """Extract valid emails from content"""
        emails = set()
        
        # Find all email matches
        matches = self.email_pattern.findall(content)
        
        for email in matches:
            email = email.lower().strip()
            
            # Skip if matches exclude patterns
            should_exclude = False
            for pattern in self.exclude_patterns:
                if re.match(pattern, email):
                    should_exclude = True
                    break
                    
            if not should_exclude and self._is_valid_email(email):
                emails.add(email)
                
        return emails
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format and domain"""
        try:
            # Basic validation
            if len(email) > 254 or email.count('@') != 1:
                return False
                
            local, domain = email.split('@')
            
            # Local part validation
            if len(local) == 0 or len(local) > 64:
                return False
                
            # Domain validation
            if len(domain) == 0 or len(domain) > 253:
                return False
                
            # Check for valid TLD
            if '.' not in domain or domain.endswith('.'):
                return False
                
            return True
            
        except Exception:
            return False