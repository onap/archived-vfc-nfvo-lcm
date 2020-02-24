import requests

from testscripts.const import MSB_BASE_URL

requests.packages.urllib3.disable_warnings()
resp = requests.get(MSB_BASE_URL + '/api/vnfpkgm/v1/vnf_packages', verify=False)
print(resp.status_code, resp.json())
