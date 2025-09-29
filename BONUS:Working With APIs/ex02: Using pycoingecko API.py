import requests

# Get Bitcoin price from CoinGecko API
response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
data = response.json()

# Display the Bitcoin price
btc_price = data['bitcoin']['usd']
print(f"Bitcoin Price: ${btc_price:,.2f} USD")