from typing import TYPE_CHECKING, List
import json
import requests
from bs4 import BeautifulSoup
import logging

if TYPE_CHECKING:
    from core.llm_handler import LLMEngine

logging.basicConfig(level=logging.INFO)

class LandscapeUpdater:
    def __init__(self, llm: 'LLMEngine'):
        """
        Initialize the Landscape Updater with an LLM engine.
        
        Args:
            llm: An instance of LLMEngine for analyzing web content
        """
        self.llm = llm

    def scrape_website(self, url: str) -> str:
        """
        Scrape content from a website URL.
        
        Args:
            url: The website URL to scrape
            
        Returns:
            Extracted text content from the website
        """
        try:
            logging.info(f"Fetching content from: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            logging.info(f"✓ Successfully scraped {len(text)} characters")
            return text
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to scrape {url}: {e}")
            raise Exception(f"Could not access website: {e}")
        except Exception as e:
            logging.error(f"Error parsing website: {e}")
            raise

def update_company(self, url: str, features_to_check: List[str]) -> dict:
        raw_text = self.scrape_website(url)
        
        # Reduced from 15,000 to 8,000 to save "Tokens Per Minute" (TPM)
        max_chars = 8000 
        if len(raw_text) > max_chars:
            logging.info(f"Truncating content to {max_chars} to save TPM quota")
            raw_text = raw_text[:max_chars]
        
        logging.info("Analyzing content with LLM...")
        product_data = self.llm.extract_product_data(raw_text, features_to_check)
        return product_data