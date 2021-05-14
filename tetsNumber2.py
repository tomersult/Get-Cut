import requests
import json

BASE = "http://192.168.1.14:5000/oriel"

response = requests.get(BASE)
print(response)
