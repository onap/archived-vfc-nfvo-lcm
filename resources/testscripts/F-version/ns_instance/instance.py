import json
import httplib2
import sys
ns_instance_Id = sys.argv[1]
data = {
    "additionalParamForNs": {
        "sdnControllerId": "2"
    },
    "locationConstraints": [{
        "vnfProfileId": "45711f40-3f43-415b-bb45-46e5c6940735",
        "locationConstraints": {
            "vimId": "CPE-DC_RegionOne"
        }
    }]
}
headers = {'content-type': 'application/json', 'accept': 'application/json'}
ca_certs = None
auth_type = "rest_no_auth"
http = httplib2.Http(ca_certs=ca_certs, disable_ssl_certificate_validation=(auth_type == "rest_no_auth"))
http.follow_all_redirects = True
resp, resp_content = http.request('https://192.168.235.89:30283/api/nslcm/v1/ns/' + ns_instance_Id + '/instantiate',
                                  method="POST", body=json.dumps(data), headers=headers)
print(resp['status'], resp_content)
