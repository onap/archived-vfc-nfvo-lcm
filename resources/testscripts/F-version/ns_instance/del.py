import requests
import sys

from testscripts.const import MSB_BASE_URL

requests.packages.urllib3.disable_warnings()

resp = requests.delete(MSB_BASE_URL + '/api/nslcm/v1/ns/5a65cb1b-4766-4cf0-8571-f210a1811f78', verify=False)
print(resp.status_code)
