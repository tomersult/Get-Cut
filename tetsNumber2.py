import requests
import json

BASE = "http://127.0.0.1:5000/"

response = requests.post(BASE, data={"userName": "oriel",
                                     "password": "04030403", })
print(response)
