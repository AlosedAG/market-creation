import os
from google import genai
from google.genai import types
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_api_key():
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
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        client = genai.Client(api_key=api_key)
        
        logging.info("\n→ Fetching available models from API...")
        
        # Get all available models
        models_response = client.models.list()
        
        # Filter and collect models
        available_models = []
        for model in models_response:
            if hasattr(model, 'name') and 'gemini' in model.name.lower():
                model_name = model.name
                display_name = model_name.replace('models/', '')
                
                # Skip embedding models
                if 'embedding' in display_name.lower():
                    continue
                
                available_models.append({
                    'name': model_name,
                    'display_name': display_name,
                })
        
        if not available_models:
            raise Exception("No Gemini models available")
        
        # Sort: Flash models first, then others
        available_models.sort(key=lambda x: (
            'flash' not in x['display_name'].lower(),
            x['display_name']
        ))
        
        # Display models with quota recommendations
        print("\n" + "="*70)
        print("AVAILABLE GEMINI MODELS")
        print("="*70)
        
        # Group models by tier
        flash_lite = [m for m in available_models if 'flash-lite' in m['display_name'].lower()]
        flash_regular = [m for m in available_models if 'flash' in m['display_name'].lower() and 'lite' not in m['display_name'].lower()]
        pro_models = [m for m in available_models if 'pro' in m['display_name'].lower()]
        other_models = [m for m in available_models if m not in flash_lite + flash_regular + pro_models]
        
        idx = 1
        
        if flash_lite:
            print("\n FLASH LITE (Lowest Cost - Try These First):")
            for model_info in flash_lite:
                print(f"  {idx}. {model_info['display_name']}")
                idx += 1
        
        if flash_regular:
            print("\n FLASH (Good Balance):")
            for model_info in flash_regular:
                print(f"  {idx}. {model_info['display_name']}")
                idx += 1
        
        if pro_models:
            print("\n PRO (More Capable):")
            for model_info in pro_models:
                print(f"  {idx}. {model_info['display_name']}")
                idx += 1
        
        if other_models:
            print("\n OTHER:")
            for model_info in other_models:
                print(f"  {idx}. {model_info['display_name']}")
                idx += 1
        
        print("="*70)
        
        # Get user choice
        while True:
            try:
                hint = "\n💡 TIP: If you hit quota limits, try Flash Lite models (lowest cost)"
                print(hint)
                choice = input(f"\nSelect model (1-{len(available_models)}) or Enter for Flash Lite [1]: ").strip()
                
                if choice == "":
                    choice = 1
                else:
                    choice = int(choice)
                
                if 1 <= choice <= len(available_models):
                    break
                else:
                    print(f"Please enter a number between 1 and {len(available_models)}")
            except ValueError:
                print("Please enter a valid number")
        
        # Get selected model
        selected_model = available_models[choice - 1]
        model_name = selected_model['name']
        
        logging.info(f"\n✓ Selected: {selected_model['display_name']}")
        logging.info("⚠️  Skipping test call to save quota - model will be validated on first use")
        
        return client, model_name
        
    except Exception as e:
        logging.error(f"Failed to fetch models: {e}")
        
        # quota error message
        if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
            print("\n" + "="*70)
            print("⚠️  QUOTA LIMIT REACHED")
            print("="*70)
            print("You've exceeded your free tier quota. Options:")
            print("1. Wait 1 hour and try again (quotas reset hourly)")
            print("2. Try a different model (Flash Lite uses less quota)")
            print("3. Check usage: https://ai.dev/usage?tab=rate-limit")
            print("4. Upgrade: https://ai.google.dev/pricing")
            print("="*70)
            
        raise Exception(
            "Could not initialize model. Please check:\n"
            "1. Your API key is valid\n"
            "2. You haven't exceeded quota limits\n"
            "3. Visit https://aistudio.google.com/apikey to verify"
        )