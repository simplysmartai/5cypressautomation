#!/usr/bin/env python3
import os
import csv
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def get_perplexity_leads(niche_label, city):
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("Error: PERPLEXITY_API_KEY not found in .env")
        return []

    url = "https://api.perplexity.ai/chat/completions"
    
    prompt = f"""
    Find 20 local {niche_label} businesses in {city}, GA. 
    For each business, I need:
    1. Business Name
    2. Website URL
    3. Phone Number
    4. Physical Address
    
    Return the data as a clean JSON list of objects with keys: name, website, phone, address.
    Do not include any other text in the response, just the JSON array.
    """

    payload = {
        "model": "sonar", 
        "messages": [
            {"role": "system", "content": "You are a lead generation specialist. Return only JSON."},
            {"role": "user", "content": prompt}
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        
        # Clean up the response content in case there's markdown triple backticks
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        return json.loads(content)
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return []

def save_to_csv(leads, niche_id):
    if not leads:
        return
    
    filename = f".tmp/leads_{niche_id}.csv"
    os.makedirs(".tmp", exist_ok=True)
    
    keys = leads[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(leads)
    
    print(f"Successfully saved {len(leads)} leads to {filename}")

if __name__ == "__main__":
    niche_label = "Med Spa"
    niche_id = "med_spa"
    city = "Alpharetta"
    
    print(f"Generating leads for {niche_label} in {city}...")
    leads = get_perplexity_leads(niche_label, city)
    if leads:
        save_to_csv(leads, niche_id)
    else:
        print("No leads found.")
