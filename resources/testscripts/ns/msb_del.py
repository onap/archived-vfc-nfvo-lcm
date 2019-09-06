import requests
import sys
create_id = sys.argv[1]

resp = requests.delete('http://10.12.5.131:30280/api/nsd/v1/ns_descriptors/'+create_id)
print(resp.status_code)