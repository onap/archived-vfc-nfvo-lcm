import json
import httplib2

data = {
    "context": {
        "globalCustomerId": "global-customer-id-test1",
        "serviceType": "service-type-test1"
    },
    "csarId": "d5d678dc-80ef-461e-8630-d105f43b0a18",
    "nsName": "ns_vsn",
    "description": "description"
}

full_url = 'https://192.168.235.89:30283/api/nslcm/v1/ns'
headers = {'content-type': 'application/json', 'accept': 'application/json'}
ca_certs = None
auth_type = "rest_no_auth"
http = httplib2.Http(ca_certs=ca_certs, disable_ssl_certificate_validation=(auth_type == "rest_no_auth"))
http.follow_all_redirects = True
resp, resp_content = http.request(full_url, method="POST", body=json.dumps(data), headers=headers)
headers = {'content-type': 'application/json', 'accept': 'application/json'}
print(resp['status'], resp_content)
