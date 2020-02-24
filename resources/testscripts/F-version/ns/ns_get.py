import requests

from testscripts.const import MSB_BASE_URL

requests.packages.urllib3.disable_warnings()
resp = requests.get(MSB_BASE_URL + '/api/nsd/v1/ns_descriptors', verify=False)
print(resp.status_code, resp.json())
