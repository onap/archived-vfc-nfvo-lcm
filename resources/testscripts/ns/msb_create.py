import json
import httplib2
ud_data = {'userDefinedData': {"key1": "value1"}}
headers = {'content-type': 'application/json', 'accept': 'application/json'}
http = httplib2.Http()
resp, resp_content = http.request('http://172.30.3.104:30280/api/nsd/v1/ns_descriptors',
                                  method="POST",
                                  body=json.dumps(ud_data),
                                  headers=headers)
print(resp['status'], resp_content)
