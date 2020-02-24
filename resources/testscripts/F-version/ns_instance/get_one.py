import requests
import sys

from testscripts.const import MSB_BASE_URL

id = sys.argv[1]
requests.packages.urllib3.disable_warnings()
resp = requests.get(MSB_BASE_URL + '/api/nslcm/v1/ns/' + id, verify=False)
print(resp.status_code, resp.json())
