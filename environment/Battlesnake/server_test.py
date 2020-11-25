import requests
import json

with open('tests/data/request_1.json') as json_file:
    data = json.load(json_file)

r = requests.post('http://0.0.0.0:8080/move', json=data)
print(r)

