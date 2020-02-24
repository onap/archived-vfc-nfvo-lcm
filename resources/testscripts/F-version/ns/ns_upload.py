import requests
import sys
from testscripts.const import MSB_BASE_URL, NS_CSAR_PATH

id = sys.argv[1]

requests.packages.urllib3.disable_warnings()
url = MSB_BASE_URL + '/api/nsd/v1/ns_descriptors/ + id /nsd_content'
resp = requests.put(url, files={'file': open(NS_CSAR_PATH, 'rb')}, verify=False)
print(resp.status_code)
