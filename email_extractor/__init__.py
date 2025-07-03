"""
Email Extractor - A comprehensive email extraction tool with anti-bot protection
"""

from .spider import EmailSpider
from .core.models import EmailResult
from .core.filters import DomainFilter
from .core.extractor import EmailExtractor
from .utils.anti_bot import AntiBot
from .search.global_search import GlobalSearchEngine
from .exporters.database import DatabaseManager

__version__ = "1.0.0"
__all__ = [
    'EmailSpider',
    'EmailResult', 
    'DomainFilter',
    'EmailExtractor',
    'AntiBot',
    'GlobalSearchEngine',
    'DatabaseManager'
]