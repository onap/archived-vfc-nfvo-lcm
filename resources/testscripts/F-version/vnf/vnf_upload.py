import requests
import sys

from testscripts.const import MSB_BASE_URL, VNF_CSAR_PATH


requests.packages.urllib3.disable_warnings()
url = MSB_BASE_URL + '/api/vnfpkgm/v1/vnf_packages/2d1fe0ed-f05f-4b85-a7d6-86ddfb7018b5/package_content'
resp = requests.put(url, files={'file': open(VNF_CSAR_PATH, 'rb')}, verify=False)
print(resp.status_code)
