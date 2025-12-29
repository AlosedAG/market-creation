import os
from google import genai

def list_my_models():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        api_key = input("Paste your Gemini API key: ").strip()
    
    client = genai.Client(api_key=api_key)
    
    print("\n" + "="*60)
    print(f"{'AVAILABLE MODELS':^60}")
    print("="*60)
    print(f"{'Model Name':<40} | {'Supported Actions'}")
    print("-"*60)
    
    try:
        # The new SDK uses client.models.list()
        for model in client.models.list():
            # Filter for models that support generating content
            if 'generateContent' in model.supported_actions:
                print(f"{model.name:<40} | Supported")
    except Exception as e:
        print(f"Error listing models: {e}")
    
    print("="*60)

if __name__ == "__main__":
    list_my_models()