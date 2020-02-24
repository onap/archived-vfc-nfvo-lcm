import requests
import sys

from testscripts.const import MSB_BASE_URL

requests.packages.urllib3.disable_warnings()
id = sys.argv[1]
resp = requests.delete(MSB_BASE_URL + '/api/nslcm/v1/ns/' + id, verify=False)
print(resp.status_code)
