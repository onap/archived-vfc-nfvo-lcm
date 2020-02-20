import requests
import sys

requests.packages.urllib3.disable_warnings()
jobId = '1'
if len(sys.argv) > 1:
    jobId = sys.argv[1]
resp = requests.get('https://192.168.235.89:30283/api/nslcm/v1/jobs/%s' % jobId, verify=False)
print(resp.status_code, resp.json())
