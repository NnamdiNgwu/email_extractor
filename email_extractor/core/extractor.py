import re
from typing import Set
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class EmailExtractor:
    """Enhanced email extraction from web content"""
    
    def __init__(self):
        # Standard email regex pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Obfuscated email patterns - handles modern obfuscation
        self.obfuscated_patterns = [
            # contact[at]domain[dot]com
            re.compile(r'\b([A-Za-z0-9._%+-]+)\s*\[at\]\s*([A-Za-z0-9.-]+)\s*\[dot\]\s*([A-Za-z]{2,})\b', re.IGNORECASE),
            # contact(at)domain(dot)com  
            re.compile(r'\b([A-Za-z0-9._%+-]+)\s*\(at\)\s*([A-Za-z0-9.-]+)\s*\(dot\)\s*([A-Za-z]{2,})\b', re.IGNORECASE),
            # contact AT domain DOT com
            re.compile(r'\b([A-Za-z0-9._%+-]+)\s+AT\s+([A-Za-z0-9.-]+)\s+DOT\s+([A-Za-z]{2,})\b', re.IGNORECASE),
            # contact at domain dot com
            re.compile(r'\b([A-Za-z0-9._%+-]+)\s+at\s+([A-Za-z0-9.-]+)\s+dot\s+([A-Za-z]{2,})\b', re.IGNORECASE),
        ]
        
        # Minimal exclude patterns - only obvious fakes
        self.exclude_patterns = [
            r'.*@example\.(com|org|net)',
            r'.*@test\.(com|org|net)', 
            r'.*@domain\.(com|org|net)',
            r'.*@email\.(com|org|net)',
            r'.*@yourcompany\.(com|org|net)',
            r'.*@website\.(com|org|net)',
        ]
    
    def extract_emails(self, content: str, source_url: str) -> Set[str]:
        """Extract emails using multiple detection methods"""
        emails = set()
        
        # Method 1: Standard email detection
        matches = self.email_pattern.findall(content)
        for email in matches:
            email = email.lower().strip()
            if self._should_include_email(email):
                emails.add(email)
        
        # Method 2: Extract from mailto links
        mailto_emails = self._extract_mailto_emails(content)
        emails.update(mailto_emails)
        
        # Method 3: Extract obfuscated emails
        obfuscated_emails = self._extract_obfuscated_emails(content)
        emails.update(obfuscated_emails)
        
        # Method 4: Extract from JavaScript
        js_emails = self._extract_js_emails(content)
        emails.update(js_emails)
        
        if emails:
            logger.info(f"Found {len(emails)} emails from {source_url}")
            
        return emails
    
    def _extract_mailto_emails(self, content: str) -> Set[str]:
        """Extract emails from mailto: links"""
        emails = set()
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.IGNORECASE))
            
            for link in mailto_links:
                href = link.get('href', '')
                email_match = re.search(r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', href, re.IGNORECASE)
                if email_match:
                    email = email_match.group(1).lower()
                    if self._should_include_email(email):
                        emails.add(email)
                        logger.info(f"Found mailto email: {email}")
        except Exception as e:
            logger.debug(f"Error parsing mailto links: {e}")
            
        return emails
    
    def _extract_obfuscated_emails(self, content: str) -> Set[str]:
        """Extract obfuscated emails like contact[at]domain[dot]com"""
        emails = set()
        
        for pattern in self.obfuscated_patterns:
            matches = pattern.findall(content)
            for match in matches:
                if len(match) == 3:  # (local, domain, tld)
                    email = f"{match[0]}@{match[1]}.{match[2]}".lower()
                    if self._should_include_email(email):
                        emails.add(email)
                        logger.info(f"Found obfuscated email: {email}")
        
        return emails
    
    def _extract_js_emails(self, content: str) -> Set[str]:
        """Extract emails from JavaScript code"""
        emails = set()
        
        js_patterns = [
            r'["\']([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})["\']',
            r'email\s*[:=]\s*["\']([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})["\']',
            r'contact\s*[:=]\s*["\']([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})["\']',
        ]
        
        for pattern in js_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for email in matches:
                email = email.lower()
                if self._should_include_email(email):
                    emails.add(email)
                    logger.info(f"Found JS email: {email}")
        
        return emails
    
    def _should_include_email(self, email: str) -> bool:
        """Determine if email should be included"""
        for pattern in self.exclude_patterns:
            if re.match(pattern, email):
                return False
        
        return self._is_valid_email(email)
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format and domain"""
        try:
            if len(email) > 254 or email.count('@') != 1:
                return False
                
            local, domain = email.split('@')
            
            if len(local) == 0 or len(local) > 64:
                return False
                
            if len(domain) == 0 or len(domain) > 253:
                return False
                
            if '.' not in domain or domain.endswith('.'):
                return False
                
            return True
            
        except Exception:
            return False