import requests
import sys

id = sys.argv[1]

requests.packages.urllib3.disable_warnings()
url = 'https://192.168.235.89:30283/api/vnfpkgm/v1/vnf_packages/' + id + '/package_content'
resp = requests.put(url, files={'file': open(r"C:\Users\86187\Desktop\vfc-tests\vgw.csar", 'rb')}, verify=False)
print(resp.status_code)