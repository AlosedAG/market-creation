from typing import TYPE_CHECKING, List, Dict
import json

if TYPE_CHECKING:
    from utils.llm_handler import LLMEngine

class LandscapeCreator:
    def __init__(self, llm: 'LLMEngine'):
        """
        Initialize the Landscape Creator with an LLM engine.
        
        Args:
            llm: An instance of LLMEngine for market analysis
        """
        self.llm = llm

    def build_taxonomy(self, topic: str) -> dict:
        """
        Generate a market taxonomy for the given topic.
        
        Args:
            topic: The market topic to analyze (e.g., "Chatbots")
            
        Returns:
            Dictionary with market structure including divisions and features
        """
        return self.llm.analyze_market(topic)

    def find_competitors(self, topic: str, divisions: List[str]) -> List[Dict]:
        """
        Use Gemini's built-in Google Search to find current market players.
        
        Args:
            topic: The market topic
            divisions: List of market divisions/channels
            
        Returns:
            List of competitor dictionaries with company info
        """
        query = f"""
        Search for the top {topic} companies and products in these categories: {', '.join(divisions)}.
        
        For each company/product you find, return a JSON array with this structure:
        [
          {{
            "company_name": "Company Name",
            "product_name": "Product Name",
            "official_website_url": "https://example.com",
            "description": "Brief description"
          }}
        ]
        
        Find 5-10 major players in this market. Use Google Search to find current, real companies.
        """
        
        try:
            result = self.llm.search_and_analyze(query)
            return result
        except Exception as e:
            print(f"Search failed: {e}")
            print("Try using manual research or wait for quota reset")
            return []