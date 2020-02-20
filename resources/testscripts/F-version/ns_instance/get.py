import requests

requests.packages.urllib3.disable_warnings()
resp = requests.get('https://192.168.235.89:30283/api/nslcm/v1/ns', verify=False)
print(resp.status_code, resp.json())
