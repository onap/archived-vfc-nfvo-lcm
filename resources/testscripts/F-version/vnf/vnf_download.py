import requests
import sys

requests.packages.urllib3.disable_warnings()
id =sys.argv[1]
url = 'https://192.168.235.89:30283/api/vnfpkgm/v1/vnf_packages/' +id +' /package_content'
resp = requests.get(url, verify=False)
local_file = open(r'./name.csar', 'wb')
local_file.write(resp.content)
local_file.close()
