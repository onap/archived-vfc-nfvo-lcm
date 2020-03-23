import requests
import sys
from testscripts.const import MSB_BASE_URL, NS_CSAR_PATH

requests.packages.urllib3.disable_warnings()
url = MSB_BASE_URL + '/api/nsd/v1/ns_descriptors/5dc2bd9c-74d7-4e81-9b15-c09d726aaaa1/nsd_content'
resp = requests.put(url, files={'file': open(NS_CSAR_PATH, 'rb')}, verify=False)
print(resp.status_code)
