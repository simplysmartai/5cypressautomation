import os
import csv
from apify_client import ApifyClient

# Inputs: usernames, hashtags, queries, number of tweets, date range, client identifier
# Outputs: CSV with tweet data

APIFY_TOKEN = os.getenv('APIFY_TOKEN')

client = ApifyClient(APIFY_TOKEN)

def scrape_twitter(query, max_tweets=100, client_id=None):
    run_input = {
        'query': query,
        'maxTweets': max_tweets,
    }
    run = client.actor('apify/twitter-scraper').call(run_input=run_input)
    items = run['items']
    filename = f'twitter_scrape_{client_id or "default"}.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=items[0].keys())
        writer.writeheader()
        writer.writerows(items)
    print(f'Scraped {len(items)} tweets. Results saved to {filename}')

if __name__ == '__main__':
    # Example usage
    scrape_twitter('#AI', max_tweets=50, client_id='demo')
