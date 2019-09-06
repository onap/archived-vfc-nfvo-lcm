import requests
import sys
create_id = sys.argv[1]

url = 'http://10.12.5.131:30280/api/nsd/v1/ns_descriptors/' + create_id + '/nsd_content'
resp = requests.put(url, files={'file': open(r"/home/ubuntu/test/test/ns/ns_vgw.csar", 'rb')})
print(resp.status_code)
