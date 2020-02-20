import requests
import sys

id = sys.argv[1]

requests.packages.urllib3.disable_warnings()
resp = requests.delete('https://192.168.235.89:30283/api/vnfpkgm/v1/vnf_packages/' + id, verify=False)
print(resp.status_code)
