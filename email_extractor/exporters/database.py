import sqlite3
import csv
from typing import List
import logging
from ..core.models import EmailResult

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handle database operations"""
    
    def __init__(self, db_path: str = "emails.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                domain TEXT NOT NULL,
                source_url TEXT NOT NULL,
                keyword TEXT NOT NULL,
                country_code TEXT NOT NULL,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(email, source_url, keyword)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def save_emails(self, email_results: List[EmailResult]):
        """Save email results to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for result in email_results:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO emails 
                    (email, domain, source_url, keyword, country_code)
                    VALUES (?, ?, ?, ?, ?)
                ''', (result.email, result.domain, result.source_url, 
                     result.keyword, result.country_code))
            except Exception as e:
                logger.error(f"Error saving email {result.email}: {e}")
                
        conn.commit()
        conn.close()
        
    def export_to_csv(self, filename: str = "extracted_emails.csv"):
        """Export emails to CSV file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM emails ORDER BY extracted_at DESC')
        rows = cursor.fetchall()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Email', 'Domain', 'Source URL', 'Keyword', 'Country Code', 'Extracted At'])
            writer.writerows(rows)
            
        conn.close()
        logger.info(f"Exported {len(rows)} emails to {filename}")

    
    def export_country_specific(self, filename: str, country_code: str):
        """Export emails for specific country to CSV file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
            
        cursor.execute('''
            SELECT * FROM emails 
            WHERE country_code = ? 
            ORDER BY extracted_at DESC
        ''', (country_code,))
        rows = cursor.fetchall()
            
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Email', 'Domain', 'Source URL', 'Keyword', 'Country Code', 'Extracted At'])
            writer.writerows(rows)
                
        conn.close()
        logger.info(f"Exported {len(rows)} emails for {country_code} to {filename}")