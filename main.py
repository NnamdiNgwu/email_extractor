#!/usr/bin/env python3
"""
Main script for email extraction
"""

import logging
import os
from email_extractor import EmailSpider

try:
    if not os.path.exists("logs"):
        os.makedirs("logs")
except OSError as e:
    print(f"Error creating logs directory: {e}")
    exit(1)
# os.mkdir("logs")  # Ensure logs directory exists

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/email_extractor.log"),
        logging.StreamHandler()
    ])
logger = logging.getLogger(__name__)

def main():
    """Main extraction function"""
    # Initialize spider
    spider = EmailSpider(max_workers=1)
    
    # Configuration
    general_keywords = [" Renewable Energy Equipment", "agricultural equipment", "farm machinery","agro machinery",
               "food processing", "mining", "wood processing", "wood products",
                "furniture", "construction materials", "building materials",
                "construction equipment", "mining equipment", "gold mining",
                "Mining company", "toys", "children's products", 
                "baby products", "educational toys", "electronics", 
                "consumer electronics", "home appliances", "kitchen appliances",
                "smart home devices"]
    
     # Marine and Industrial Equipment Keywords
    marine_and_industrial_keywords = [
        # Anchoring and Mooring Equipment
        "marine anchors", "mushroom anchors", "navy anchors", "vinyl covered anchors",
        "marine cable", "anchor chains", "flagpole cleats", "pad eyes", "marine bollards",
        "marine chocks", "tie back systems",
        
        # Rigging and Lifting Equipment  
        "hand swage tensioners", "marine hooks", "rigging clips", "wire rope",
        "marine swivels", "rigging links", "rigging rings", "bottom blocks",
        "marine capstans", "chain hoists", "jib cranes", "power heads",
        "floor cranes", "marine sheaves", "strap hoists", "tractor drives",
        "trolleys carriers", "marine winches", "wire rope hoists",
        
        # Marine Hardware and Fittings
        "automatic drain plugs", "spreader boots", "marine gaskets",
        "packing gaskets", "ramp door gaskets", "flax gaskets", "graphite PTFE gaskets",
        "marine seals", "marine shims", "marine O-rings", "marine bearings",
        "craft split bearings", "split spherical bearings", "lead bronze bearings",
        "bi-metal bearings", "tri-metal bearings",
        
        # Marine Structures and Safety
        "marine fender systems", "marine bolts", "marine spikes", "tie rods",
        "marine ladders", "marine railings", "marine platforms", "marine stairways",
        "marine catwalks", "crossover bridges", "marine gangways", "marine ramps",
        "wave screens",
        
        # Marine Cases and Storage
        "roto-molded polyethylene cases", "marine equipment racks",
        "marine storage systems",
        
        # Marine Electronics and Communications
        "low noise amplifiers", "marine converters", "marine receivers",
        "marine communications equipment", "marine electronics",
        
        # Marine Engine and Systems
        "utility pads", "vibration reducing pads", "marine heat exchangers",
        "marine flanges", "marine hose", "water outlets", "expansion tanks",
        "marine end plates", "marine caps", "oil coolers",
        
        # General Marine Equipment
        "marine equipment", "boat equipment", "ship equipment", "marine supplies",
        "marine hardware", "marine parts", "marine accessories",
        "commercial marine equipment", "industrial marine equipment"
    ]
    keywords = general_keywords + marine_and_industrial_keywords
    country_codes = [".com",".us", ".uk", ".fr", ".au", ".ca", ".de", ".it", ".es", ".nl", ".in", ".jp", ".br", ".ru", ".mx", ".kr", ".se", ".ch", ".no", ".fi", ".dk"]
    
    # Search configuration
    search_config = {
        'max_urls_per_keyword': 30,
        'operators': {
            'exclude_words': ['wikipedia', 'youtube'],#, 'facebook', 'twitter', 'linkedin'],
            'include_words': ['contact', 'sales', 'services' 'about','email', 'mail', 'support', 'info'],
            'language': 'en'
        }
    }
    
    try:
        logger.info("Starting sequential country-based email extraction...")
        logger.info(f"Countries to process: {country_codes}")
        logger.info(f"Keywords per country: {keywords}")
        
        results = spider.crawl(keywords, country_codes, search_config)
        
        # Export results
        spider.db_manager.export_to_csv("extracted_emails.csv")
        
        logger.info(f"Extraction complete! Found {len(results)} total email results")
        
    except KeyboardInterrupt:
        logger.info("Extraction stopped by user")
    except Exception as e:
        logger.error(f"Extraction failed: {e}")

def main_chinese():
    """Chinese market extraction"""
    spider = EmailSpider(max_workers=2)
    
    # Chinese keywords and configuration
    keywords = ["黄金交易", "投资服务", "矿业公司", "金融顾问"]
    country_codes = [".cn", ".com.cn"]
    
    search_config = {
        'max_urls_per_keyword': 20,
        'operators': {
            'exclude_words': ['baike', 'zhihu', 'weibo'],
            'language': 'zh'
        }
    }
    
    try:
        logger.info("Starting Chinese email extraction...")
        results = spider.crawl(keywords, country_codes, search_config)
        
        spider.db_manager.export_to_csv("chinese_extracted_emails.csv")
        logger.info(f"Chinese extraction complete! Found {len(results)} results")
        
    except Exception as e:
        logger.error(f"Chinese extraction failed: {e}")

if __name__ == "__main__":
    # Run standard extraction
    main()
    
    # Uncomment to run Chinese extraction
    # main_chinese()