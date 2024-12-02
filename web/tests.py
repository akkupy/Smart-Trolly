import requests

# Define the URL for the add_to_cart endpoint
url = 'http://127.0.0.1:8001/add_to_cart/'

# Define the data to send in the POST request
data = {
    'product_name': 'Yippe',
    'price': '14',
    'quantity': '1',
}

# Send a POST request to the server
response = requests.post(url, data=data)

# Check the response
if response.status_code == 200:
    print("Item added to cart:", response.json())
else:
    print("Error:", response.status_code, response.text)
