import os
import csv
from apify_client import ApifyClient

# Inputs: keywords or product URLs, number of products, client identifier
# Outputs: CSV with product data

APIFY_TOKEN = os.getenv('APIFY_TOKEN')

client = ApifyClient(APIFY_TOKEN)

def scrape_amazon_products(keywords, max_products=20, client_id=None):
    run_input = {
        'search': keywords,
        'maxResults': max_products,
    }
    run = client.actor('apify/amazon-product-scraper').call(run_input=run_input)
    items = run['items']
    filename = f'amazon_products_{client_id or "default"}.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=items[0].keys())
        writer.writeheader()
        writer.writerows(items)
    print(f'Scraped {len(items)} products. Results saved to {filename}')

if __name__ == '__main__':
    # Example usage
    scrape_amazon_products(['wireless headphones'], max_products=10, client_id='demo')
