import requests

authtoken_url = 'http://127.0.0.1:8000/token'

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = {
    'grant_type': '',
    'username': 'conas',
    'password': 'desabao',
    'scope': '',
    'client_id': '',
    'client_secret': '',
}

response = requests.post(authtoken_url, headers=headers, data=data)

print(response.text)