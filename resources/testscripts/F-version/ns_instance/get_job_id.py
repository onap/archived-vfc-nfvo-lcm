import requests
import sys

from testscripts.const import MSB_BASE_URL

requests.packages.urllib3.disable_warnings()
jobId = '1'
if len(sys.argv) > 1:
    jobId = sys.argv[1]
resp = requests.get(MSB_BASE_URL + '/api/nslcm/v1/jobs/%s' % jobId, verify=False)
print(resp.status_code, resp.json())
