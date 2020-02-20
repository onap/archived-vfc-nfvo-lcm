import json
import httplib2

full_url = 'https://192.168.235.89:30283/api/nsd/v1/ns_descriptors'
ud_data = {'userDefinedData': {"key2": "value2"}}
headers = {'content-type': 'application/json', 'accept': 'application/json'}
ca_certs = None
auth_type = "rest_no_auth"
http = httplib2.Http(ca_certs=ca_certs, disable_ssl_certificate_validation=(auth_type == "rest_no_auth"))
http.follow_all_redirects = True
resp, resp_content = http.request(full_url, method="POST", body=json.dumps(ud_data), headers=headers)
resp_status, resp_body = resp['status'], resp_content
print(resp_status, resp_body)
