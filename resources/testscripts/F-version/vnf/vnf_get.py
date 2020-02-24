import requests

from testscripts.const import MSB_IP

requests.packages.urllib3.disable_warnings()
resp = requests.get(MSB_IP + '/api/vnfpkgm/v1/vnf_packages', verify=False)
print(resp.status_code, resp.json())
