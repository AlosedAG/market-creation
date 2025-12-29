import os
import logging
import csv
from core.config import setup_api_key, get_working_model
from core.creator import LandscapeCreator
from core.updater import LandscapeUpdater
from core.llm_handler import LLMEngine

def main():
    # Setup Gemini API
    setup_api_key()
    client, model_name = get_working_model()
    
    # Initialize Engine
    llm = LLMEngine(client, model_name)
    creator = LandscapeCreator(llm)
    updater = LandscapeUpdater(llm)

    print("\n" + "="*50)
    print("GEMINI MARKET RESEARCH TOOL")
    print("="*50)
    print("1. Create New Landscape (Taxonomy + Discovery)")
    print("2. Update Existing Landscape (Scrape Website)")
    print("="*50)
    
    choice = input("Select option: ").strip()

    if choice == "1":
        topic = input("\nEnter market topic (e.g., Chatbots, ERP solutions): ").strip()
        
        print(f"\n[*] Analyzing market: {topic}...")
        
        # Get Taxonomy
        try:
            tax = creator.build_taxonomy(topic)
        except Exception as e:
            if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
                print("\n Quota exceeded!")
                return
            raise
        
        print(f"\n{'='*50}")
        print("MARKET TAXONOMY")
        print("="*50)
        print(f"Name: {tax['market_name']}")
        print(f"Definition: {tax['definition']}")
        print(f"\nDivisions: {', '.join(tax['divisions'])}")
        print(f"\nSuggested Features: {', '.join(tax['suggested_features'])}")
        print(f"\nSub-divisions: {', '.join(tax['sub_divisions'])}")
        print("="*50)
        
        # Search for Players
        do_search = input("\nSearch for current players/links? (y/n): ").strip().lower()
        if do_search == 'y':
            players = creator.find_competitors(topic, tax['divisions'])
            if players:
                print(f"\n✓ Found {len(players)} Potential Players:")
                for p in players:
                    print(f"  - {p['company_name']} ({p['product_name']}): {p['official_website_url']}")
                
                # CSV Export for Choice 1
                filename = f"{topic.replace(' ', '_').lower()}_competitors.csv"
                keys = ["company_name", "product_name", "official_website_url", "description"]
                
                try:
                    with open(filename, "w", newline="", encoding="utf-8") as output_file:
                        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                        dict_writer.writeheader()
                        dict_writer.writerows(players)
                    print(f"\n[✔] Data saved to {filename}")
                except Exception as csv_err:
                    print(f"\n[!] Error saving CSV: {csv_err}")
                
            else:
                print("\n[!] No competitors found.")

    elif choice == "2":
        url = input("\nEnter company product URL: ").strip()
        
        # Example features to check
        features = ["Mobile App", "API access", "SSO", "Analytics Dashboard", "Webhooks"]
        
        print(f"\n[*] Analyzing page content from {url}...")
        try:
            result = updater.update_company(url, features)
        except Exception as e:
            if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
                print("\nQuota exceeded!")
                return
            raise
        
        print("\n" + "="*50)
        print("EXTRACTED MARKET DATA")
        print("="*50)
        print(f"Company: {result.get('company_name', 'N/A')}")
        print(f"Product: {result.get('product_name', 'N/A')}")
        print(f"Description: {result.get('description', 'N/A')}")
        print(f"\nFeatures: {', '.join(result.get('features', []))}")
        print(f"\nFeature Flags:")
        for feature, present in result.get('feature_flags', {}).items():
            status = "✓" if present else "✗"
            print(f"  {status} {feature}")
        print(f"\nPricing: {result.get('pricing_desc', 'N/A')}")
        print(f"Tiers: {', '.join(result.get('pricing_tiers', []))}")
        print(f"\nNotes: {result.get('notes', 'N/A')}")
        print("="*50)

        # CSV Export for Choice 2
        comp_name = result.get('company_name', 'extracted_company').replace(' ', '_').lower()
        filename = f"{comp_name}_analysis.csv"
        
        try:
            # Flatten lists/dicts so they fit into single CSV cells
            csv_data = result.copy()
            if 'features' in csv_data:
                csv_data['features'] = "; ".join(csv_data['features'])
            if 'pricing_tiers' in csv_data:
                csv_data['pricing_tiers'] = "; ".join(csv_data['pricing_tiers'])
            if 'feature_flags' in csv_data:
                # Convert dict to string "Feature1: True; Feature2: False"
                csv_data['feature_flags'] = "; ".join([f"{k}: {v}" for k, v in csv_data['feature_flags'].items()])
            
            keys = csv_data.keys()
            with open(filename, "w", newline="", encoding="utf-8") as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerow(csv_data)
            print(f"\n[✔] Scraped data saved to {filename}")
        except Exception as csv_err:
            print(f"\n[!] Error saving CSV: {csv_err}")
    
    else:
        print("\n[!] Invalid option selected")

if __name__ == "__main__":
    main()