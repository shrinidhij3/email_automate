import requests

# Test the unread_emails endpoint
url = 'http://localhost:8000/api/unread-emails/'
print(f"Testing URL: {url}")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(response.json() if response.status_code == 200 else response.text)
except Exception as e:
    print(f"Error: {e}")
