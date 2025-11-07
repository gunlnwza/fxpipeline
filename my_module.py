# my_module.py
import requests

def fetch_data():
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()