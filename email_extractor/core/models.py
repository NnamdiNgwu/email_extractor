from dataclasses import dataclass
from typing import List, Set, Dict

@dataclass
class EmailResult:
    email: str
    domain: str
    source_url: str
    keyword: str
    country_code: str
    extracted_at: str