import json
import httplib2
import sys

from testscripts.const import VNF_PROFILE_ID, VIM_ID, MSB_BASE_URL

ns_instance_Id = sys.argv[1]
data = {
    "additionalParamForNs": {
        "sdnControllerId": "2"
    },
    "locationConstraints": [{
        "vnfProfileId": VNF_PROFILE_ID,
        "locationConstraints": {
            "vimId": VIM_ID
        }
    }]
}
headers = {'content-type': 'application/json', 'accept': 'application/json'}
ca_certs = None
auth_type = "rest_no_auth"
http = httplib2.Http(ca_certs=ca_certs, disable_ssl_certificate_validation=(auth_type == "rest_no_auth"))
http.follow_all_redirects = True
resp, resp_content = http.request(MSB_BASE_URL + '/api/nslcm/v1/ns/' + ns_instance_Id + '/instantiate',
                                  method="POST", body=json.dumps(data), headers=headers)
print(resp['status'], resp_content)
