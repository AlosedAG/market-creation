import json
import time
import logging
import re
from typing import List, Dict, Any
from google.genai import types
from core.config import rate_limit

class LLMEngine:
    def __init__(self, client, model_name: str):
        self.client = client
        self.model_name = model_name

    def _safe_generate(self, prompt: str, config: types.GenerateContentConfig):
        """
        Infinite Patience logic: waits for quota resets and handles server busy errors.
        """
        max_attempts = 15 
        
        for attempt in range(1, max_attempts + 1):
            try:
                rate_limit()
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                return response
            
            except Exception as e:
                err_msg = str(e).upper()
                
                # Handle Quota (429) or Server Overload (503)
                if any(x in err_msg for x in ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "OVERLOADED"]):
                    wait_time = 65 
                    logging.warning(f"\n[!] Limit hit. Waiting {wait_time}s for reset... (Attempt {attempt}/{max_attempts})")
                    time.sleep(wait_time)
                    continue
                else:
                    # If it's a 400 or other fatal error, raise it immediately
                    raise e
                    
        raise Exception("Max patience reached. Please try again later.")

    def analyze_market(self, topic: str) -> dict:
        prompt = f"Analyze the market for: {topic}. Return JSON with: market_name, definition, divisions, suggested_features, sub_divisions."
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            tools=[], 
            temperature=0.2
        )
        response = self._safe_generate(prompt, config)
        return json.loads(response.text)

    def search_and_analyze(self, query: str) -> list:
        """
        Uses the corrected Google Search tool (google_search).
        """
        logging.info("Initiating Google Search grounding...")
        
        # --- THE FIX IS HERE ---
        # Changed 'google_search_retrieval' to 'google_search'
        search_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        config = types.GenerateContentConfig(
            tools=[search_tool],
            temperature=0.0 
        )

        try:
            response = self._safe_generate(query, config)
            if response and response.text:
                return self._parse_json_from_text(response.text)
            return []
        except Exception as e:
            logging.error(f"Search failed: {e}")
            return []

    def extract_product_data(self, raw_text: str, features_to_check: List[str]) -> dict:
        prompt = f"Analyze: {raw_text[:8000]}. Check features: {features_to_check}."
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            tools=[],
            temperature=0.1
        )
        response = self._safe_generate(prompt, config)
        return json.loads(response.text)

    def _parse_json_from_text(self, text_content: str) -> list:
        """Extracts JSON array even if the model provides conversational context."""
        try:
            # Look for the JSON block [...]
            json_match = re.search(r'\[\s*\{.*\}\s*\]', text_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            # Look for single JSON object {...}
            json_obj_match = re.search(r'\{\s*".*":.*\s*\}', text_content, re.DOTALL)
            if json_obj_match:
                return [json.loads(json_obj_match.group(0))]
        except Exception as e:
            logging.error(f"JSON Parsing failed: {e}")
        return []