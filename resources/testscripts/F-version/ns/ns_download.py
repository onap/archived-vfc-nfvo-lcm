import requests
import sys

from testscripts.const import MSB_IP, NS_CSAR_PATH

id = sys.argv[1]
url = MSB_IP + '/api/nsd/v1/ns_descriptors/' + id + '/nsd_content'
resp = requests.get(url)
local_file = open(NS_CSAR_PATH, 'wb')
local_file.write(resp.content)
local_file.close()
