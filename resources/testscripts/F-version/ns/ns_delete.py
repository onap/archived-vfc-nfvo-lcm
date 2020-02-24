import requests
import sys

from testscripts.const import MSB_BASE_URL

id = sys.argv[1]

requests.packages.urllib3.disable_warnings()
resp = requests.delete(MSB_BASE_URL + '/api/nsd/v1/ns_descriptors/' + id, verify=False)
print(resp.status_code)
