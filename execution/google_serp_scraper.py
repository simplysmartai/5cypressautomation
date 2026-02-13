import os
import csv
from apify_client import ApifyClient

# Inputs: keywords, number of results/pages, location/language, client identifier
# Outputs: CSV with SERP data

APIFY_TOKEN = os.getenv('APIFY_TOKEN')

client = ApifyClient(APIFY_TOKEN)

def scrape_google_serp(keywords, max_pages=1, client_id=None):
    run_input = {
        'queries': keywords,
        'maxPages': max_pages,
    }
    run = client.actor('apify/google-search-scraper').call(run_input=run_input)
    items = run['items']
    filename = f'google_serp_{client_id or "default"}.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=items[0].keys())
        writer.writeheader()
        writer.writerows(items)
    print(f'Scraped {len(items)} SERP results. Results saved to {filename}')

if __name__ == '__main__':
    # Example usage
    scrape_google_serp(['best wireless headphones'], max_pages=1, client_id='demo')
