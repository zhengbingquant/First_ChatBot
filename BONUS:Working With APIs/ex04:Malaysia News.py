import requests

# Your News API key
api_key = "2e0ebb19013d4e06bc4eaa5cd8d9d465"

# Get latest news about Malaysia
url = f"https://newsapi.org/v2/everything?q=Malaysia&sortBy=publishedAt&apiKey={api_key}"
response = requests.get(url)
data = response.json()

# Display the latest news articles
if data['status'] == 'ok':
    articles = data['articles'][:5]  # Get top 5 articles
    
    print("=" * 60)
    print("LATEST NEWS ABOUT MALAYSIA")
    print("=" * 60)
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']['name']}")
        print(f"   Published: {article['publishedAt']}")
        print(f"   URL: {article['url']}")
        if article['description']:
            print(f"   Description: {article['description']}")
else:
    print("Error fetching news:", data.get('message', 'Unknown error'))