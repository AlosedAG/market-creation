import os
import logging
import time
from google import genai
from google.genai import types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- RATE LIMITING CONFIGURATION ---
# Track the timestamp of the last API call globally
_last_api_call = 0

# Set to 6.0 seconds to stay safely under the 10-15 RPM (Requests Per Minute) limit
_min_delay_seconds = 6.0 

def rate_limit():
    """
    Throttles execution to ensure a minimum delay between API calls.
    Call this function immediately before any client.models.generate_content call.
    """
    global _last_api_call
    current_time = time.time()
    time_since_last = current_time - _last_api_call
    
    if time_since_last < _min_delay_seconds:
        sleep_time = _min_delay_seconds - time_since_last
        logging.info(f"Rate limiting: Cooling down for {sleep_time:.1f}s to protect quota...")
        time.sleep(sleep_time)
    
    # Update the timestamp AFTER the sleep
    _last_api_call = time.time()

def setup_api_key():
    """
    Retrieves the API key from environment variables or user input.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        api_key = input("\nPaste your Gemini API key: ").strip()
        if not api_key:
            logging.error("No API key provided")
            raise ValueError("API key is required")  
        os.environ['GEMINI_API_KEY'] = api_key
    
    logging.info("API key configured successfully")
    return api_key

def get_working_model():
    """
    Initializes the Gemini client and allows the user to select a model.
    Skips the 'list_models' call to save initial quota.
    """
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            api_key = setup_api_key()
            
        client = genai.Client(api_key=api_key)
        
        default_models = [
            'gemini-2.5-flash-lite',       # Best for Quota/Rate limits
            'gemini-3-flash-preview',      # Latest and greatest
            'gemini-2.5-flash',            # Standard performance
            'gemini-2.0-flash-lite',       # Older lite version,
        ]
        
        print("\n" + "="*70)
        print("QUOTA-SAFE MODE: Model Selection")
        print("="*70)
        print("Using these models directly skips discovery calls to save quota.")
        print("\nAvailable options:")
        for i, model in enumerate(default_models, 1):
            print(f"  {i}. {model}")
        print("="*70)
        
        # User selection logic
        while True:
            try:
                choice = input(f"\nSelect model (1-{len(default_models)}) or Enter for default [1]: ").strip()
                
                if choice == "":
                    choice = 1
                else:
                    choice = int(choice)
                
                if 1 <= choice <= len(default_models):
                    break
                else:
                    print(f"Please enter a number between 1 and {len(default_models)}")
            except ValueError:
                print("Please enter a valid number")
        
        selected_name = default_models[choice - 1]
        
        # The SDK expects just the model name string or 'models/name'
        model_name = selected_name
        
        logging.info(f"✓ Selected: {selected_name}")
        logging.info(f"  Throttling enabled: {_min_delay_seconds}s interval between calls")
        
        return client, model_name
        
    except Exception as e:
        if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
            print("\n" + "="*70)
            print("  QUOTA LIMIT REACHED")
            print("="*70)
            print("You've exceeded your free tier quota. Options:")
            print("1. Wait 60 seconds (Free tier resets every minute).")
            print("2. Upgrade to Pay-as-you-go in AI Studio.")
            print(f"3. Current hard limit: ~10-15 Requests Per Minute.")
            print("="*70)
            
        raise Exception(f"Could not initialize Gemini Client: {e}")