import requests

# Get a random quote from Zen Quotes API
response = requests.get("https://zenquotes.io/api/random")
quote_data = response.json()[0]

# Display the quote
print(f"\"{quote_data['q']}\"")
print(f"- {quote_data['a']}")