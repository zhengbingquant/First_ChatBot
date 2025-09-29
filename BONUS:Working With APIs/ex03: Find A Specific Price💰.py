import requests

# Ask user for cryptocurrency name
crypto = input("Enter cryptocurrency name (e.g., bitcoin, ethereum, dogecoin): ").lower()

# Get price from CoinGecko API
response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd")
data = response.json()

# Display the price
if crypto in data:
    price = data[crypto]['usd']
    print(f"{crypto.capitalize()} Price: ${price:,.2f} USD")
else:
    print(f"Cryptocurrency '{crypto}' not found. Please check the name and try again.")