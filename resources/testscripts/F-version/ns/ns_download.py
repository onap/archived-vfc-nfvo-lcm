import requests
import sys

id = sys.argv[1]
url = 'https://192.168.235.89:30283/api/nsd/v1/ns_descriptors/' + id + '/nsd_content'
resp = requests.get(url)
local_file = open(r'./name.csar', 'wb')
local_file.write(resp.content)
local_file.close()
