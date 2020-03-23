import json
import httplib2

from testscripts.const import MSB_BASE_URL

data = {
    "additionalParamForNs": {
        "sdnControllerId": "2"
    },
    "locationConstraints": [{
        "vnfProfileId": "706281ad-e8dd-4935-955d-1ee815361e50",
        "locationConstraints": {
            "vimId": "ovp_RegionOne"
        }
    },
    {
        "vnfProfileId": "877e079a-3fdf-4c14-987d-e1f1f1a19f57",
        "locationConstraints": {
            "vimId": "ovp_RegionOne"
        }
    },
    {
        "vnfProfileId": "5bf43799-207a-48f0-94b8-13006cce6a7b",
        "locationConstraints": {
            "vimId": "ovp_RegionOne"
        }
    }]
}

headers = {'content-type': 'application/json', 'accept': 'application/json'}
ca_certs = None
auth_type = "rest_no_auth"
http = httplib2.Http(ca_certs=ca_certs, disable_ssl_certificate_validation=(auth_type == "rest_no_auth"))
http.follow_all_redirects = True
resp, resp_content = http.request(MSB_BASE_URL + '/api/nslcm/v1/ns/17d76476-747e-47b3-9580-314376000252/instantiate',
                                  method="POST", body=json.dumps(data), headers=headers)
print(resp['status'], resp_content)
