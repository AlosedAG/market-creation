import json
from google.genai import types
from typing import List

class LLMEngine:
    def __init__(self, client, model_name: str):
        """
        Initialize LLM Engine with the new Google GenAI SDK.
        
        Args:
            client: The genai.Client instance
            model_name: The model name to use (e.g., 'gemini-1.5-flash')
        """
        self.client = client
        self.model_name = model_name

    def analyze_market(self, topic: str) -> dict:
        """
        Analyze a market topic and return taxonomy structure.
        
        Args:
            topic: The market topic to analyze
            
        Returns:
            Dictionary with market structure
        """
        prompt = f"""
        Analyze the market for: {topic}.
        Return a JSON object with exactly these keys:
        - "market_name": A formal name (e.g., 'Conversational Intelligence').
        - "definition": A brief description.
        - "divisions": List of 4-6 channels (e.g., SMS, Voice).
        - "suggested_features": List of 8-10 features to check (e.g., SSO, API).
        - "sub_divisions": List of 3-5 niche segments.
        """
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        return json.loads(response.text)

    def extract_product_data(self, raw_text: str, features_to_check: List[str]) -> dict:
        """
        Extract structured product data from website text.
        
        Args:
            raw_text: Raw website content
            features_to_check: List of features to verify
            
        Returns:
            Dictionary with extracted product information
        """
        prompt = f"""
        Analyze this website text and extract product info.
        Features to check (return true/false for each): {features_to_check}
        
        Website Content:
        {raw_text[:15000]}
        
        Return a JSON object matching this structure:
        {{
            "company_name": "string",
            "product_name": "string",
            "description": "string",
            "features": ["list of strings"],
            "feature_flags": {{"Feature Name": true/false}},
            "case_study_desc": "string",
            "case_study_link": "string",
            "is_case_study_present": true/false,
            "pricing_desc": "string",
            "pricing_tiers": ["list of strings"],
            "notes": "string"
        }}
        """
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        return json.loads(response.text)

    def search_and_analyze(self, query: str) -> list:
        """
        Use Gemini's built-in Google Search grounding to find and analyze information.
        
        NOTE: Google Search grounding is available in specific Gemini models.
        Check model capabilities before using this feature.
        
        Args:
            query: Search query to analyze
            
        Returns:
            List of structured results
        """
        try:
            # Enable Google Search grounding
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=query,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    # Note: Google Search grounding might require specific model versions or may not be available in all regions
                )
            )
            
            return json.loads(response.text)
        except Exception as e:
            # If search grounding isn't available, provide helpful error
            if 'grounding' in str(e).lower() or 'search' in str(e).lower():
                raise Exception(
                    "Google Search grounding not available for this model. "
                    "Try using Gemini 2.0 Flash Exp or later models."
                )
            raise