import requests
import sys

from testscripts.const import MSB_IP

id = sys.argv[1]

requests.packages.urllib3.disable_warnings()
resp = requests.get(MSB_IP + '/api/vnfpkgm/v1/vnf_packages/' + id, verify=False)
print(resp.status_code, resp.json())
