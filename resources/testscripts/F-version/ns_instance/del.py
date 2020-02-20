import requests
import sys

id = sys.argv[1]
resp = requests.delete('https://192.168.235.89:30283/api/nslcm/v1/ns/' + id, verify=False)
print(resp.status_code)
