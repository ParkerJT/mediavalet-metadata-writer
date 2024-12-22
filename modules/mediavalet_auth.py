import requests
from base64 import b64encode
import pwinput

# Replace with your client_id and client_secret from MediaValet
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"

def get_access_token():
    # Define the endpoint and headers
    token_url = "https://login.mediavalet.com/connect/token"

    # Get username and password as input
    username = str(input("Enter MediaValet Username: "))
    password = str(pwinput.pwinput("Enter MediaValet Password: ", mask="*"))
    
    # Create the Basic Auth header value
    auth_header_value = b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header_value}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Define the payload
    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "api"
    }

    # Make the POST request
    response = requests.post(token_url, headers=headers, data=payload)

    # Check for errors and return the token
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None