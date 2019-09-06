import requests
resp = requests.get('http://10.12.5.131:30280/api/nsd/v1/ns_descriptors')
print(resp.status_code, resp.json())
