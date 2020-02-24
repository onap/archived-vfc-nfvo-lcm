import requests
import sys

from testscripts.const import MSB_BASE_URL, VNF_CSAR_PATH

requests.packages.urllib3.disable_warnings()
id = sys.argv[1]
url = MSB_BASE_URL + '/api/vnfpkgm/v1/vnf_packages/' + id + '/package_content'
resp = requests.get(url, verify=False)
local_file = open(VNF_CSAR_PATH, 'wb')
local_file.write(resp.content)
local_file.close()
