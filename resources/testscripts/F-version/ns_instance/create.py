import json
import httplib2

from testscripts.const import MSB_BASE_URL, GLOBAL_CUSTOMER_Id, SERVICE_TYPE, CSAR_ID, NS_NAME, DESCRIPTION

data = {
    "context": {
        "globalCustomerId": GLOBAL_CUSTOMER_Id,
        "serviceType": SERVICE_TYPE
    },
    "csarId": CSAR_ID,
    "nsName": NS_NAME,
    "description": DESCRIPTION
}

full_url = MSB_BASE_URL + '/api/nslcm/v1/ns'
headers = {'content-type': 'application/json', 'accept': 'application/json'}
ca_certs = None
auth_type = "rest_no_auth"
http = httplib2.Http(ca_certs=ca_certs, disable_ssl_certificate_validation=(auth_type == "rest_no_auth"))
http.follow_all_redirects = True
resp, resp_content = http.request(full_url, method="POST", body=json.dumps(data), headers=headers)
headers = {'content-type': 'application/json', 'accept': 'application/json'}
print(resp['status'], resp_content)
